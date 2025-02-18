from src.database.base import *


def get_last_date(ticker: str):
    """
    Returns the latest date available in the table for the given ticker.
    If no data exists, returns None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("SELECT MAX(date) FROM {}").format(sql.Identifier(ticker.lower()))
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result


#create stock table, this will be the schema
def create_stock_table(ticker: str):
    """Creates a stock-specific table with all required technical indicators if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            date DATE PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT
        );
    """).format(sql.Identifier(ticker.lower()))
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


#delete stock data
def delete_stock_table(ticker: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("DROP TABLE {ticker}").format(sql.Identifier(ticker.lower()))
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()



def get_latest_stock_data(ticker: str, window: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sql.SQL("""
        SELECT date, open, high, low, close, volume
        FROM {} 
        ORDER BY date DESC 
        LIMIT %s;
    """).format(sql.Identifier(ticker.lower()))

    cursor.execute(query, (window,))
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])

    # ✅ Ensure all columns are lowercase and have no spaces
    df.columns = df.columns.str.strip().str.lower()

    return df.sort_values(by="date")


