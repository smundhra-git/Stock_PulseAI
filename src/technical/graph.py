import plotly.express as px
import plotly.graph_objects as go
from src.database.stocks import get_latest_stock_data
import pandas as pd

# Mapping from custom period string to number of days (assumed trading days)
PERIOD_MAPPING = {
    "1w": 7,
    "1month": 30,
    "3months": 90,
    "6months": 180,
    "1y": 365,
    "5y": 1825
}

def get_stock_graph_function(ticker: str, period: str = "1y"):
    """
    Returns a Plotly line chart of the closing price for the given ticker.
    The period parameter should be one of: 1w, 1month, 3months, 6months, 1y, 5y, or max.
    Data is retrieved from the database using get_latest_stock_data.
    """
    period = period.lower()
    if period == "max":
        # Use a high window value to approximate 'all available data'
        window = 10000
    else:
        if period not in PERIOD_MAPPING:
            raise ValueError("Invalid period. Choose from 1w, 1month, 3months, 6months, 1y, 5y, or max.")
        window = PERIOD_MAPPING[period]
    
    data = get_latest_stock_data(ticker, window)
    if data.empty:
        raise ValueError("No data fetched for ticker")
    
    # Ensure that the date column is used as the index
    data.set_index("date", inplace=True)
    
    # Create a line chart using the closing price with a business-classic white background
    fig = px.line(
        data_frame=data, 
        x=data.index, 
        y="close", 
        title=f"{ticker.upper()} Stock Price ({period})",
        labels={"x": "Date", "close": "Closing Price"},
        template="plotly_white"
    )
    
    # Optionally update layout to add gridlines and other styling
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )
    
    return fig

def get_candlestick_chart(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    Returns a Plotly candlestick chart for the given ticker.
    
    Parameters:
        ticker (str): Stock ticker symbol.
        period (str): One of 1w, 1month, 3months, 6months, 1y, 5y, or max.
                      This determines how many rows (days) to retrieve from the DB.
        interval (str): The desired aggregation interval (e.g., "1d", "2d", "5d", "1y").
                        When not "1d", daily data is resampled to the given interval.
    
    Data is retrieved from the database using get_latest_stock_data.
    
    Additionally, if any date's data is missing in the series, the function fills in the gap by
    reindexing over all business days and forward-filling missing price values.
    """
    period = period.lower()
    if period == "max":
        window = 10000  # A high number to approximate all available data
    else:
        if period not in PERIOD_MAPPING:
            raise ValueError("Invalid period. Choose from 1w, 1month, 3months, 6months, 1y, 5y, or max.")
        window = PERIOD_MAPPING[period]
    
    data = get_latest_stock_data(ticker, window)
    if data.empty:
        raise ValueError("No data fetched for ticker")
    
    # Ensure the date column is in datetime format and set as index
    data["date"] = pd.to_datetime(data["date"])
    data.set_index("date", inplace=True)
    data.sort_index(inplace=True)
    
    # Reindex the data to fill any missing business days (i.e. "close the gap")
    all_dates = pd.date_range(start=data.index.min(), end=data.index.max(), freq='B')
    data = data.reindex(all_dates)
    # Forward-fill price data and set missing volume to 0
    data[['open', 'high', 'low', 'close']] = data[['open', 'high', 'low', 'close']].fillna(method='ffill')
    data['volume'] = data['volume'].fillna(0)
    
    # If the interval is not daily, resample the data.
    # For candlestick charts, we aggregate: open is the first, high is the max,
    # low is the min, close is the last, and volume is summed.
    if interval.lower() != "1d":
        resample_interval = interval.upper()
        data = data.resample(resample_interval, label='right', closed='right').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
    
    # Create a candlestick chart with a white background and classic style
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name=ticker.upper()
    )])
    fig.update_layout(
        title=f"{ticker.upper()} Candlestick Chart ({period}, Interval: {interval})",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )
    return fig

# Example usage:
if __name__ == "__main__":
    ticker = "AAPL"
    
    # Generate and show a line chart for 1 year period
    line_fig = get_stock_graph_function(ticker, period="1y")
    line_fig.show()
    
    # Generate and show a candlestick chart for 1 month period with a daily interval
    candle_fig = get_candlestick_chart(ticker, period="1month", interval='1d')
    candle_fig.show()
