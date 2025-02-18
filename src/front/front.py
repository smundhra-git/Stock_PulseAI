from src.database.base import *
from src.database.market import *
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.express as px
# Mapping from custom period string to number of days (assumed trading days)
PERIOD_MAPPING = {
    "1w": 7,
    "1month": 30,
    "3months": 90,
    "6months": 180,
    "1y": 365,
    "5y": 1825
}

def fetch_market_data(market: str, period: str = "1mo"):
    last_date = get_last_market_date(market)
    if last_date is None:
        data = yf.download(market, period="max", interval="1d")
    else:
        start_date = pd.to_datetime(last_date) + pd.Timedelta(days=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        data = yf.download(market, start=start_date_str, interval="1d")

    if data.empty:
        return {"message": "No new data available."}, 204
    
    data.reset_index(inplace=True)
    print("Original columns:", data.columns.tolist())

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [
            col[0].lower() if col[1] == "" else f"{col[0].lower()}_{col[1].lower()}"
            for col in data.columns
        ]
    else:
        data.columns = [col.lower() for col in data.columns]

    if "date_" in data.columns:
        data.rename(columns={"date_": "date"}, inplace=True)

    ticker_suffix = f"_{market.lower()}"
    renamed_columns = {col: col.replace(ticker_suffix, "") for col in data.columns if col.endswith(ticker_suffix)}
    if renamed_columns:
        data.rename(columns=renamed_columns, inplace=True)

    required_columns = ["date", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns after renaming: {missing_columns}")
        
    data["date"] = pd.to_datetime(data["date"]).dt.date

    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        INSERT INTO {} (date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (date) DO NOTHING;
    """).format(sql.Identifier(market.lower()))

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
    return {"message": "Stock data fetched successfully."}, 200


def get_market_data_fn(market: str, period: str = "1mo"):
    """
    Fetches market data for the specified index (e.g., S&P 500), ensures the table exists,
    updates data if needed, and returns a graph.

    Args:
        market (str): Market index name (e.g., "sp500").
        period (str): Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max").

    Returns:
        dict: JSON data containing the Plotly graph.
    """

    period = period.lower()
    if period == "max":
        window = 10000
    else:
        if period not in PERIOD_MAPPING:
            raise ValueError("Invalid period. Choose from 1w, 1month, 3months, 6months, 1y, 5y, or max.")
        window = PERIOD_MAPPING[period]
    
    data = get_latest_market_data(market, window)
    if data.empty:
        raise ValueError("No data fetched for market")
    
    data.set_index("date", inplace=True)

    # Get a more readable title for the market
    market_titles = {
        "^GSPC": "S&P 500",
        "sp500": "S&P 500"
    }
    market_title = market_titles.get(market, market.upper())

    fig = px.line(
        data_frame=data,
        x=data.index,
        y="close",
        title=f"{market_title} Stock Price ({period})",
        labels={"x": "Date", "close": "Closing Price"},
        template="plotly_white"
    )
    
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )

    return fig

