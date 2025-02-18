from src.database.base import *
from datetime import datetime, timedelta

def create_market_table(market: str):
    """
    Creates a market index table (e.g., S&P 500) if it doesn't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            date DATE PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT,
            last_updated TIMESTAMP DEFAULT NOW()
        );
    """).format(sql.Identifier(market.lower()))
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def get_last_market_date(market: str):
    """
    Returns the latest date available in the market table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("SELECT MAX(date) FROM {}").format(sql.Identifier(market.lower()))
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


def get_market_data(market: str, period: str = "1d"):
    """
    Fetches market data for the specified index (e.g., S&P 500), ensures the table exists,
    updates data if needed, and returns a graph.

    Args:
        market (str): Market index name (e.g., "sp500").
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        SELECT date, open, high, low, close, volume
        FROM {} 
        ORDER BY date DESC 
        LIMIT %s;
    """).format(sql.Identifier(market.lower()))

    cursor.execute(query, (period,))
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    df.columns = df.columns.str.strip().str.lower()
    return df.sort_values(by="date")


def get_latest_market_data(market: str, window: int):
    """
    Retrieves the latest market data from the database.
    
    Args:
        market (str): Market index name (e.g., "sp500")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        SELECT date, open, high, low, close, volume
        FROM {}
        ORDER BY date DESC
        LIMIT %s;
    """).format(sql.Identifier(market.lower()))
    cursor.execute(query, (window,))
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    df.columns = df.columns.str.strip().str.lower()
    return df.sort_values(by="date")
