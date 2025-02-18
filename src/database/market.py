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
    Fetches the latest market data for an index like S&P 500.
    If data is missing or outdated, fetches from Yahoo Finance and updates the database.
    """
    last_date = get_last_market_date(market)

    # If data exists and is up to date, return from DB
    if last_date and last_date >= datetime.utcnow().date() - timedelta(days=1):
        conn = get_db_connection()
        df = pd.read_sql(
            sql.SQL("SELECT * FROM {} ORDER BY date DESC LIMIT 100").format(sql.Identifier(market.lower())),
            conn
        )
        conn.close()
        return df.to_dict(orient="records")

    # Otherwise, fetch fresh data from Yahoo Finance
    ticker = "^GSPC" if market.lower() == "sp500" else market.upper()
    data = yf.Ticker(ticker).history(period=period)

    if data.empty:
        return {"error": "No data found for the given period."}

    conn = get_db_connection()
    cursor = conn.cursor()

    for index, row in data.iterrows():
        cursor.execute(
            sql.SQL("""
                INSERT INTO {} (date, open, high, low, close, volume, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (date) DO NOTHING;
            """).format(sql.Identifier(market.lower())),
            (index.date(), row["Open"], row["High"], row["Low"], row["Close"], row["Volume"])
        )

    conn.commit()
    cursor.close()
    conn.close()

    return get_market_data(market, period)  # Return updated data

