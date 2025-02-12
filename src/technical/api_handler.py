from src.database.db_operations import *
from src.technical.calculateIndicators import *
from src.technical.fetchData import *


def function(ticker: str):
    create_stock_table(ticker)
    fetch_stock_data(ticker)
    df = get_latest_stock_data(ticker, window=200)
    signal, final_score = calculate_score(df)
    return signal, final_score
