import requests
import tweepy
import praw
import time
import re
import string
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
nltk.download('vader_lexicon')
nltk.download('stopwords')

from newspaper import Article

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.linear_model import LinearRegression

# -------------------------
# 1. Data Collection Methods
# -------------------------

def fetch_financial_news(query, count=5):
    """
    Collects financial news articles using NewsAPI.
    Replace "YOUR_NEWSAPI_KEY" with your NewsAPI key.
    """
    news_api_key = "YOUR_NEWSAPI_KEY"  # <-- Replace with your key
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": count,
        "apiKey": news_api_key,
        "language": "en"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get('articles', [])
        news_articles = []
        for article in articles:
            news_articles.append({
                'title': article['title'],
                'url': article['url'],
                'content': article.get('content') or article.get('description', '')
            })
        return news_articles
    except Exception as e:
        print("Error fetching news:", e)
        return []

def fetch_tweets(query, count=50):
    """
    Collects tweets matching the query.
    Replace the placeholder strings with your actual Twitter API credentials.
    """
    consumer_key = "YOUR_TWITTER_CONSUMER_KEY"        # <-- Replace with your key
    consumer_secret = "YOUR_TWITTER_CONSUMER_SECRET"      # <-- Replace with your key
    access_token = "YOUR_TWITTER_ACCESS_TOKEN"            # <-- Replace with your key
    access_token_secret = "YOUR_TWITTER_ACCESS_TOKEN_SECRET"  # <-- Replace with your key

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    try:
        tweets = api.search_tweets(q=query, count=count, lang='en', tweet_mode='extended')
        tweet_texts = []
        for tweet in tweets:
            # Handle retweets if necessary
            if 'retweeted_status' in tweet._json:
                tweet_texts.append(tweet._json['retweeted_status']['full_text'])
            else:
                tweet_texts.append(tweet.full_text)
        return tweet_texts
    except Exception as e:
        print("Error fetching tweets:", e)
        return []

def fetch_reddit_posts(query, count=20):
    """
    Collects Reddit posts matching the query using PRAW.
    Replace the placeholder values with your Reddit API credentials.
    """
    reddit = praw.Reddit(
        client_id="YOUR_REDDIT_CLIENT_ID",          # <-- Replace with your key
        client_secret="YOUR_REDDIT_CLIENT_SECRET",    # <-- Replace with your key
        user_agent="YOUR_USER_AGENT"                 # <-- Replace with your key
    )
    posts = []
    try:
        # Search in all subreddits for demonstration
        for submission in reddit.subreddit("all").search(query, limit=count):
            posts.append(submission.title + ". " + submission.selftext)
        return posts
    except Exception as e:
        print("Error fetching Reddit posts:", e)
        return []

def load_earnings_call_transcripts():
    """
    Simulated earnings call transcripts.
    In a production system, you might scrape or download transcripts.
    """
    transcripts = [
        "CEO: We are confident in our long-term growth. Our Q2 results exceeded expectations.",
        "CEO: We are facing challenges due to supply chain constraints. Our margins are under pressure."
    ]
    return transcripts

def load_analyst_reports():
    """
    Simulated analyst reports.
    In reality, you might parse PDFs, scrape web pages, or use a dedicated API.
    """
    reports = [
        "Goldman Sachs upgrades Apple to Strong Buy. The tech giant is expected to outperform.",
        "Morgan Stanley cuts Amazon target by 20% amid rising competition."
    ]
    return reports

# -------------------------
# 2. Preprocessing Function
# -------------------------

def preprocess_text(text):
    """
    Cleans text by lowercasing, removing URLs, punctuation, HTML tags,
    numbers, and stopwords.
    """
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\w*\d\w*', '', text)
    stop_words = set(stopwords.words("english"))
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

# -------------------------
# 3. Sentiment Analysis Functions
# -------------------------

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

# -------------------------
# 4. Aggregation Function
# -------------------------

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

# -------------------------
# 6. Main Pipeline
# -------------------------

def main():
    # Ask user for the financial topic or ticker symbol
    query = input("Enter a financial topic (e.g., Tesla, Fed, etc.): ")

    # ----- Data Collection -----
    print("\nCollecting Financial News...")
    news_articles = fetch_financial_news(query, count=5)
    print(f"Collected {len(news_articles)} news articles.")

    print("\nCollecting Tweets...")
    tweets = fetch_tweets(query, count=50)
    print(f"Collected {len(tweets)} tweets.")

    print("\nCollecting Reddit Posts...")
    reddit_posts = fetch_reddit_posts(query, count=20)
    print(f"Collected {len(reddit_posts)} Reddit posts.")

    print("\nLoading Earnings Call Transcripts...")
    transcripts = load_earnings_call_transcripts()
    print(f"Loaded {len(transcripts)} earnings call transcripts.")

    print("\nLoading Analyst Reports...")
    analyst_reports = load_analyst_reports()
    print(f"Loaded {len(analyst_reports)} analyst reports.")

    # ----- Data Preprocessing & Sentiment Analysis -----
    # For each source, preprocess texts and compute an average sentiment score.
    def process_texts(texts):
        vader_scores = []
        finbert_scores = []
        for text in texts:
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
    tweet_texts = tweets
    reddit_texts = reddit_posts
    transcript_texts = transcripts
    analyst_texts = analyst_reports

    # Compute average sentiment for each source
    source_sentiments = {}
    source_sentiments['financial_news'] = process_texts(news_texts)
    source_sentiments['tweets'] = process_texts(tweet_texts)
    source_sentiments['reddit'] = process_texts(reddit_texts)
    source_sentiments['earnings_calls'] = process_texts(transcript_texts)
    source_sentiments['analyst_reports'] = process_texts(analyst_texts)

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
