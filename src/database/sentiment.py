from src.database.base import *


def create_news_table():
    """Creates the news_data table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS news_data (
            id SERIAL PRIMARY KEY,
            ticker TEXT,
            title TEXT,
            url TEXT,
            content TEXT,
            published_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT NOW()
        );
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def insert_news_data(ticker: str, news_articles: list):
    """
    Inserts news article records into the news_data table.
    Each article in news_articles should be a dict with keys:
    title, url, content, and publishedAt.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO news_data (ticker, title, url, content, published_at, fetched_at)
        VALUES (%s, %s, %s, %s, %s, NOW());
    """
    for article in news_articles:
        published_at = None
        if article.get("publishedAt"):
            try:
                # Convert publishedAt to a datetime (assuming ISO format)
                published_at = pd.to_datetime(article["publishedAt"])
            except Exception as e:
                print("Error parsing publishedAt for article:", e)
        cursor.execute(insert_query, (
            ticker,
            article.get("title"),
            article.get("url"),
            article.get("content"),
            published_at
        ))
    conn.commit()
    cursor.close()
    conn.close()


def get_last_news_date(ticker: str):
    """
    Returns the latest published_at date for the given ticker from the news_data table.
    If no data exists, returns None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT MAX(published_at) FROM news_data WHERE ticker = %s;"
    cursor.execute(query, (ticker,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


#############################################
# Tweets Data Table Functions
#############################################

def create_tweets_table():
    """Creates the tweets_data table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS tweets_data (
            id SERIAL PRIMARY KEY,
            ticker TEXT,
            content TEXT,
            tweet_date TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT NOW()
        );
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def insert_tweets_data(ticker: str, tweets: list):
    """
    Inserts tweet records into the tweets_data table.
    Each tweet in tweets should be a dict with keys: content and date.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO tweets_data (ticker, content, tweet_date, fetched_at)
        VALUES (%s, %s, %s, NOW());
    """
    for tweet in tweets:
        tweet_date = None
        if tweet.get("date"):
            try:
                tweet_date = pd.to_datetime(tweet["date"])
            except Exception as e:
                print("Error parsing tweet date:", e)
        cursor.execute(insert_query, (ticker, tweet.get("content"), tweet_date))
    conn.commit()
    cursor.close()
    conn.close()

def get_last_tweets_date(ticker: str):
    """
    Returns the latest tweet_date for the given ticker from the tweets_data table.
    If no data exists, returns None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT MAX(tweet_date) FROM tweets_data WHERE ticker = %s;"
    cursor.execute(query, (ticker,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result



#############################################
# Reddit Data Table Functions
#############################################

def create_reddit_table():
    """Creates the reddit_data table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS reddit_data (
            id SERIAL PRIMARY KEY,
            ticker TEXT,
            title TEXT,
            selftext TEXT,
            created_utc TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT NOW()
        );
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def insert_reddit_data(ticker: str, reddit_posts: list):
    """
    Inserts Reddit post records into the reddit_data table.
    Each post in reddit_posts should be a dict with keys: title, selftext, and created_utc.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO reddit_data (ticker, title, selftext, created_utc, fetched_at)
        VALUES (%s, %s, %s, %s, NOW());
    """
    for post in reddit_posts:
        created_utc = None
        if post.get("created_utc"):
            try:
                # Convert the Unix timestamp (in seconds) to a datetime object.
                timestamp = float(post["created_utc"])
                created_utc = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
            except Exception as e:
                print("Error parsing reddit post created_utc:", e)
        cursor.execute(insert_query, (ticker, post.get("title"), post.get("selftext"), created_utc))
    conn.commit()
    cursor.close()
    conn.close()


def get_last_reddit_date(ticker: str):
    """
    Returns the latest created_utc date for the given ticker from the reddit_data table.
    If no data exists, returns None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT MAX(created_utc) FROM reddit_data WHERE ticker = %s;"
    cursor.execute(query, (ticker,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result



def get_latest_news_data(ticker: str, window: int = 100):
    conn = get_db_connection()
    query = sql.SQL("""
        SELECT * FROM news_data 
        WHERE ticker = %s
        ORDER BY published_at DESC 
        LIMIT %s;
    """)
    df = pd.read_sql(query.as_string(conn), conn, params=(ticker, window))
    conn.close()
    return df

def get_latest_tweets_data(ticker: str, window: int = 100):
    conn = get_db_connection()
    query = sql.SQL("""
        SELECT * FROM tweets_data 
        WHERE ticker = %s
        ORDER BY tweet_date DESC 
        LIMIT %s;
    """)
    df = pd.read_sql(query.as_string(conn), conn, params=(ticker, window))
    conn.close()
    return df

def get_latest_reddit_data(ticker: str, window: int = 100):
    conn = get_db_connection()
    query = sql.SQL("""
        SELECT * FROM reddit_data 
        WHERE ticker = %s
        ORDER BY created_utc DESC 
        LIMIT %s;
    """)
    df = pd.read_sql(query.as_string(conn), conn, params=(ticker, window))
    conn.close()
    return df
