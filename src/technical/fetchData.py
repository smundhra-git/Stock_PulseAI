import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from src.database.db_operations import *  # Import database functions

def fetch_stock_data(ticker: str, interval: str = "1d"):
    """
    Fetches historical stock price data for a given ticker and stores it in PostgreSQL.
    
    Steps:
        1. Check if new data is available
        2. If no data exists, get all data
        3. If some data exists, get data from the last available date onwards
    """

    last_date = get_last_date(ticker)

    if last_date is None:
        data = yf.download(ticker, period="max", interval=interval)
    else:
        start_date = pd.to_datetime(last_date) + pd.Timedelta(days=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        data = yf.download(ticker, start=start_date_str, interval=interval)

    if data.empty:
        return {"message": "No new data available."}, 204  # No Content

    data.reset_index(inplace=True)

    # Flatten MultiIndex if it exists
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0].lower() if col[1] == '' else f"{col[0].lower()}_{col[1].lower()}" for col in data.columns]

    # Rename "date_" to "date" if necessary
    if 'date_' in data.columns:
        data.rename(columns={'date_': 'date'}, inplace=True)

    # Remove ticker suffix dynamically if present
    ticker_suffix = f"_{ticker.lower()}"
    renamed_columns = {col: col.replace(ticker_suffix, "") for col in data.columns if col.endswith(ticker_suffix)}
    data.rename(columns=renamed_columns, inplace=True)

    # Ensure required columns exist
    required_columns = ["date", "close", "high", "low", "open", "volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns after renaming: {missing_columns}")

    data["date"] = pd.to_datetime(data["date"]).dt.date  # Ensure date format

    # Prepare for inserting into PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()

    # Use psycopg2.sql for safe table name formatting
    query = sql.SQL("""
        INSERT INTO {} (date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING;
    """).format(sql.Identifier(ticker.lower()))  # Safe table formatting

    for _, row in data.iterrows():
        values = (row["date"], row["open"], row["high"], row["low"], row["close"], row["volume"])
        try:
            cursor.execute(query, values)
        except Exception as e:
            conn.rollback()  # Rollback on error
            print(f"Error inserting row: {e}")  # Log the error
            continue  # Skip to next row

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Stock data fetched successfully."}, 200  # OK

# Testing the function
if __name__ == "__main__":
    ticker = "AAPL"  # ✅ Use uppercase for API calls, lowercase for table naming
    fetch_stock_data(ticker)
