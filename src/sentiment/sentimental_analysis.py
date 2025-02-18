"""
Classify is the sentimental is bullish or bearish
use of NLP, text analysis and computational liguistics
We will use VADER (future -> build our own lexicon)
"""

import pandas as pd
from datetime import date, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src.sentiment.fetch_data import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.sentiment.process import *
from transformers import pipeline
from src.database.sec_files import store_sentiment_results

# https://www.geeksforgeeks.org/python-sentiment-analysis-using-vader/
def analyze_sentiment_vader_news(articles: pd.DataFrame) -> pd.DataFrame:
    """
    Use VADER to compute sentiment scores for each row in the DataFrame.
    Assumes the text to analyze is in the 'content' column.
    Adds sentiment columns ('neg', 'neu', 'pos', 'compound') to the DataFrame,
    and classifies sentiment as 'bullish', 'bearish', or 'neutral' based on the compound score.
    """
    sid_obj = SentimentIntensityAnalyzer()

    # Apply sentiment analysis to the 'content' column after preprocessing
    def get_scores(text):
        text = preprocess_text(text)
        return sid_obj.polarity_scores(text)

    # Get scores as a Series of dictionaries, then expand into a DataFrame
    scores_series = articles['content'].apply(get_scores)
    scores_df = pd.DataFrame(scores_series.tolist())
    articles = pd.concat([articles, scores_df], axis=1)

    return articles

def analyze_sentiment_vader_reddit(articles: pd.DataFrame) -> pd.DataFrame:
    """
    Use VADER to compute sentiment scores for each row in the DataFrame.
    Assumes the text to analyze is in the 'content' column.
    Adds sentiment columns ('neg', 'neu', 'pos', 'compound') to the DataFrame,
    and classifies sentiment as 'bullish', 'bearish', or 'neutral' based on the compound score.
    """
    sid_obj = SentimentIntensityAnalyzer()

    # Apply sentiment analysis to the 'content' column after preprocessing
    def get_scores(text):
        text = preprocess_text(text)
        return sid_obj.polarity_scores(text)

    # Get scores as a Series of dictionaries, then expand into a DataFrame
    scores_series = articles['selftext'].apply(get_scores)
    scores_df = pd.DataFrame(scores_series.tolist())
    articles = pd.concat([articles, scores_df], axis=1)

    # Classify sentiment based on compound score
    def classify_sentiment(compound):
        if compound >= 0.2:
            return "bullish"
        elif compound <= -0.2:
            return "bearish"
        else:
            return "neutral"

    articles['sentiment_class'] = articles['compound'].apply(classify_sentiment)
    return articles

finbert_pipeline = None
def initialize_finbert():
    """
    Initializes the FinBERT pipeline using a finance-specific pretrained model.
    """
    global finbert_pipeline
    if finbert_pipeline is None:
        try:
            finbert_pipeline = pipeline("sentiment-analysis", 
                                          model="yiyanghkust/finbert-tone", 
                                          tokenizer="yiyanghkust/finbert-tone")
        except Exception as e:
            finbert_pipeline = None

def normalize_finbert_score(label, score):
    """
    Normalizes FinBERT sentiment score to:
    - Bullish: 70-100
    - Neutral: 30-70
    - Bearish: 0-30
    """
    if label.lower() == "positive":
        return round(70 + (score * 30), 2)  # Scale from 70 to 100
    elif label.lower() == "neutral":
        return round(30 + (score * 40), 2)  # Scale from 30 to 70
    else:  # Negative
        return round(score * 30, 2)  # Scale from 0 to 30

# this is for SEC filings
def analyze_sentiment_finbert_sec(articles: pd.DataFrame):
    """
    Uses FinBERT to assess sentiment of SEC filings.
    
    Args:
        articles: DataFrame with columns ['content', 'accession_number', etc.]
    Returns:
        DataFrame with added sentiment columns
    """
    global finbert_pipeline
    if finbert_pipeline is None:
        initialize_finbert()
    
    if not finbert_pipeline:
        return articles

    try:
        results = []
        total = len(articles)
        
        
        for idx, row in articles.iterrows():
            content = row.get('content', '')
            
            # Skip empty content
            if not content or pd.isna(content):
                results.append({
                    "accession_number": row["Accession Number"],
                    "sentiment_label": "neutral",
                    "sentiment_score": 50.0,
                    "sentiment_class": "neutral"
                })
                continue

            try:
                # Process in chunks if content is too long
                chunk_size = 512
                chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                chunk_scores = []
                
                for chunk in chunks[:10]:  # Limit to first 10 chunks
                    if not chunk.strip():
                        continue
                    finbert_output = finbert_pipeline(chunk)[0]
                    score = normalize_finbert_score(finbert_output["label"], finbert_output["score"])
                    chunk_scores.append(score)
                
                # Average the chunk scores
                if chunk_scores:
                    final_score = sum(chunk_scores) / len(chunk_scores)
                else:
                    final_score = 50.0  # Neutral score for empty content
                
                # Determine sentiment class
                sentiment_class = classify_sentiment(final_score)
                
                results.append({
                    "accession_number": row["Accession Number"],
                    "sentiment_label": "positive" if final_score > 70 else "negative" if final_score < 30 else "neutral",
                    "sentiment_score": final_score,
                    "sentiment_class": sentiment_class
                })
                
                
            except Exception as e:
                results.append({
                    "accession_number": row["Accession Number"],
                    "sentiment_label": "neutral",
                    "sentiment_score": 50.0,
                    "sentiment_class": "neutral"
                })

        # Convert results to DataFrame and merge
        results_df = pd.DataFrame(results)
        
        # Merge with original DataFrame
        merged_df = articles.merge(
            results_df,
            left_on="Accession Number",
            right_on="accession_number",
            how="left"
        )
        
        # Store results in database
        try:
            store_sentiment_results(results_df)
        except Exception as e:
            pass
        return merged_df

    except Exception as e:
        return articles


def classify_sentiment(score):
    """
    Converts normalized sentiment score into a category:
    - Bullish (≥ 70)
    - Neutral (30-70)
    - Bearish (≤ 30)
    """
    if score >= 70:
        return "bullish"
    elif score <= 30:
        return "bearish"
    else:
        return "neutral"


def analyze_sentiment_finbert_news(articles: pd.DataFrame):
    """
    Uses FinBERT to assess sentiment of a news DataFrame, specifically the 'content' column.
    Adds 'sentiment_score' column.
    
    :param articles: DataFrame with a 'content' column containing news articles.
    :return: DataFrame with sentiment analysis results.
    """
    global finbert_pipeline
    if finbert_pipeline is None:
        initialize_finbert()
    if finbert_pipeline:
        try:
            results = []

            for index, row in articles.iterrows():
                content = row['content']

                # Skip empty content
                if not content or pd.isna(content):
                    results.append({
                        "index": index,  # Add index explicitly
                        "sentiment_score": 50.0,  # Default neutral score
                    })
                    continue

                # Run sentiment analysis
                finbert_output = finbert_pipeline(content)[0]  # Extract first result
                
                # Convert to normalized 0-100 scale
                adjusted_score = normalize_finbert_score(finbert_output["label"], finbert_output["score"])

                # Store results
                results.append({
                    "index": index,  # Add index explicitly
                    "sentiment_score": adjusted_score,  # Now scaled to 0-100
                })
            
            # Convert results into a DataFrame
            results_df = pd.DataFrame(results)

            # Ensure correct merging
            articles = articles.reset_index().merge(results_df, on="index", how="left").set_index("index")

            return articles
        except Exception as e:
            return articles
    else:
        return articles





