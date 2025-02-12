import os
from dotenv import load_dotenv
import requests
import snscrape.modules.twitter as sntwitter
import praw

load_dotenv()

news_api_key = os.getenv("NEWSAPI")


def fetch_financial_news(query, count=20):
    """
    Collects financial news articles using NewsAPI.
    """
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

def fetch_tweets(query, max_tweets=50):
    """
    Collects tweets matching the query using snscrape.
    This method does not require API keys.
    """
    tweets_list = []
    try:
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            if len(tweets_list) >= max_tweets:
                break
            tweets_list.append(tweet.content)
        return tweets_list
    except Exception as e:
        print("Error fetching tweets via snscrape:", e)
        return []
    
def fetch_reddit_posts(query, count=50):
    """
    Collects Reddit posts matching the query using PRAW.
    Replace the placeholder values with your Reddit API credentials.
    """
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENTID"),          
        client_secret=os.getenv("REDDIT_CLIENTSECRET"),    
        user_agent="TRIAL"                 
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
    
# WE WILL USE BLOOMBERG API AFTER FUNDING