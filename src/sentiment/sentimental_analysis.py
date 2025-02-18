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

def main():
    query = input("Enter a financial topic (e.g., Tesla, Fed, etc.): ")
    return sentiment(query)

if __name__ == '__main__':
    main()
