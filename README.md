# Naviec
NEM forecast optimiser by Tony Pham and Hai Hyunh

####### GITHUB PRACTICES #######

git branches bellow 
main => Final product post-testing and validation

staging => Used to merge features and for integration QAs
dev => Used to be cloned to develop new features
when working on a feature, clone from staging and name it dev/...
commit at the end of every session, and pull from dev at the start of every session

after local testing, produce a PR to staging for interation QAs

once approved, can merge into main. Everytime main is pushed, pull from main to staging and dev



####### ARCHITECTURE #######
# NEM Price Forecasting & Optimisation System

An end-to-end quantitative research system for forecasting electricity prices in the Australian National Electricity Market and evaluating trading strategies using optimisation and backtesting.

This project ingests market data, builds machine learning models to forecast electricity prices, and uses an optimisation engine to simulate energy trading strategies such as battery arbitrage.

The system is designed to resemble a realistic quantitative research and machine learning pipeline.

---

# System Overview

The system processes electricity market data through several layers:

1. Data ingestion
2. Data storage
3. Feature engineering
4. Forecasting models
5. Optimisation and backtesting
6. API and visualisation

High-level flow:

```
Market Data Sources
        ↓
Data Ingestion Pipeline
        ↓
PostgreSQL Database
        ↓
Feature Engineering Pipeline
        ↓
Forecasting Models
        ↓
Optimisation Engine
        ↓
Backtesting Results
        ↓
API + Dashboard
```

