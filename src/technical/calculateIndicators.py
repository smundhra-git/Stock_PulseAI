import psycopg2
import pandas as pd
from psycopg2 import sql
from src.database.db_operations import *

def calculate_latest_sma(df: pd.DataFrame, window: int):
    """
    Calculate the latest SMA (Simple Moving Average) for the last `window` days.
    """
    return df["close"].rolling(window=window).mean().iloc[-1]  # Latest SMA value

def calculate_latest_ema(df: pd.DataFrame, window: int):
    """
    Calculate the latest EMA (Exponential Moving Average) for the last `window` days
    using the correct formula EMA_t = P_t * alpha + EMA_(t-1) * (1 - alpha). --> Investopedia
    """
    alpha = 2 / (window + 1)  # Smoothing factor

    ema = df["close"].iloc[0]  # Initialize EMA with the first closing price

    for price in df["close"][1:]:
        ema = (price * alpha) + (ema * (1 - alpha))  # Apply EMA formula iteratively

    return ema  # Return the most recent EMA value

def calculate_MACD(df: pd.DataFrame):
    return calculate_latest_ema(df, 12) - calculate_latest_ema(df, 26)

def calculate_rsi(df: pd.DataFrame, window: int = 14):
    """
    Calculate the Relative Strength Index (RSI) for the last `window` days.

    RSI = 100 - (100 / (1 + RS))
    where RS = (Average Gain / Average Loss)
    """
    if "close" not in df.columns:
        raise KeyError("Missing required column: 'close'")

    # Calculate price differences
    df["price_change"] = df["close"].diff()

    # Separate gains and losses
    df["gain"] = df["price_change"].apply(lambda x: x if x > 0 else 0)
    df["loss"] = df["price_change"].apply(lambda x: -x if x < 0 else 0)

    # Compute rolling average of gains and losses
    avg_gain = df["gain"].rolling(window=window, min_periods=window).mean()
    avg_loss = df["loss"].rolling(window=window, min_periods=window).mean()

    # Compute RS and RSI
    df["rs"] = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + df["rs"]))

    return df[["date", "close", "rsi"]].iloc[-1]  # Return the latest RSI value

def calculate_stochastic_oscillator(df: pd.DataFrame, window: int = 14):
    """
    Calculate the %K value of the Stochastic Oscillator for the last `window` periods.
    """
    
    df["highest_high"] = df["high"].rolling(window=window).max()
    df["lowest_low"] = df["low"].rolling(window=window).min()

    df["stochastic_%K"] = ((df["close"] - df["lowest_low"]) / 
                            (df["highest_high"] - df["lowest_low"])) * 100

    return df[["date", "close", "stochastic_%K"]].iloc[-1]

def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20):
    """
    Calculate Bollinger Bands (Upper Band, Lower Band) for the last `window` days.

    Upper Band = SMA + (2 * sd)
    Lower Band = SMA - (2 * sd)
    """
    if len(df) < window:
        raise ValueError("Not enough data to calculate Bollinger Bands")

    # Calculate SMA (Middle Band)
    df["sma"] = df["close"].rolling(window=window).mean()

    # Calculate Standard Deviation
    df["std_dev"] = df["close"].rolling(window=window).std()

    # Compute Upper & Lower Bands
    df["upper_band"] = df["sma"] + (2 * df["std_dev"])
    df["lower_band"] = df["sma"] - (2 * df["std_dev"])

    return df[["date", "close", "sma", "upper_band", "lower_band"]].iloc[-1]  # Return the latest values


def calculate_vwap(df: pd.DataFrame):
    """
    Calculate the Volume Weighted Average Price (VWAP) for the last available date.

    VWAP = SUM(P_t * V_t) / SUM(V_t)
    where P_t = (high + low + close) / 3
    """
    if "high" not in df.columns or "low" not in df.columns or "close" not in df.columns or "volume" not in df.columns:
        raise KeyError("Missing required columns: ['high', 'low', 'close', 'volume']")

    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (df["typical_price"] * df["volume"]).cumsum() / df["volume"].cumsum()

    return df[["date", "close", "vwap"]].iloc[-1]  # Return the latest VWAP value

