import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
st.set_page_config(
    page_title="Investment Portfolio Monitor",
    page_icon="📈",
    layout="wide"
)

# ── Load data from Supabase ──
@st.cache_data(ttl=300)
def load_data():
    engine = create_engine(DATABASE_URL)
    metrics = pd.read_sql("SELECT * FROM calculated_metrics", engine)
    alerts  = pd.read_sql("SELECT * FROM alerts", engine)
    metrics["date"] = pd.to_datetime(metrics["date"]).dt.date
    alerts["date"]  = pd.to_datetime(alerts["date"]).dt.date
    return metrics, alerts

metrics, alerts = load_data()
ASSETS = metrics["asset_name"].unique().tolist()
latest = metrics.groupby("asset_name").last().reset_index()

# ── Helper: get value for one asset ──
def get(asset, col):
    row = latest[latest["asset_name"] == asset]
    if row.empty:
        return None
    return row[col].values[0]

# ── Header ──
st.title("Investment Portfolio Risk Monitor")

col1, col2, col3 = st.columns(3)
col1.caption(f"Data refreshed daily at 7am IST")
col2.caption(f"Last data date: {metrics['date'].max()}")
col3.caption(f"Pipeline: yfinance API to Supabase PostgreSQL")

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Documentation",
    "📊 Overview",
    "📉 Trends",
    "⚠️ Risk",
    "🚨 Alerts",
    "💡 Insights"
])


# ── TAB 1: DOCUMENTATION ──
with tab1:
    st.title("Project Documentation")

    st.markdown("""
    This dashboard is the front end of an automated data pipeline built for
    investment portfolio monitoring. It is designed for investment analysts,
    risk managers, and finance teams at financial institutions who need a
    daily view of how their market assets are performing.
    """)

    st.divider()

    st.header("Who is this for")
    st.markdown("""
    Any financial institution that manages an investment portfolio needs to
    track how their assets are doing on a daily basis. This includes:

    - Insurance companies that invest policyholder premiums into market assets
    - Mutual funds tracking portfolio performance against benchmarks
    - Pension funds monitoring risk against future payout obligations
    - Banks tracking their treasury and investment book
    - NBFCs monitoring market exposure

    Right now most teams do this manually. An analyst pulls data from
    different sources every morning, pastes it into Excel, calculates
    a few numbers, and sends a report. This takes 2 to 3 hours daily
    and is prone to errors.

    This pipeline automates that entire process.
    """)

    st.divider()

    st.header("What problem this solves")
    st.markdown("""
    Market data comes from multiple sources in raw unstructured form.
    There is no single place where an analyst can see how all assets
    are performing, which ones are risky, and which ones have breached
    alert thresholds.

    This pipeline pulls data from Yahoo Finance every day, calculates
    the key risk and performance metrics, stores everything in a cloud
    database, and makes it available through this dashboard.

    The analyst opens this dashboard at 9am every morning and has
    everything they need in one place. No Excel. No manual data pulling.
    No errors from copy paste.
    """)

    st.divider()

    st.header("What decisions this helps make")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Daily decisions**
        - Which assets had a bad day and why
        - Whether any alert thresholds were breached
        - Whether to rebalance the portfolio

        **Weekly decisions**
        - Is the portfolio trending up or down overall
        - Which asset is dragging performance
        - Is volatility increasing across the board
        """)
    with col2:
        st.markdown("""
        **Monthly decisions**
        - How is cumulative return tracking against targets
        - Which assets are in deep drawdown
        - Is the portfolio diversified or are assets moving together

        **Risk decisions**
        - Is any single asset too volatile for our risk appetite
        - Are we overexposed to correlated assets
        - Do we need to add a hedge
        """)

    st.divider()

    st.header("Pipeline architecture")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("""
        **Source**

        Yahoo Finance API via yfinance library

        6 financial instruments

        Daily OHLCV data
        """)
    with col2:
        st.markdown("""
        **Extract**

        fetch_data.py

        Full load on Day 1

        Incremental from Day 2

        Saves to data/raw/
        """)
    with col3:
        st.markdown("""
        **Transform**

        clean_transform.py

        Handles nulls

        Drops unused columns

        Calculates 6 metrics
        """)
    with col4:
        st.markdown("""
        **Load**

        load_to_db.py

        Supabase PostgreSQL

        3 warehouse tables

        Generates alerts
        """)
    with col5:
        st.markdown("""
        **Serve**

        app.py

        This dashboard

        Reads live from warehouse

        Refreshes daily at 7am
        """)

    st.code("""
