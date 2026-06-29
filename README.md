# Investment Portfolio Risk Monitor

An automated ELT pipeline that pulls daily financial market data, calculates risk metrics, and serves an interactive dashboard for investment portfolio monitoring.

**Live dashboard:** https://investment-portfolio-monitor.streamlit.app

---

## What this is

Financial institutions that manage investment portfolios need a daily view of how their assets are performing. This includes insurance companies investing policyholder premiums, mutual funds tracking performance, pension funds monitoring risk, and banks managing their treasury book.

Right now most teams do this manually. An analyst pulls data from different sources every morning, pastes it into Excel, calculates a few numbers, and sends a report. This takes hours and is prone to errors.

This pipeline automates that entire process. It runs every day at 7am IST, pulls fresh market data, calculates the key risk and performance metrics, stores everything in a cloud database, and makes it available through a live interactive dashboard.

---

## Who this is for

Any financial institution managing an investment portfolio against future obligations:

- Insurance companies investing policyholder premiums
- Mutual funds tracking portfolio performance against benchmarks
- Pension funds monitoring risk against future payout obligations
- Banks tracking treasury and investment books
- NBFCs monitoring market exposure

---

## Pipeline architecture

```
Source
Yahoo Finance API via yfinance library

Extract
fetch_data.py
Pulls daily OHLCV data for 6 assets
Full load on Day 1, incremental from Day 2 onwards
Saves raw CSV files to data/raw/

Transform
clean_transform.py
Handles nulls via forward fill
Drops unused columns
Calculates 6 risk and performance metrics
Saves to data/transformed/

Load
load_to_db.py
Loads 3 structured tables into Supabase PostgreSQL
Generates alerts for threshold breaches
Runs deduplication on every load

Orchestrate
pipeline.py
Runs Extract, Transform, Load in sequence
Scheduled daily at 7am IST
Catches and logs errors without crashing

Serve
dashboard/app.py
Streamlit dashboard with 6 tabs
Reads live from Supabase on every load
Publicly deployed on Streamlit Cloud
```

---

## Assets tracked

| Asset | Ticker | Class | Why tracked |
|---|---|---|---|
| Nifty 50 | ^NSEI | Equity Index | Broad Indian market. Insurance companies invest premiums here. |
| Sensex | ^BSESN | Equity Index | Secondary equity benchmark for full market picture. |
| Gold ETF | GOLDBEES.NS | Commodity | Safe haven asset. Rises when equity markets fall. |
| ICICI Lombard | ICICIGI.NS | Insurance Sector | Large general insurance benchmark. |
| HDFC Life | HDFCLIFE.NS | Insurance Sector | Large life insurance benchmark. |
| SBI Life | SBILIFE.NS | Insurance Sector | Second life insurance benchmark. |

---

## Metrics calculated

| Metric | Formula | Business use | Alert |
|---|---|---|---|
| Daily Return | (today close - yesterday close) / yesterday close x 100 | Daily performance scorecard | Drop below 3% triggers alert |
| 30 Day Moving Average | Rolling 30 day average of close price | Short term trend monitoring | None |
| 90 Day Moving Average | Rolling 90 day average of close price | Long term trend monitoring | None |
| 30 Day Volatility | Rolling 30 day std deviation of daily returns | Risk measurement | None |
| Cumulative Return | (current close / first close - 1) x 100 | Total portfolio growth | None |
| Drawdown | (current close - rolling peak) / rolling peak x 100 | Downside risk from peak | Drop below 5% triggers alert |

---

## Warehouse schema

Three tables in Supabase PostgreSQL:

**raw_prices** - untouched source data, kept for audit trail

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

**calculated_metrics** - source of truth for the dashboard

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

**alerts** - log of all threshold breaches

| Column | Type |
|---|---|
| id | SERIAL |
| date | TIMESTAMPTZ |
| asset_name | VARCHAR |
| alert_type | VARCHAR |
| metric_value | FLOAT |
| threshold | FLOAT |
| created_at | TIMESTAMPTZ |

---

## Load strategy

**Day 1 - Full load**

No existing data in the warehouse. Pipeline pulls 2 years of historical data for all 6 assets. Around 490 rows per asset. This runs once to populate the database.

**Day 2 onwards - Incremental load**

Existing data found in the warehouse. Pipeline checks the last date in the database and pulls only new data since that date. One new row per asset per trading day. Appended to existing data with deduplication.

---

## Dashboard tabs

| Tab | What it shows |
|---|---|
| Documentation | Business context, architecture, metrics explained, tech stack |
| Overview | Daily scorecard with green/red for each asset, cumulative returns chart |
| Trends | Price chart with 30 and 90 day moving average overlay, daily returns distribution |
| Risk | Volatility bar chart, correlation heatmap, drawdown chart |
| Alerts | All threshold breach events with filters |
| Insights | Senior level live analysis with dynamic numbers from the database |

---

## Tech stack

| Layer | Tool used | Production equivalent |
|---|---|---|
| Source | Yahoo Finance API via yfinance | Bloomberg API or Reuters Eikon |
| Extract | Python + pandas | Airbyte or Fivetran |
| Transform | Python + pandas | dbt or Apache Spark |
| Warehouse | Supabase PostgreSQL | Snowflake or Google BigQuery |
| Orchestration | schedule library | Apache Airflow or Prefect |
| Dashboard | Streamlit + Plotly | Tableau or Power BI |

---

## How to run locally

**1. Clone the repository**

```bash
git clone https://github.com/SaiAjay29/Investment-portfolio.git
cd Investment-portfolio
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set up environment variable**

Create a file called config.env in the project root:

```
DATABASE_URL=your-supabase-connection-string
```

**4. Run the full pipeline**

```bash
export DATABASE_URL="your-supabase-connection-string"
python orchestrate/pipeline.py
```

**5. Run the dashboard**

```bash
streamlit run dashboard/app.py
```

---

## Project structure

```
investment-portfolio/
├── extract/
│   └── fetch_data.py
├── transform/
│   └── clean_transform.py
├── load/
│   └── load_to_db.py
├── orchestrate/
│   └── pipeline.py
├── dashboard/
│   └── app.py
├── docs/
│   └── requirements.md
├── requirements.txt
└── README.md
```

---

## Built by

Sai Ajay Bhargav Gunturu
B.Tech Data Science and AI, ICFAI University Hyderabad
Financial Services Data Engineering Portfolio Project

