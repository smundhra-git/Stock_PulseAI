import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from datetime import datetime

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Database connection parameters from .env
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)

def create_metadata_table():
    """Creates a metadata table to track the last saved date for each stock."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_metadata (
            ticker VARCHAR(10) PRIMARY KEY,
            last_saved_date DATE
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def get_last_saved_date(ticker: str):
    """Fetches the last saved date for a given stock from metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT last_saved_date FROM stock_metadata WHERE ticker = %s;", (ticker,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return result[0] if result else None

def update_last_saved_date(ticker: str, last_date: str):
    """Updates the metadata table with the latest saved date for a stock."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO stock_metadata (ticker, last_saved_date)
        VALUES (%s, %s)
        ON CONFLICT (ticker) DO UPDATE 
        SET last_saved_date = EXCLUDED.last_saved_date;
    """, (ticker, last_date))
    
    conn.commit()
    cursor.close()
    conn.close()

def create_stock_table(ticker: str):
    """Creates a stock-specific table with moving averages if it doesn't exist."""
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
            sma_20 FLOAT,
            sma_50 FLOAT,
            ema_20 FLOAT
        );
    """).format(sql.Identifier(ticker.lower()))

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def fetch_stock_data(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    Fetches historical stock price data for a given ticker,
    storing only new data in PostgreSQL.

    Parameters:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
        period (str): Data period (default "1y").
        interval (str): Time interval (default "1d").

    Returns:
        None (Data is stored in the database)
    """
    last_saved_date = get_last_saved_date(ticker)
    
    # If we have a last saved date, only pull new data
    if last_saved_date:
        start_date = (last_saved_date + pd.DateOffset(days=1)).strftime("%Y-%m-%d")
        data = yf.download(ticker, start=start_date, interval=interval)
    else:
        data = yf.download(ticker, period=period, interval=interval)

    if data.empty:
        print(f"❌ No new data found for {ticker}")
        return

    # Prepare data for insertion
    data.reset_index(inplace=True)
    data = data[["Date", "Open", "High", "Low", "Close", "Volume"]]
    data["Date"] = pd.to_datetime(data["Date"]).dt.date  # Convert to date only

    # ✅ Calculate Moving Averages
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["EMA_20"] = data["Close"].ewm(span=20, adjust=False).mean()

    # Insert new data into PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()

    for _, row in data.iterrows():
        query = sql.SQL("""
            INSERT INTO {} (date, open, high, low, close, volume, sma_20, sma_50, ema_20)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING;
        """).format(sql.Identifier(ticker.lower()))

        cursor.execute(query, tuple(row))

    # Commit changes & update last saved date
    conn.commit()
    cursor.close()
    conn.close()

    last_date = data["Date"].max().strftime("%Y-%m-%d")
    update_last_saved_date(ticker, last_date)

    print(f"✅ Successfully updated {ticker} data up to {last_date}")

# ✅ Testing the function
if __name__ == "__main__":
    create_metadata_table()  # Ensure metadata table exists
    ticker = "AAPL"  # Example stock ticker
    create_stock_table(ticker)  # Ensure stock table exists
    fetch_stock_data(ticker)
