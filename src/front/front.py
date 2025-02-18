from src.database.base import *
from src.database.market import *
import plotly.graph_objects as go


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

    # Ensure the table exists
    create_market_table(market)

    # Get the last available date in the database
    last_date = get_last_market_date(market)

    # Fetch fresh data if necessary
    if not last_date or last_date < datetime.utcnow().date():
        get_market_data(market, period)

    # Retrieve updated data from the database
    conn = get_db_connection()
    df = pd.read_sql(
        sql.SQL("SELECT * FROM {} ORDER BY date ASC").format(sql.Identifier(market.lower())),
        conn
    )
    conn.close()

    if df.empty:
        return {"error": "No data available."}

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Create a Plotly Candlestick Chart
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Market Data"
    ))

    fig.update_layout(
        title=f"{market.upper()} Market Data ({period})",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )

    return fig.to_json()  # Return the graph in JSON format