def calculate_obv(df: pd.DataFrame):
    """
    Calculate On-Balance Volume (OBV) for the last available date.
    
    OBV = OBV_prev + 
          V  (if P_t > P_t-1)
         -V  (if P_t < P_t-1)
          0  (if P_t = P_t-1)
    """
    if "close" not in df.columns or "volume" not in df.columns:
        raise KeyError("Missing required columns: ['close', 'volume']")

    df["obv"] = 0  # Initialize OBV column
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i - 1]:
            df.loc[df.index[i], "obv"] = df["obv"].iloc[i - 1] + df["volume"].iloc[i]
        elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
            df.loc[df.index[i], "obv"] = df["obv"].iloc[i - 1] - df["volume"].iloc[i]
        else:
            df.loc[df.index[i], "obv"] = df["obv"].iloc[i - 1]

    return df[["date", "close", "obv"]].iloc[-1]  # Return latest OBV value


def calculate_donchian_channel(df: pd.DataFrame, window: int = 20):
    """
    Calculate Donchian Channel (Upper and Lower Bands) for the last `window` days.
    
    Upper Channel = max(Highs over last `window` periods)
    Lower Channel = min(Lows over last `window` periods)
    """
    if "high" not in df.columns or "low" not in df.columns:
        raise KeyError("Missing required columns: ['high', 'low']")

    # Calculate Upper & Lower Channels
    df["upper_channel"] = df["high"].rolling(window=window).max()
    df["lower_channel"] = df["low"].rolling(window=window).min()

    return df[["date", "upper_channel", "lower_channel"]].iloc[-1]  # Return latest values



def calculate_score(df: pd.DataFrame):
    """
    Calculate a score based on multiple technical indicators.
    
    Score Classification:
    - Above 5   → Strong Buy
    - 2 to 5    → Buy
    - -2 to 2   → Hold
    - -5 to -2  → Sell
    - Below -5  → Strong Sell
    """

    score = 0  # Initialize score
    
    # 1. **Moving Averages: Golden Cross / Death Cross**
    if calculate_latest_sma(df, 50) > calculate_latest_sma(df, 200):
        score += 1  # Golden Cross (Bullish)
    else:
        score -= 1  # Death Cross (Bearish)

    if calculate_latest_ema(df, 50) > calculate_latest_ema(df, 200):
        score += 1  # EMA Bullish Signal
    else:
        score -= 1  # EMA Bearish Signal

    # 2. **MACD & Signal Line**
    macd = calculate_MACD(df)
    signal_line = calculate_latest_ema(df, 9)  # Signal Line (9-day EMA of MACD)
    
    if macd > signal_line:
        score += 1  # Bullish MACD Crossover
    else:
        score -= 1  # Bearish MACD Crossover

    # 3. **RSI (Overbought / Oversold Conditions)**
    rsi = calculate_rsi(df, 14)["rsi"]
    if rsi > 70:
        score -= 1  # Overbought
    elif rsi < 30:
        score += 1  # Oversold

    # 4. **Stochastic Oscillator**
    stochastic = calculate_stochastic_oscillator(df, 14)
    stochastic_signal = calculate_latest_sma(df, 3)  # 3-day SMA of Stochastic

    if stochastic["stochastic_%K"] < 20 and stochastic["stochastic_%K"] > stochastic_signal:
        score += 1  # Bullish Reversal
    elif stochastic["stochastic_%K"] > 80 and stochastic["stochastic_%K"] < stochastic_signal:
        score -= 1  # Bearish Reversal

    # 5. **Bollinger Bands**
    bbands = calculate_bollinger_bands(df, 20)
    if df["close"].iloc[-1] <= bbands["lower_band"]:
        score += 1  # Price is at Lower Band → Oversold
    elif df["close"].iloc[-1] >= bbands["upper_band"]:
        score -= 1  # Price is at Upper Band → Overbought

    # 6. **VWAP (Volume Weighted Average Price)**
    vwap = calculate_vwap(df)
    if df["close"].iloc[-1] < vwap["vwap"]:
        score += 1  # Price below VWAP and moving up → Buy
    else:
        score -= 1  # Price above VWAP and moving down → Sell

    # 7. **On-Balance Volume (OBV)**
    obv = calculate_obv(df)
    if obv["obv"] > df["obv"].iloc[-2]:  # OBV increasing
        score += 1  # Buying Pressure
    else:
        score -= 1  # Selling Pressure

    # 8. **Donchian Channel Breakout**
    donchian = calculate_donchian_channel(df, 20)
    if df["close"].iloc[-1] > donchian["upper_channel"]:
        score += 1  # Breakout above → Bullish
    elif df["close"].iloc[-1] < donchian["lower_channel"]:
        score -= 1  # Breakout below → Bearish

    # **Final Score Classification**
    if score > 5:
        return "Strong Buy", score
    elif 2 <= score <= 5:
        return "Buy", score
    elif -2 <= score <= 2:
        return "Hold", score
    elif -5 <= score < -2:
        return "Sell", score
    else:
        return "Strong Sell", score

