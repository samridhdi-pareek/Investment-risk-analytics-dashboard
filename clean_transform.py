import pandas as pd
import numpy as np
import os
from datetime import datetime

RAW_DATA_PATH = "data/raw/"
TRANSFORMED_DATA_PATH = "data/transformed/"
os.makedirs(TRANSFORMED_DATA_PATH, exist_ok=True)

ASSETS = [
    "nifty50",
    "sensex", 
    "gold",
    "icici_lombard",
    "hdfc_life",
    "sbi_life"
]

def read_raw_data(asset_name):
    """Read raw CSV for one asset"""
    file_path = f"{RAW_DATA_PATH}{asset_name}_raw.csv"
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    df.index.name = "date"
    return df

def clean_data(df, asset_name):
    """
    Clean raw data:
    - Drop unneeded columns
    - Handle nulls
    - Fix data types
    """
    # Drop columns not needed for analysis
    cols_to_drop = ["Dividends", "Stock Splits"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Forward fill nulls — if market closed, carry previous day price
    df = df.ffill()

    # Drop any remaining nulls at start of series
    df = df.dropna()

    # Ensure numeric columns are float
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"  Cleaned {asset_name} — {len(df)} rows, {df.shape[1]} columns")
    return df

def calculate_metrics(df, asset_name):
    """
    Calculate all business-required metrics from Close price
    """
    metrics = pd.DataFrame(index=df.index)
    metrics["asset_name"] = asset_name

    # Daily return — % change from previous day
    metrics["daily_return"] = df["Close"].pct_change() * 100

    # 30 day moving average
    metrics["ma_30"] = df["Close"].rolling(window=30).mean()

    # 90 day moving average
    metrics["ma_90"] = df["Close"].rolling(window=90).mean()

    # Volatility — 30 day rolling standard deviation of daily returns
    metrics["volatility_30"] = metrics["daily_return"].rolling(window=30).std()

    # Cumulative return — total return from first date
    metrics["cumulative_return"] = (
        (df["Close"] / df["Close"].iloc[0]) - 1
    ) * 100

    # Drawdown — how far below the rolling peak
    rolling_max = df["Close"].cummax()
    metrics["drawdown"] = ((df["Close"] - rolling_max) / rolling_max) * 100

    # Close price — needed for correlation and charts
    metrics["close"] = df["Close"]

    # Drop rows where metrics could not be calculated
    metrics = metrics.dropna(subset=["daily_return"])

    print(f"  Calculated metrics for {asset_name} — {len(metrics)} rows")
    return metrics

def run_transform():
    print(f"\n{'='*50}")
    print(f"Transform started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    all_clean = []
    all_metrics = []

    for asset_name in ASSETS:
        print(f"Processing {asset_name}...")

        # Read
        df = read_raw_data(asset_name)

        # Clean
        df_clean = clean_data(df, asset_name)

        # Calculate metrics
        df_metrics = calculate_metrics(df_clean, asset_name)

        all_clean.append(df_clean)
        all_metrics.append(df_metrics)
        print()

    # Combine all assets into one table
    combined_clean = pd.concat(all_clean, keys=ASSETS)
    combined_metrics = pd.concat(all_metrics)

    # Save
    combined_clean.to_csv(f"{TRANSFORMED_DATA_PATH}clean_prices.csv")
    combined_metrics.to_csv(f"{TRANSFORMED_DATA_PATH}calculated_metrics.csv")

    print(f"Saved clean_prices.csv — {len(combined_clean)} total rows")
    print(f"Saved calculated_metrics.csv — {len(combined_metrics)} total rows")
    print(f"\nTransform complete.\n")

if __name__ == "__main__":
    run_transform()