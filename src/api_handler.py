from src.database.stocks import *
from src.technical.calculateIndicators import *
from src.technical.fetchData import *
from src.technical.graph import *
from src.sentiment.fetch_data import *
from src.sentiment.sentimental_analysis import *
from src.front.front import *
from src.database.market import *
from src.sentiment.sentiment import main as get_sentiment


def function(ticker: str):
    create_stock_table(ticker)
    fetch_stock_data(ticker)
    df = get_latest_stock_data(ticker, window=200)
    signal, final_score = calculate_score(df)
    return signal, final_score

def get_stock_graph(ticker, period):
    return get_stock_graph_function(ticker, period)


def get_candlestick(ticker, period, interval):
    return get_candlestick_chart(ticker, period, interval)

def get_sentiments(ticker:str):
    article = fetch_financial_news(ticker, 100)
    articles_df = pd.DataFrame(article)
    articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
    articles_df = articles_df.sort_values('publishedAt', ascending=False)
    articles_df = analyze_sentiment_vader(articles_df)
    return articles_df


def get_market_data(market: str, period: str = "1d"):
    """
    Get market data with proper error handling
    """
    create_market_table(market)
    fetch_market_data(market, period)  # This fetches and stores in DB
    return get_market_data_fn(market, period)  # This retrieves from DB and creates graph

def get_sentiment_score(ticker: str) -> dict:
    """
    Get sentiment scores for a given stock ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL")
    Returns:
        dict: Dictionary containing sentiment scores
    """
    try:
        sentiment_scores = get_sentiment(ticker)
        if sentiment_scores is None:
            return {
                "error": "Failed to get sentiment scores",
                "ticker": ticker
            }
            
        return {
            "ticker": ticker,
            "news_sentiment": round(sentiment_scores['news_sentiment_score'], 2),
            "reddit_sentiment": round(sentiment_scores['reddit_sentiment_score'], 2),
            "sec_sentiment": round(sentiment_scores['sec_sentiment_score'], 2),
            "overall_sentiment": round(sentiment_scores['sentiment_score'], 2)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "ticker": ticker
        }

