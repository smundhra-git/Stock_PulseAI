import pandas as pd
import numpy as np
import os
import urllib.parse
import sqlalchemy
from dotenv import load_dotenv
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb

# Define the regression features we want to use.
REGRESSION_FEATURES = ['open', 'close', 'high', 'low', 'volume', 'volatility']

# ---------------------------
# Environment & DB Connection
# ---------------------------
load_dotenv()
password_encoded = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{password_encoded}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
engine = sqlalchemy.create_engine(DB_URL)


# ---------------------------
# Data Fetching
# ---------------------------
def fetch_stock_data(ticker: str):
    """
    Fetch stock data for the given ticker from the database table.
    The table name is assumed to be the lowercase ticker.
    """
    query = f"SELECT * FROM {ticker.lower()} ORDER BY date ASC"
    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            print(f"❌ No data found for {ticker}")
            return None
        return df
    except Exception as e:
        print(f"⚠️ Error fetching data for {ticker}: {e}")
        return None


# ---------------------------
# Feature Engineering & Preprocessing
# ---------------------------
def preprocess_stock_data(df: pd.DataFrame):
    """
    Preprocess the stock data by:
      - Converting column names to lowercase.
      - Converting the 'date' column to datetime.
      - Creating time-based features.
      - Computing the target variables for forecasting 1-day, 30-day, and 1-year ahead.
      
    The regression models will use only the following features:
         [open, close, high, low, volume, volatility]
    (Here, volatility is defined as high - low.)
    
    Additionally, we compute sma_20 and sma_50 for later adjustment.
    
    Returns:
        X       : DataFrame of regression features (6 columns).
        y_1d    : Series for 1-day ahead target (next day's close).
        y_1m    : Series for 30-day ahead target.
        y_1y    : Series for 1-year ahead target.
        df_full : The full processed DataFrame (including SMA columns) for later adjustment.
    """
    # Convert all column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # --- Check if enough rows exist for a 1-year target ---
    # Shifting by -252 requires at least 253 rows.
    if len(df) < 253:
        print(f"❌ Not enough data for 1-year prediction. Required at least 253 rows, got {len(df)} rows.")
        return None, None, None, None, None
    
    # Create time-based features (for information only)
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    # Compute price change and volatility (volatility = high - low)
    df['price_change'] = df['close'].pct_change()
    df['volatility'] = df['high'] - df['low']
    
    # ----------------------------
    # Compute Additional Indicators for Adjustment
    # ----------------------------
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # ----------------------------
    # Create Target Variables
    # ----------------------------
    df['future_1d'] = df['close'].shift(-1)
    df['future_1m'] = df['close'].shift(-30)
    df['future_1y'] = df['close'].shift(-252)
    
    # Save targets separately
    targets = df[['future_1d', 'future_1m', 'future_1y']]
    
    # ----------------------------
    # Regression Features
    # ----------------------------
    # We use only the specified features.
    df[REGRESSION_FEATURES] = df[REGRESSION_FEATURES].ffill().bfill()
    
    # Drop rows where any target is NaN (typically the last rows)
    df.dropna(subset=['future_1d', 'future_1m', 'future_1y'], inplace=True)
    
    if df.empty:
        print("❌ Processed DataFrame is empty after dropping NaNs!")
        return None, None, None, None, None
    
    X = df[REGRESSION_FEATURES]
    y_1d = df['future_1d']
    y_1m = df['future_1m']
    y_1y = df['future_1y']
    
    return X, y_1d, y_1m, y_1y, df


