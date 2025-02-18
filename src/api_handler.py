from src.database.stocks import *
from src.technical.calculateIndicators import *
from src.technical.fetchData import *
from src.technical.graph import *
from src.sentiment.fetch_data import *
from src.sentiment.sentimental_analysis import *
from src.front.front import *


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
    get_market_data_fn(market, period)