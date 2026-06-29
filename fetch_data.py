import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# ── Configuration ──
RAW_DATA_PATH = "data/raw/"
os.makedirs(RAW_DATA_PATH, exist_ok=True)

# ── Assets we are tracking ──
TICKERS = {
    "^NSEI":       "nifty50",
    "^BSESN":      "sensex",
    "GOLDBEES.NS": "gold",
    "ICICIGI.NS":  "icici_lombard",
    "HDFCLIFE.NS": "hdfc_life",
    "SBILIFE.NS":  "sbi_life"
}

# ── How far back on first run ──
INITIAL_LOOKBACK_YEARS = 2

def get_start_date(asset_name):
    """
    Check if we already have data for this asset.
    If yes  — return yesterday (incremental load)
    If no   — return 2 years ago (full load)
    """
    file_path = f"{RAW_DATA_PATH}{asset_name}_raw.csv"
    
    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path, index_col=0, parse_dates=True)
        last_date = existing_data.index.max()
        print(f"  Existing data found for {asset_name}. Last date: {last_date.date()}")
        return last_date + timedelta(days=1)
    else:
        start = datetime.today() - timedelta(days=365 * INITIAL_LOOKBACK_YEARS)
        print(f"  No existing data for {asset_name}. Full load from {start.date()}")
        return start

def fetch_asset_data(ticker, asset_name):
    """
    Pull data for one asset from yfinance API.
    Handles both full load and incremental load.
    """
    start_date = get_start_date(asset_name)
    end_date   = datetime.today()

    print(f"  Fetching {asset_name} from {start_date.date()} to {end_date.date()}...")

    stock = yf.Ticker(ticker)
    df    = stock.history(start=start_date, end=end_date)

    if df.empty:
        print(f"  No new data for {asset_name}. Already up to date.")
        return

    # ── Add metadata columns ──
    df["asset_name"]  = asset_name
    df["ticker"]      = ticker
    df["pulled_at"]   = datetime.now()

    # ── Append or create ──
    file_path = f"{RAW_DATA_PATH}{asset_name}_raw.csv"

    if os.path.exists(file_path):
        existing = pd.read_csv(file_path, index_col=0, parse_dates=True)
        df       = pd.concat([existing, df])
        df       = df[~df.index.duplicated(keep="last")]

    df.to_csv(file_path)
    print(f"  Saved {asset_name}_raw.csv — {len(df)} total rows")

def fetch_all_assets():
    print(f"\n{'='*50}")
    print(f"Extract started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    for ticker, asset_name in TICKERS.items():
        print(f"Processing {asset_name}...")
        fetch_asset_data(ticker, asset_name)
        print()

    print("Extract complete.\n")

if __name__ == "__main__":
    fetch_all_assets()