# ---------------------------
# Regression Modeling & Prediction
# ---------------------------
def train_and_predict(X, y, horizon_label: str):
    """
    Trains multiple regression models on features X and target y,
    then averages their predictions to generate a forecast.
    
    For linear models, we print the regression formula in the form:
      y = intercept + coef1 * open + coef2 * close + ... + coef6 * volatility
    
    Parameters:
        X             : DataFrame of regression features.
        y             : Series of target values.
        horizon_label : Label for the forecast horizon (e.g., '1d', '30d', '1y').
    
    Returns:
        final_prediction : The averaged prediction across all models.
    """
    if X is None or y is None or X.empty or y.empty:
        print(f"❌ No valid data for training ({horizon_label})")
        return None
    
    # Use train/test split if sufficient data exists.
    if len(X) < 10:
        print(f"⚠️ Too few data points for splitting. Using entire dataset ({horizon_label})")
        X_train, y_train = X, y
        X_test, y_test = X, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define our regression models.
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=10),
        "Lasso Regression": Lasso(alpha=0.01, max_iter=10000),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, learning_rate=0.1),
        "XGBoost": xgb.XGBRegressor(objective='reg:squarederror', n_estimators=300, learning_rate=0.05)
    }
    
    model_predictions = []
    
    for name, model in models.items():
        try:
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
            # Use the prediction for the last test sample as representative.
            pred_value = preds[-1]
            model_predictions.append(pred_value)
            
            mse = mean_squared_error(y_test, preds)
            r2 = r2_score(y_test, preds)
            print(f"{name} ({horizon_label}): RMSE = {round(np.sqrt(mse), 2)}, R² = {round(r2, 3)} | Last Prediction = {round(pred_value, 2)}")
            
            # If the model is linear, extract and print the regression formula.
            if hasattr(model, 'coef_'):
                # Since we trained on scaled data, we convert coefficients to the original scale.
                effective_coefs = model.coef_ / scaler.scale_
                effective_intercept = model.intercept_ - np.sum(model.coef_ * scaler.mean_ / scaler.scale_)
                formula = f"y = {effective_intercept:.2f}"
                for feat, coef in zip(REGRESSION_FEATURES, effective_coefs):
                    formula += f" + ({coef:.2f} * {feat})"
                print(f"Regression formula for {name} ({horizon_label}): {formula}")
            
        except Exception as e:
            print(f"❌ Error training {name} for {horizon_label}: {e}")
    
    if model_predictions:
        final_prediction = np.mean(model_predictions)
        print(f"✅ Final Averaged Prediction ({horizon_label}): {round(final_prediction, 2)}\n")
        return final_prediction
    else:
        print("❌ No predictions available.")
        return None


# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    ticker = "AAPL"
    df_raw = fetch_stock_data(ticker)
    
    if df_raw is not None:
        X, y_1d, y_1m, y_1y, df_proc = preprocess_stock_data(df_raw)
        
        if X is not None and df_proc is not None:
            print("\n📈 Predicting stock prices for 1 day ahead...")
            pred_1d = train_and_predict(X, y_1d, "1d")
            
            print("📈 Predicting stock prices for 30 days ahead...")
            pred_30d = train_and_predict(X, y_1m, "30d")
            
            print("📈 Predicting stock prices for 1 year ahead...")
            pred_1y = train_and_predict(X, y_1y, "1y")
            
            # ---------------------------
            # Adjustment Based on Moving Averages
            # ---------------------------
            # Use the last row's SMA values for directional adjustment.
            last_row = df_proc.iloc[-1]
            last_close = last_row['close']
            sma_20 = last_row['sma_20']
            sma_50 = last_row['sma_50']
            
            # For a 1-day prediction, adjust using sma_20; for 30-day, use sma_50.
            adjustment_1d = 0.1 * (last_close - sma_20)  # Weight (0.1) can be tuned
            adjustment_30d = 0.1 * (last_close - sma_50)
            
            final_pred_1d = pred_1d + adjustment_1d if pred_1d is not None else None
            final_pred_30d = pred_30d + adjustment_30d if pred_30d is not None else None
            final_pred_1y = pred_1y  # No adjustment for 1-year forecast
            
            print("========================================")
            print(f"Raw Regression Prediction (1d): {pred_1d:.2f}")
            print(f"sma_20: {sma_20:.2f} | Last Close: {last_close:.2f} | Adjustment (1d): {adjustment_1d:.2f}")
            print(f"Final 1d Prediction: {final_pred_1d:.2f}\n")
            
            print(f"Raw Regression Prediction (30d): {pred_30d:.2f}")
            print(f"sma_50: {sma_50:.2f} | Last Close: {last_close:.2f} | Adjustment (30d): {adjustment_30d:.2f}")
            print(f"Final 30d Prediction: {final_pred_30d:.2f}\n")
            
            print(f"Final 1y Prediction (no moving average adjustment): {final_pred_1y:.2f}")