**Current status:** only stages 1 and 2 (data ingestion, data storage) are implemented. Everything from feature engineering onward is planned but not yet built — see [Next Steps](#next-steps).

---

# Setup & Running

## Prerequisites

* Python 3.11+
* Docker Desktop, with WSL integration enabled for your distro if running on WSL (Docker Desktop → Settings → Resources → WSL Integration)
* A `.env` file in the repo root (gitignored) with:
  ```
  DB_NAME=...
  DB_USER=...
  DB_PASSWORD=...
  DB_HOST=localhost
  DB_PORT=5433
  DB_PORT_HOST=5433
  ```
  `DB_HOST`/`DB_PORT` must point wherever Postgres is reachable *from where you run the Python code*. Since there is currently no containerised `app` service (see [Known Issues](#known-issues)), Python runs on the host and Postgres runs in Docker — so `DB_HOST=localhost` and `DB_PORT` must match the host-exposed port (`DB_PORT_HOST` in `docker-compose.yml`, default `5433`), not Postgres's internal port `5432`.

## One-time setup

```bash
pip install -r requirements.txt

docker compose up -d   # starts naviec_postgres, detached so it survives closing the terminal

cd src
python3 -c "from data_ingestion.db.schema import create_tables; create_tables()"
```

## Running the pipeline

**Important:** run these from inside `src/` (`cd src` first). `python -m src.main ...` from the repo root does **not** work — see [Known Issues](#known-issues).

```bash
cd src

# Run data ingestion only (fetches AEMO data, upserts into Postgres, updates data/full_data.csv)
python3 main.py ingest

# Run all available stages (currently just ingestion; prints which later stages are missing)
python3 main.py all

# Delete all files under the data directory
python3 main.py clean
```

`ingest`/`all` accept optional flags:

```bash
python3 main.py ingest --start "2024-01-01 00:00:00" --end "2024-01-31 00:00:00" --table DISPATCHPRICE --data-dir /path/to/repo
```

With no flags, `ingest` defaults to the last `DEFAULT_LOOKBACK_DAYS` (30, in `src/constants.py`) ending now. On a machine with a correct clock this works out of the box; if your system clock is skewed relative to real time, AEMO's archive won't have data for that window yet and you'll need to pass explicit `--start`/`--end` values from the past instead.

---

# Data Sources

Market data is sourced from the Australian Energy Market Operator for the National Electricity Market.

**Currently implemented:** Dispatch price (`DISPATCHPRICE`, regional electricity price every 5 minutes), region `SA1` only.

**Planned** primary datasets:

* Regional demand
* Generation mix
* Interconnector flows
* Pre-dispatch forecasts

**Planned** external data sources:

* Weather data
* Solar irradiance
* Wind speed

These signals strongly influence electricity price formation.

---

# Technology Stack

This section describes the target stack for the full system. Only the pieces marked *(implemented)* exist today.

## Core Languages

Python *(implemented)*
Used for data pipelines, feature engineering, machine learning, and orchestration.

C++ *(planned)*
Used for the optimisation engine and high-performance backtesting simulations.

---

## Data Infrastructure

PostgreSQL *(implemented — TimescaleDB extension not yet added)*
Used for storing large time-series datasets efficiently.

Key advantages:

* Optimised time-series storage
* SQL-based feature queries
* Scales well to millions of rows

---

## Data Processing

Python libraries in use: Pandas, NumPy.
Polars is listed as a future option but not currently used.

Responsibilities:

* parsing market datasets
* cleaning raw data
* generating training features *(planned)*
* constructing ML datasets *(planned)*

---

## Machine Learning *(planned)*

Model training uses:

* Scikit-learn
* XGBoost
* PyTorch
* Statsmodels

Model types include:

* Persistence baseline
* Linear regression
* Gradient boosted trees
* LSTM neural networks

Experiment tracking is performed using MLflow.

---

## Optimisation *(planned)*

The trading optimisation engine is implemented in C++.

Responsibilities:

* simulate battery charging and discharging strategies
* maximise trading profit
* enforce operational constraints
* run large-scale backtests efficiently

Possible optimisation methods include:

* dynamic programming
* linear programming
* heuristic strategies

---

## API Layer *(planned)*

FastAPI exposes model predictions and strategy results.

Example endpoints:

POST /predict
Returns predicted electricity prices.

GET /forecast
Returns latest forecast data.

GET /strategy_results
Returns optimisation and backtesting results.

---

## Visualisation *(planned)*

Streamlit dashboard visualises:

* predicted vs actual prices
* model performance metrics
* electricity demand patterns
* trading strategy profitability

---

# System Components

## 1. Data Ingestion *(implemented)*

Responsible for downloading raw AEMO dispatch price data and loading it into PostgreSQL.

Process:

1. Fetch `DISPATCHPRICE` data from AEMO via `nemosis`
2. Upsert the fetched batch into `dispatch_prices`
3. Merge with the existing `data/full_data.csv`, dedupe, trim to a rolling 30-day window, and rewrite the file

See [File Responsibilities](#file-responsibilities) for the actual scripts.

---

## 2. Data Storage *(partially implemented)*

Raw price data is stored in PostgreSQL.

Implemented table:

`dispatch_prices`

```
settlementdate  TIMESTAMP
regionid        TEXT
rrp             NUMERIC
PRIMARY KEY (settlementdate, regionid)
```

Planned tables (not yet created):

`regional_demand`

```
timestamp
region
demand
scheduled_generation
net_interchange
```

`generation_mix`

```
timestamp
region
wind_generation
solar_generation
coal_generation
gas_generation
```

---

## 3. Feature Engineering *(planned — next up)*

Transforms raw data into model-ready features.

Example features:

* lagged prices
* rolling averages
* rolling volatility
* net demand
* renewable penetration
* hour of day / time-of-day stratum
* day of week

Feature pipeline:

```
load raw data from Postgres
generate lag features
compute rolling statistics
export training dataset
```

Output:

```
data/processed/training_dataset.parquet
```

---

## 4. Forecasting Models *(planned)*

Machine learning models predict future electricity prices.

Training pipeline:

```
load training dataset
train model
evaluate performance
save trained model
```

Evaluation metrics:

* RMSE
* MAE
* MAPE

Models are saved in the `models/` directory.

---

## 5. Forecast Generation *(planned)*

A scheduled pipeline produces forecasts using trained models.

Process:

```
retrieve latest market data
generate features
run prediction model
store forecast output
```

Example forecast output:

```
timestamp | predicted_price
12:00     | 87.4
12:05     | 91.2
12:10     | 104.8
```

---

## 6. Optimisation Engine *(planned)*

The optimisation engine evaluates trading strategies using predicted prices.

Primary use case:

Battery energy arbitrage.

Inputs:

* predicted prices
* battery capacity
* charge/discharge limits
* efficiency

Objective:

Maximise trading profit subject to operational constraints.

Output:

* optimal charging schedule
* trading profit
* performance metrics

---

## 7. Backtesting System *(planned)*

Backtesting simulates strategy performance using historical prices.

Metrics evaluated:

* total profit
* Sharpe ratio
* maximum drawdown
* volatility

Backtests can run thousands of simulations using the C++ engine.

---

## 8. API Service *(planned)*

The API layer allows other systems to retrieve predictions and strategy results.

FastAPI service provides:

* prediction endpoints
* historical forecast queries
* strategy evaluation results

---

## 9. Dashboard *(planned)*

A Streamlit application provides a visual interface for exploring results.

Dashboard features:

* electricity price charts
* predicted vs actual comparisons
* demand and generation visualisation
* trading strategy performance

---

# File Responsibilities

What actually exists in this repo today:

```
Naviec/
├── .env                              # DB credentials (gitignored, not committed)
├── docker-compose.yml                # Defines the naviec_postgres service (Postgres 15). No app service yet.
├── Dockerfile                        # Builds the Python app image; defaults to `python -m src.main all` (currently broken, see Known Issues)
├── requirements.txt                  # Python dependencies
├── data/                             # Ingestion output + nemosis's raw AEMO cache (gitignored)
│
├── src/
│   ├── main.py                       # CLI entrypoint: `ingest` / `all` / `clean` subcommands
│   ├── constants.py                  # Shared config: DEFAULT_LOOKBACK_DAYS, DEFAULT_REGION, DEFAULT_TABLE, DROPPED_FCAS_COLUMNS
│   ├── fetch_aemo.py                 # NEMDataFetcher: fetches DISPATCHPRICE from AEMO, upserts into Postgres, maintains the 30-day rolling data/full_data.csv
│   ├── clean_data.py                 # Deletes all files under data/
│   ├── HourlySampling.r              # Standalone stratified-sampling bias/SE analysis (not wired into the pipeline; reads data/partial_single_day.csv manually)
│   │
│   └── data_ingestion/
│       ├── __init__.py               # Package marker
│       └── db/
│           ├── connection.py         # get_connection(): opens a psycopg2 connection using .env credentials
│           ├── schema.py             # create_tables(): CREATE TABLE IF NOT EXISTS dispatch_prices
│           └── loader.py             # load_dataframe() / load_from_csv() / run_load(): upserts price rows into dispatch_prices
│
├── archive/                          # Older, unmaintained exploratory R scripts
├── latex/                            # Research writeup (SeasonalSampling.tex/.pdf)
└── README.md
```

Everything else described in the sections above (feature engineering, models, optimizer, API, dashboard) is design intent, not code that exists yet.

---

# Known Issues

* **`python -m src.main ...` does not work**, despite being the historically documented invocation. `main.py` and its dependencies use bare imports (`from fetch_aemo import ...` rather than `from src.fetch_aemo import ...`), which only resolve when run as `cd src && python3 main.py ...`. Use that form until the import style is fixed.
* **`docker-compose.yml` has no `app` service.** `docker compose up` only starts Postgres; the Dockerfile's image is never launched by compose. Running the Python code and connecting to Postgres currently requires running Python on the host against Postgres's host-exposed port (see Setup above), not inside the Docker network.
* **Ingestion requires live internet access** to AEMO (`nemweb.com.au`) via the `nemosis` library, and can only fetch date ranges AEMO has actually archived (i.e. not in the future relative to real-world time).

---

# Next Steps

Near-term implementation tasks, roughly in priority order:

1. **Feature engineering** (`src/features/feature_engineering.py`, not yet created) — pull `dispatch_prices` from Postgres and build a price-only training dataset: lagged prices, rolling mean/volatility, hour-of-day/stratum, day-of-week.
2. **Fix the stratified-sampling bias bug** in `src/HourlySampling.r` (line 82) — the bias calculation mixes mismatched-length vectors (`K_hat` replicate estimates vs per-stratum combinatorial counts) due to R's silent recycling. Should be `bias <- mean(sample_means) - theta`.
3. **Baseline forecasting model** — once a training set exists, train a simple baseline (persistence or linear regression) end-to-end to validate the full loop before investing in more complex models.
4. **Regional demand ingestion** — add a `regional_demand` table + loader once the price-only path is validated; demand is the strongest secondary price driver.
5. **Fix `main.py`'s import style** so `python -m src.main ...` works as documented, or update the README/Dockerfile to standardise on `cd src && python3 main.py ...`.
6. **Wire an `app` service into `docker-compose.yml`** so the full pipeline can run containerized against Postgres over the Docker network.

---

# Key Research Challenges

Electricity markets exhibit unique statistical properties including:

* extreme price spikes
* strong seasonality
* regime shifts
* non-stationary behaviour

Effective models must account for these characteristics.

---

# Future Improvements

Longer-term research directions, once the core pipeline is working:

* probabilistic price forecasting
* regime detection models
* spike prediction models
* reinforcement learning trading strategies
* real-time market data ingestion
