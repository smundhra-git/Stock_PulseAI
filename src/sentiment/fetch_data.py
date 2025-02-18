"""
NEXT STEPS:
1. Get Bloomberg data for earnings transcript
2. Get Bloomberg data for analyst reports
3. Get X API for retail sentiments
"""

import requests
import os
from dotenv import load_dotenv
import requests
# from snscrape.modules.twitter import *
import praw
import certifi
import datetime
from src.database.sentiment import *
import requests
from datetime import datetime
from dateutil.parser import parse  # Requires the python-dateutil package

# Load environment variables from .env
load_dotenv()

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# News API key from environment
news_api_key = os.getenv("NEWSAPI")


def fetch_financial_news(query, count=20, from_date=None):
    """
    Collects financial news articles using NewsAPI.
    If from_date is provided, only articles published on or after that date are fetched.
    The returned articles are sorted by their published date (most recent first).
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": count,
        "apiKey": news_api_key,
        "language": "en"
    }
    if from_date:
        params["from"] = from_date.strftime("%Y-%m-%d")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        news_articles = []
        for article in articles:
            news_articles.append({
                'title': article['title'],
                'url': article['url'],
                'content': article.get('content') or article.get('description', ''),
                'publishedAt': article.get('publishedAt', None)
            })
        # Sort articles by publishedAt date (most recent first)
        news_articles.sort(
            key=lambda x: parse(x['publishedAt']) if x['publishedAt'] else datetime.min,
            reverse=True
        )
        return news_articles
    except Exception as e:
        print("Error fetching news:", e)
        return []
# Further documentation - https://github.com/JustAnotherArchivist/snscrape/blob/master/snscrape/modules/twitter.py
def fetch_tweets(query, max_tweets=50, from_date=None):
    """
    Collects tweets matching the query using Snscrape's TwitterSearchScraper.
    If from_date is provided, a 'since:' clause is appended to the query.
    
    Args:
        query (str): The search query (for example, a ticker symbol).
        max_tweets (int): The maximum number of tweets to fetch.
        from_date (datetime.datetime, optional): Only fetch tweets after this date.
    
    Returns:
        List[dict]: A list of dictionaries, each containing tweet content and date.
    """
    # If a from_date is provided, add the since clause to the query.
    if from_date:
        query = f"{query} since:{from_date.strftime('%Y-%m-%d')}"
    
    # Create the scraper instance using the default LIVE mode.
    scraper = TwitterSearchScraper(query, mode=TwitterSearchScraperMode.LIVE)
    
    tweets_list = []
    # Iterate over tweets from the scraper.
    for tweet in scraper.get_items():
        tweets_list.append({
            'content': tweet.content,
            'date': tweet.date.isoformat() if tweet.date else None
        })
        # Stop when we have fetched the desired number of tweets.
        if len(tweets_list) >= max_tweets:
            break
    return tweets_list


def fetch_reddit_posts(query, count=50, from_date=None):
    """
    Collects Reddit posts matching the query using PRAW.
    If from_date is provided, only posts created on or after that date are returned.
    """
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENTID"),
        client_secret=os.getenv("REDDIT_CLIENTSECRET"),
        user_agent="TRIAL"
    )
    posts = []
    try:
        for submission in reddit.subreddit("all").search(query, limit=count):
            # Filter based on submission creation time if from_date is provided.
            if from_date:
                if submission.created_utc < from_date.timestamp():
                    continue
            posts.append({
                'title': submission.title,
                'selftext': submission.selftext,
                'created_utc': submission.created_utc
            })
        return posts
    except Exception as e:
        print("Error fetching Reddit posts:", e)
        return []


def main():
    ticker = input("Enter a ticker (e.g., TSLA, AAPL, etc.): ").strip()
    
    # Ensure that the necessary tables exist.
    create_news_table()
    create_reddit_table()
    
    # Retrieve the last fetch dates from the database for incremental fetching.
    last_news_date = get_last_news_date(ticker)
    last_reddit_date = get_last_reddit_date(ticker)
    
    news_articles = fetch_financial_news(ticker, from_date=last_news_date)
    insert_news_data(ticker, news_articles)
    """
    To Work with twitter later
    """
    #     create_tweets_table()
    # last_tweets_date = get_last_tweets_date(ticker)
    # print("\nFetching Tweets...")
    # tweets = fetch_tweets(ticker, from_date=last_tweets_date)
    # print(f"Fetched {len(tweets)} tweets for {ticker}.")
    # for tweet in tweets:
    #     print("Date:", tweet.get('date'))
    #     print("Content:", tweet.get('content'))
    #     print("-" * 40)
    # insert_tweets_data(ticker, tweets)
    
    reddit_posts = fetch_reddit_posts(ticker, from_date=last_reddit_date)
    insert_reddit_data(ticker, reddit_posts)




"""
Next Idea -> Fetch Data
-> Store them in the database
-> Analysis will get data from database directly?
"""