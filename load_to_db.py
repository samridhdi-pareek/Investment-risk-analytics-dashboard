import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
TRANSFORMED_DATA_PATH = "data/transformed/"

def get_engine():
    engine = create_engine(DATABASE_URL)
    return engine

def create_tables(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_prices (
                date            TIMESTAMPTZ,
                asset_name      VARCHAR(50),
                open            FLOAT,
                high            FLOAT,
                low             FLOAT,
                close           FLOAT,
                volume          FLOAT,
                ticker          VARCHAR(20),
                pulled_at       TIMESTAMPTZ,
                PRIMARY KEY (date, asset_name)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS calculated_metrics (
                date                TIMESTAMPTZ,
                asset_name          VARCHAR(50),
                daily_return        FLOAT,
                ma_30               FLOAT,
                ma_90               FLOAT,
                volatility_30       FLOAT,
                cumulative_return   FLOAT,
                drawdown            FLOAT,
                close               FLOAT,
                PRIMARY KEY (date, asset_name)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alerts (
                id              SERIAL PRIMARY KEY,
                date            TIMESTAMPTZ,
                asset_name      VARCHAR(50),
                alert_type      VARCHAR(50),
                metric_value    FLOAT,
                threshold       FLOAT,
                created_at      TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.commit()
        print("  Tables created successfully")

def load_clean_prices(engine):
    df = pd.read_csv(
        f"{TRANSFORMED_DATA_PATH}clean_prices.csv",
        parse_dates=True
    )
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df.to_sql(
        "raw_prices",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=500
    )
    print(f"  Loaded raw_prices — {len(df)} rows")

def load_calculated_metrics(engine):
    df = pd.read_csv(
        f"{TRANSFORMED_DATA_PATH}calculated_metrics.csv",
        parse_dates=True
    )
    df.to_sql(
        "calculated_metrics",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=500
    )
    print(f"  Loaded calculated_metrics — {len(df)} rows")

def generate_alerts(engine):
    df = pd.read_csv(f"{TRANSFORMED_DATA_PATH}calculated_metrics.csv")
    alerts = []

    drop_alerts = df[df["daily_return"] < -3][
        ["date", "asset_name", "daily_return"]
    ].copy()
    drop_alerts["alert_type"] = "daily_drop"
    drop_alerts["metric_value"] = drop_alerts["daily_return"]
    drop_alerts["threshold"] = -3
    alerts.append(drop_alerts)

    drawdown_alerts = df[df["drawdown"] < -5][
        ["date", "asset_name", "drawdown"]
    ].copy()
    drawdown_alerts["alert_type"] = "drawdown"
    drawdown_alerts["metric_value"] = drawdown_alerts["drawdown"]
    drawdown_alerts["threshold"] = -5
    alerts.append(drawdown_alerts)

    if alerts:
        combined_alerts = pd.concat(alerts)
        combined_alerts = combined_alerts[
            ["date", "asset_name", "alert_type", "metric_value", "threshold"]
        ]
        combined_alerts.to_sql(
            "alerts",
            engine,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=500
        )
        print(f"  Generated {len(combined_alerts)} alerts")

def run_load():
    print(f"\n{'='*50}")
    print(f"Load started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    engine = get_engine()

    print("Creating tables...")
    create_tables(engine)
    print()

    print("Loading clean prices...")
    load_clean_prices(engine)
    print()

    print("Loading calculated metrics...")
    load_calculated_metrics(engine)
    print()

    print("Generating alerts...")
    generate_alerts(engine)
    print()

    print("Load complete.\n")

if __name__ == "__main__":
    run_load()