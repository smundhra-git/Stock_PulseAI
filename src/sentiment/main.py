import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from transformers import pipeline
from sklearn.linear_model import LinearRegression

from sentiment.fetch_data import *
from sentiment.process import *

def analyze_sentiment_vader(text):
    """
    Uses NLTK's VADER to calculate sentiment.
    Returns a dictionary with sentiment scores.
    """
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return sentiment  # Contains 'neg', 'neu', 'pos', and 'compound'

# FinBERT initialization (only once)
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
            print("Error initializing FinBERT pipeline:", e)
            finbert_pipeline = None

def analyze_sentiment_finbert(text):
    """
    Uses FinBERT to assess sentiment.
    Returns a dictionary with a 'label' and a 'score'.
    """
    global finbert_pipeline
    if finbert_pipeline is None:
        initialize_finbert()
    if finbert_pipeline:
        try:
            result = finbert_pipeline(text)
            # Result format example: [{'label': 'positive', 'score': 0.95}]
            return result[0]
        except Exception as e:
            print("FinBERT analysis error:", e)
            return {"label": "neutral", "score": 0.0}
    else:
        return {"label": "neutral", "score": 0.0}

def finbert_label_to_score(label, score):
    """
    Converts FinBERT sentiment labels to a numeric score.
    Positive maps to +score, negative to -score, neutral to 0.
    """
    if label.lower() == "positive":
        return score
    elif label.lower() == "negative":
        return -score
    else:
        return 0.0

def aggregate_sentiments(sentiment_data, weights):
    """
    Aggregates sentiment scores from multiple sources.
    sentiment_data: dict mapping source names to numeric sentiment scores.
    weights: dict mapping source names to their respective weights.
    Returns a single aggregated sentiment score.
    """
    total_weight = sum(weights.values())
    aggregated_score = 0.0
    for source, score in sentiment_data.items():
        aggregated_score += score * weights.get(source, 0)
    if total_weight:
        aggregated_score /= total_weight
    return aggregated_score

# -------------------------
# 5. Stock Price Prediction (Simulation)
# -------------------------

def predict_stock_prices(sentiment_series, price_series):
    """
    Fits a linear regression model to simulate the relationship between sentiment and stock prices.
    sentiment_series: array-like of sentiment scores.
    price_series: array-like of stock prices (or returns).
    Returns the predictions and the trained model.
    """
    model = LinearRegression()
    X = np.array(sentiment_series).reshape(-1, 1)
    y = np.array(price_series)
    model.fit(X, y)
    print("\n--- Stock Price Regression ---")
    print("Regression Coefficient:", model.coef_[0])
    print("Regression Intercept:", model.intercept_)
    predictions = model.predict(X)
    return predictions, model


def main():
    # Ask user for the financial topic or ticker symbol
    query = input("Enter a financial topic (e.g., Tesla, Fed, etc.): ")

    # ----- Data Collection -----
    print("\nCollecting Financial News...")
    news_articles = fetch_financial_news(query, count=5)
    print(f"Collected {len(news_articles)} news articles.")

    # print("\nCollecting Tweets...")
    # tweets = fetch_tweets(query, count=50)
    # print(f"Collected {len(tweets)} tweets.")

    print("\nCollecting Reddit Posts...")
    reddit_posts = fetch_reddit_posts(query, count=20)
    print(f"Collected {len(reddit_posts)} Reddit posts.")

    # ----- Data Preprocessing & Sentiment Analysis -----
    # For each source, preprocess texts and compute an average sentiment score.
    def process_texts(texts):
        vader_scores = []
        finbert_scores = []
        for text in texts:
            if(type(text) != str):
                processed = preprocess_text_dict(text)
            else:
                processed = preprocess_text(text)
            # VADER sentiment
            vader_result = analyze_sentiment_vader(processed)
            vader_score = vader_result['compound']
            vader_scores.append(vader_score)
            # FinBERT sentiment
            finbert_result = analyze_sentiment_finbert(processed)
            finbert_score = finbert_label_to_score(finbert_result['label'], finbert_result['score'])
            finbert_scores.append(finbert_score)
        avg_vader = np.mean(vader_scores) if vader_scores else 0
        avg_finbert = np.mean(finbert_scores) if finbert_scores else 0
        # Combine the two methods equally
        combined = (avg_vader + avg_finbert) / 2.0
        return combined

    # Prepare texts from each data source
    news_texts = [article['title'] + ". " + article['content'] for article in news_articles if article['content']]
    reddit_texts = reddit_posts

    # Compute average sentiment for each source
    source_sentiments = {}
    source_sentiments['financial_news'] = process_texts(news_texts)
    source_sentiments['reddit'] = process_texts(reddit_texts)
    print("\n--- Individual Source Sentiment Scores ---")
    for source, score in source_sentiments.items():
        print(f"{source:20s}: {score:.3f}")

    # Define weights for each source (example weights)
    weights = {
        'financial_news': 0.4,
        'tweets': 0.2,
        'reddit': 0.2,
        'earnings_calls': 0.1,
        'analyst_reports': 0.1
    }

    aggregated_sentiment = aggregate_sentiments(source_sentiments, weights)
    print(f"\nAggregated Sentiment Score for '{query}': {aggregated_sentiment:.3f}")

    # ----- Simulate Stock Price Prediction -----
    # For demonstration, we simulate a time series of sentiment scores around the aggregated sentiment.
    time_periods = 10
    np.random.seed(42)
    # Create simulated sentiment variations over time
    sentiment_series = aggregated_sentiment + np.random.normal(0, 0.1, time_periods)
    # Simulate a stock price series (e.g., base price of 100, sentiment influences price changes)
    base_price = 100
    price_series = base_price + np.cumsum(sentiment_series * 5 + np.random.normal(0, 1, time_periods))

    predictions, model = predict_stock_prices(sentiment_series, price_series)
    print("\nSimulated Sentiment Time Series:")
    print(sentiment_series)
    print("\nSimulated Stock Price Series:")
    print(price_series)
    print("\nPredicted Stock Prices (from Regression):")
    print(predictions)

    # ----- Plotting the Results -----
    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    plt.plot(range(time_periods), sentiment_series, marker='o', label='Sentiment Score')
    plt.title("Simulated Sentiment Time Series")
    plt.xlabel("Time Period")
    plt.ylabel("Sentiment Score")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(range(time_periods), price_series, marker='o', color='green', label='Stock Price')
    plt.plot(range(time_periods), predictions, marker='x', color='red', linestyle='--', label='Predicted Price')
    plt.title("Simulated Stock Price Series and Predictions")
    plt.xlabel("Time Period")
    plt.ylabel("Stock Price")
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