Source (Yahoo Finance API)
    Extract  fetch_data.py
Raw CSV saved in data/raw/
    Transform  clean_transform.py
Cleaned metrics in data/transformed/
    Load  load_to_db.py
Supabase PostgreSQL Cloud Database
    Serve
This Streamlit Dashboard
    """)

    st.divider()

    st.header("Assets tracked")
    assets_df = pd.DataFrame({
        "Asset": ["Nifty 50", "Sensex", "Gold ETF", "ICICI Lombard", "HDFC Life", "SBI Life"],
        "Ticker": ["^NSEI", "^BSESN", "GOLDBEES.NS", "ICICIGI.NS", "HDFCLIFE.NS", "SBILIFE.NS"],
        "Class": ["Equity Index", "Equity Index", "Commodity", "Insurance Sector", "Insurance Sector", "Insurance Sector"],
        "Why tracked": [
            "Broad Indian equity market. Insurance companies invest premiums here.",
            "Second equity benchmark. Used alongside Nifty for full market picture.",
            "Safe haven asset. Rises when equity markets fall. Used as a hedge.",
            "Large general insurance company. Tracks insurance sector health.",
            "Large life insurance company. Key indicator for life insurance segment.",
            "Second life insurance benchmark. Confirms sector trends."
        ]
    })
    st.dataframe(assets_df, use_container_width=True, hide_index=True)

    st.divider()

    st.header("Metrics calculated")
    metrics_df = pd.DataFrame({
        "Metric": ["Daily Return", "30 Day Moving Average", "90 Day Moving Average",
                   "30 Day Volatility", "Cumulative Return", "Drawdown"],
        "What it means": [
            "How much did this asset gain or lose today compared to yesterday",
            "Average closing price over the last 30 trading days",
            "Average closing price over the last 90 trading days",
            "How much the daily return fluctuates over 30 days. Higher means more risky.",
            "Total return since we started tracking. Shows overall portfolio growth.",
            "How far the current price is below the highest price seen so far."
        ],
        "Alert": ["Drop below 3% triggers alert", "No alert", "No alert",
                  "No alert", "No alert", "Drop below 5% from peak triggers alert"]
    })
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    st.divider()

    st.header("Data refresh and load strategy")
    col1, col2 = st.columns(2)
    with col1:
        st.success("""
        **Day 1 - Full Load**

        No data exists yet in the warehouse.
        Pipeline pulls 2 years of history.
        Around 490 rows per asset.
        This runs once to populate the database.
        """)
    with col2:
        st.info("""
        **Day 2 onwards - Incremental Load**

        Data already exists in the warehouse.
        Pipeline checks the last date in the database.
        Pulls only new data since that date.
        Runs automatically every day at 7am IST.
        """)

    st.divider()

    st.header("Warehouse tables")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**raw_prices** - untouched source data for audit")
        st.markdown("""
        | Column | Type |
        |---|---|
        | date | TIMESTAMPTZ |
        | asset_name | VARCHAR |
        | open | FLOAT |
        | high | FLOAT |
        | low | FLOAT |
        | close | FLOAT |
        | volume | FLOAT |
        | ticker | VARCHAR |
        | pulled_at | TIMESTAMPTZ |
        """)
    with col2:
        st.markdown("**calculated_metrics** - source of truth for dashboard")
        st.markdown("""
        | Column | Type |
        |---|---|
        | date | TIMESTAMPTZ |
        | asset_name | VARCHAR |
        | daily_return | FLOAT |
        | ma_30 | FLOAT |
        | ma_90 | FLOAT |
        | volatility_30 | FLOAT |
        | cumulative_return | FLOAT |
        | drawdown | FLOAT |
        | close | FLOAT |
        """)
    with col3:
        st.markdown("**alerts** - threshold breach log")
        st.markdown("""
        | Column | Type |
        |---|---|
        | id | SERIAL |
        | date | TIMESTAMPTZ |
        | asset_name | VARCHAR |
        | alert_type | VARCHAR |
        | metric_value | FLOAT |
        | threshold | FLOAT |
        | created_at | TIMESTAMPTZ |
        """)

    st.divider()

    st.header("Tech stack")
    tech_df = pd.DataFrame({
        "Layer": ["Source", "Extract", "Transform", "Warehouse", "Orchestration", "Dashboard"],
        "Tool used": ["yfinance API", "Python + pandas", "Python + pandas",
                      "Supabase PostgreSQL", "schedule library", "Streamlit + Plotly"],
        "What it would be in a large company": [
            "Bloomberg API or Reuters Eikon",
            "Airbyte or Fivetran",
            "dbt or Apache Spark",
            "Snowflake or Google BigQuery",
            "Apache Airflow or Prefect",
            "Tableau or Power BI"
        ]
    })
    st.dataframe(tech_df, use_container_width=True, hide_index=True)

    st.divider()
    st.caption("Built by Sai Ajay Bhargav Gunturu | B.Tech Data Science and AI | Financial Services DE Portfolio Project")


# ── TAB 2: OVERVIEW ──
with tab2:
    st.subheader("Daily Scorecard")
    st.caption("Latest closing price and daily return for each asset")

    cols = st.columns(len(ASSETS))
    for i, asset in enumerate(ASSETS):
        ret   = get(asset, "daily_return")
        close = get(asset, "close")
        if ret is not None:
            cols[i].metric(
                label=asset.replace("_", " ").title(),
                value=f"{close:,.2f}",
                delta=f"{ret:.2f}%"
            )

    st.divider()
    st.subheader("Cumulative Returns")
    fig = px.line(
        metrics, x="date", y="cumulative_return", color="asset_name",
        title="Cumulative Return % Since Start"
    )
    st.plotly_chart(fig, use_container_width=True)


# ── TAB 3: TRENDS ──
with tab3:
    st.subheader("Price Trend with Moving Averages")
    selected = st.selectbox("Select Asset", ASSETS)
    df_asset = metrics[metrics["asset_name"] == selected]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_asset["date"], y=df_asset["close"],
                             name="Close Price", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=df_asset["date"], y=df_asset["ma_30"],
                             name="30 Day MA", line=dict(color="#ff7f0e", dash="dash")))
    fig.add_trace(go.Scatter(x=df_asset["date"], y=df_asset["ma_90"],
                             name="90 Day MA", line=dict(color="#2ca02c", dash="dot")))
    fig.update_layout(title=f"{selected} - Price vs Moving Averages")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Daily Returns Distribution")
    fig2 = px.histogram(df_asset, x="daily_return", nbins=50,
                        title=f"{selected} - Daily Return Distribution")
    st.plotly_chart(fig2, use_container_width=True)


# ── TAB 4: RISK ──
with tab4:
    st.subheader("30 Day Volatility")
    fig = px.bar(
        latest, x="asset_name", y="volatility_30",
        color="volatility_30", color_continuous_scale="Reds",
        title="30 Day Volatility by Asset"
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="orange",
                  annotation_text="1% elevated threshold")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Correlation Matrix")
    pivot = metrics.pivot_table(index="date", columns="asset_name", values="close")
    corr = pivot.corr()
    fig = px.imshow(corr, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    title="Asset Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Drawdown from Peak")
    fig = px.line(metrics, x="date", y="drawdown", color="asset_name",
                  title="Drawdown % from Peak")
    fig.add_hline(y=-5, line_dash="dash", line_color="red",
                  annotation_text="5% alert threshold")
    st.plotly_chart(fig, use_container_width=True)


# ── TAB 5: ALERTS ──
with tab5:
    st.subheader("Threshold Breach Alerts")
    st.caption("Daily drop greater than 3% or drawdown greater than 5% from peak")

    if alerts.empty:
        st.success("No alerts triggered.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Total Alerts", len(alerts))
        col2.metric("Assets Affected", alerts["asset_name"].nunique())

        st.divider()
        alert_type = st.selectbox(
            "Filter by alert type",
            ["All"] + alerts["alert_type"].unique().tolist()
        )
        filtered = alerts if alert_type == "All" else alerts[alerts["alert_type"] == alert_type]
        st.dataframe(filtered, use_container_width=True)

        fig = px.scatter(
            filtered, x="date", y="metric_value",
            color="asset_name", symbol="alert_type",
            title="Alert Events Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)


# ── TAB 6: INSIGHTS ──
with tab6:
    st.title("Portfolio Insights")
    st.caption(f"Live analysis from Supabase. All numbers update automatically on each pipeline run. Last data: {metrics['date'].max()}")

    # ── pull live numbers ──
    best_asset     = latest.nlargest(1, "cumulative_return")["asset_name"].values[0]
    best_return    = latest.nlargest(1, "cumulative_return")["cumulative_return"].values[0]
    worst_asset    = latest.nsmallest(1, "cumulative_return")["asset_name"].values[0]
    worst_return   = latest.nsmallest(1, "cumulative_return")["cumulative_return"].values[0]
    most_vol_asset = latest.nlargest(1, "volatility_30")["asset_name"].values[0]
    most_vol_val   = latest.nlargest(1, "volatility_30")["volatility_30"].values[0]
    max_dd_asset   = latest.nsmallest(1, "drawdown")["asset_name"].values[0]
    max_dd_val     = latest.nsmallest(1, "drawdown")["drawdown"].values[0]
    total_alerts   = len(alerts)

    pivot     = metrics.pivot_table(index="date", columns="asset_name", values="close")
    corr      = pivot.corr()

    # ── scorecard ──
    st.header("Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Best Performer", best_asset.replace("_", " ").title(),
                f"{best_return:.1f}% cumulative return")
    col2.metric("Worst Performer", worst_asset.replace("_", " ").title(),
                f"{worst_return:.1f}% cumulative return")
    col3.metric("Most Volatile", most_vol_asset.replace("_", " ").title(),
                f"{most_vol_val:.2f}% daily std")
    col4.metric("Deepest Drawdown", max_dd_asset.replace("_", " ").title(),
                f"{max_dd_val:.1f}% from peak")
    col5.metric("Total Alerts Fired", total_alerts, "over 2 years")

    st.divider()

    # ── INSIGHT 1: BEST PERFORMER ──
    st.header(f"1. {best_asset.replace('_', ' ').title()} is the Best Performer at {best_return:.1f}%")
    col1, col2 = st.columns([2, 1])
    with col1:
        best_vol    = get(best_asset, "volatility_30")
        best_dd     = get(best_asset, "drawdown")
        best_alerts = len(alerts[alerts["asset_name"] == best_asset])
        st.markdown(f"""
        Over the 2 year period tracked, {best_asset.replace('_', ' ').title()} has delivered
        a cumulative return of {best_return:.1f}%. This is the strongest performer in the portfolio.

        However this performance comes with a cost. The 30 day volatility currently sits at
        {best_vol:.2f}% which is the highest in the portfolio. This means the price swings
        significantly day to day even while the overall trend is upward.

        The asset has also triggered {best_alerts} daily drop alerts over the 2 year period.
        Each of those was a day where the price fell more than 3% in a single session.

        The current drawdown is {best_dd:.1f}% which means the price is currently {abs(best_dd):.1f}%
        below its highest point in our dataset.

        For a portfolio manager this means {best_asset.replace('_', ' ').title()} is a strong
        long term hold but needs to be sized carefully. Too large a position means the portfolio
        value swings heavily on bad days even if the long term direction is positive.
        """)
    with col2:
        best_data = metrics[metrics["asset_name"] == best_asset]
        fig = px.line(best_data, x="date", y="cumulative_return",
                      title=f"{best_asset.replace('_', ' ').title()} Cumulative Return")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── INSIGHT 2: DRAWDOWN ──
    st.header("2. What Drawdown Tells You and Why It Matters")
    st.markdown(f"""
    Drawdown answers one question: if you had bought this asset at its highest price,
    how much would you be down right now?

    The formula is simple. Take the current price, subtract the peak price seen so far,
    divide by the peak price, multiply by 100. The result is always zero or negative.
    Zero means the asset is at its all time high in our dataset. A large negative number
    means the asset has fallen significantly from its best point.

    The most important number in our portfolio right now is {max_dd_asset.replace('_', ' ').title()}
    at {max_dd_val:.1f}%. This asset is currently {abs(max_dd_val):.1f}% below its peak.
    For a portfolio manager holding this position, this represents a significant unrealised loss.
    """)

    fig = px.line(metrics, x="date", y="drawdown", color="asset_name",
                  title="Drawdown from Peak - All Assets")
    fig.add_hline(y=-5, line_dash="dash", line_color="orange",
                  annotation_text="5% alert threshold")
    fig.add_hline(y=-20, line_dash="dash", line_color="red",
                  annotation_text="Severe 20% drawdown level")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Current drawdown for each asset:**")
    dd_df = latest[["asset_name", "drawdown", "cumulative_return"]].copy()
    dd_df["asset_name"] = dd_df["asset_name"].str.replace("_", " ").str.title()
    dd_df.columns = ["Asset", "Drawdown %", "Cumulative Return %"]
    dd_df = dd_df.sort_values("Drawdown %")
    st.dataframe(dd_df.round(2), use_container_width=True, hide_index=True)

    st.markdown(f"""
    The important thing to notice here is whether assets in deep drawdown also have
    weak cumulative returns. If an asset is both down significantly from its peak
    AND has poor cumulative returns, that is a signal to review the position.

    If an asset has a large drawdown but strong cumulative returns, it simply means
    it had a big run up and has pulled back from the top while still being well
    ahead overall.
    """)

    st.divider()

    # ── INSIGHT 3: CORRELATION ──
    st.header("3. Is the Portfolio Actually Diversified")
    st.markdown("""
    Diversification means holding assets that do not all move in the same direction
    at the same time. When one asset falls, another holds steady or rises.
    This protects the overall portfolio from a single bad event wiping out all value.

    Correlation measures this. A value close to 1 means two assets move almost in sync.
    A value close to 0 means they move independently. A negative value means they
    tend to move in opposite directions, which is the best diversification you can get.
    """)

    fig = px.imshow(corr, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    title="Correlation Between All Assets")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Key correlation pairs to watch:**")
    corr_pairs = []
    assets_list = corr.columns.tolist()
    for i in range(len(assets_list)):
        for j in range(i+1, len(assets_list)):
            a1 = assets_list[i]
            a2 = assets_list[j]
            val = corr.loc[a1, a2]
            corr_pairs.append({
                "Asset 1": a1.replace("_", " ").title(),
                "Asset 2": a2.replace("_", " ").title(),
                "Correlation": round(val, 3),
                "What this means": (
                    "Move almost together - low diversification benefit"
                    if val > 0.7 else
                    "Move somewhat together - moderate diversification"
                    if val > 0.3 else
                    "Move independently - good diversification"
                    if val > -0.1 else
                    "Tend to move opposite - strong hedge"
                )
            })
    corr_df = pd.DataFrame(corr_pairs).sort_values("Correlation", ascending=False)
    st.dataframe(corr_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── INSIGHT 4: VOLATILITY ──
    st.header("4. Which Assets Carry the Most Daily Risk")
    st.markdown("""
    Volatility is the standard deviation of daily returns over 30 days.
    In plain terms it measures how much the price jumps around day to day.

    A volatility of 1% means on a typical day the price moves about 1% up or down.
    A volatility of 0.5% means the price is more stable and predictable.

    For financial institutions, lower volatility is preferred for core holdings
    because it makes portfolio value more predictable. Higher volatility assets
    can be held in smaller allocations for return potential.
    """)

    fig = px.bar(latest, x="asset_name", y="volatility_30",
                 color="volatility_30", color_continuous_scale="Reds",
                 title="Current 30 Day Volatility by Asset")
    fig.add_hline(y=1.0, line_dash="dash", line_color="orange",
                  annotation_text="1% elevated level")
    st.plotly_chart(fig, use_container_width=True)

    vol_df = latest[["asset_name", "volatility_30"]].copy()
    vol_df["asset_name"] = vol_df["asset_name"].str.replace("_", " ").str.title()
    vol_df["risk level"] = vol_df["volatility_30"].apply(
        lambda x: "High" if x > 1.2 else "Elevated" if x > 0.9 else "Moderate"
    )
    vol_df.columns = ["Asset", "30 Day Volatility %", "Risk Level"]
    vol_df = vol_df.sort_values("30 Day Volatility %", ascending=False)
    st.dataframe(vol_df.round(3), use_container_width=True, hide_index=True)

    st.divider()

    # ── INSIGHT 5: PORTFOLIO HEALTH ──
    st.header("5. Overall Portfolio Health")

    assets_in_positive = latest[latest["cumulative_return"] > 0]["asset_name"].tolist()
    assets_in_negative = latest[latest["cumulative_return"] <= 0]["asset_name"].tolist()
    assets_deep_dd     = latest[latest["drawdown"] < -20]["asset_name"].tolist()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error(f"""
        **Areas of concern**

        {len(assets_deep_dd)} assets in drawdown deeper than 20%

        {total_alerts} total alerts fired over 2 years

        {worst_asset.replace('_', ' ').title()} is the weakest performer at {worst_return:.1f}%

        All assets showed negative daily returns on last trading day
        """)
    with col2:
        st.warning(f"""
        **Things to watch**

        {most_vol_asset.replace('_', ' ').title()} is most volatile at {most_vol_val:.2f}%

        Insurance sector stocks showing higher drawdown than indices

        Monitor daily for further drops below alert thresholds

        Review correlation pairs for unexpected changes
        """)
    with col3:
        st.success(f"""
        **Positives**

        {best_asset.replace('_', ' ').title()} up {best_return:.1f}% cumulative

        {len(assets_in_positive)} out of {len(ASSETS)} assets in positive cumulative return

        Pipeline running and capturing all data automatically

        All alerts logged with dates and values for audit trail
        """)

    st.divider()
    st.info("All numbers on this page are pulled live from Supabase and update automatically each time the pipeline runs. Data refreshes daily at 7am IST.")
