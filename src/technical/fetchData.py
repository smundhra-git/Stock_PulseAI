import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from src.database.stocks import *  # Import database functions

def fetch_stock_data(ticker: str, interval: str = "1d"):
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

    # Debug: print original columns
    print("Original columns:", data.columns.tolist())

    # If the columns are a MultiIndex, flatten them; otherwise, convert to lowercase
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [
            col[0].lower() if col[1] == "" else f"{col[0].lower()}_{col[1].lower()}"
            for col in data.columns
        ]
    else:
        data.columns = [col.lower() for col in data.columns]

    # Debug: print processed columns
    print("Processed columns:", data.columns.tolist())

    # If a column is named "date_" (rare case), rename it to "date"
    if "date_" in data.columns:
        data.rename(columns={"date_": "date"}, inplace=True)

    # Remove ticker suffix if present (e.g. "close_aapl" becomes "close")
    ticker_suffix = f"_{ticker.lower()}"
    renamed_columns = {col: col.replace(ticker_suffix, "") for col in data.columns if col.endswith(ticker_suffix)}
    if renamed_columns:
        data.rename(columns=renamed_columns, inplace=True)

    # Ensure required columns exist
    required_columns = ["date", "close", "high", "low", "open", "volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns after renaming: {missing_columns}")

    # Ensure date column is in the proper format
    data["date"] = pd.to_datetime(data["date"]).dt.date

    # --- Insert into PostgreSQL code ---
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        INSERT INTO {} (date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING;
    """).format(sql.Identifier(ticker.lower()))

    for _, row in data.iterrows():
        values = (row["date"], row["open"], row["high"], row["low"], row["close"], row["volume"])
        try:
            cursor.execute(query, values)
        except Exception as e:
            conn.rollback()
            print(f"Error inserting row: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Stock data fetched successfully."}, 200  # OK

# Testing the function
if __name__ == "__main__":
    ticker = "COIN"  # ✅ Use uppercase for API calls, lowercase for table naming
    fetch_stock_data(ticker)
