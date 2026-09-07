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
# Getting Started

## 1. Prerequisites

* Python 3.12
* Docker and Docker Compose

## 2. Configure credentials

Database credentials are read from a local `.env` file, which is git-ignored.
Copy the template and fill in your own values:

```bash
cp .env.example .env
```

## 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Start the database

```bash
docker compose up -d postgres
```

Apply the table definitions in `database/schema.sql`, then confirm the
connection works:

```bash
python scripts/check_db_connection.py
```

---

# Running The Pipeline

Use the CLI entrypoint at `src/main.py` to run individual stages or the full pipeline.

```bash
# Run data ingestion only
python -m src.main ingest

# Run all available stages
python -m src.main all

# Delete all files under the data directory
python -m src.main clean
```

# Data Sources

Market data is sourced from the Australian Energy Market Operator for the National Electricity Market.

Primary datasets used include:

* Dispatch price (regional electricity price every 5 minutes)
* Regional demand
* Generation mix
* Interconnector flows
* Pre-dispatch forecasts

External data sources may include:

* Weather data
* Solar irradiance
* Wind speed


---

# Technology Stack

## Core Languages

Python
Used for data pipelines, feature engineering, machine learning, and orchestration.

C++
Used for the optimisation engine and high-performance backtesting simulations.

---

## Data Infrastructure

PostgreSQL with TimescaleDB extension
Used for storing large time-series datasets efficiently.

Key advantages:

* Optimised time-series storage
* SQL-based feature queries
* Scales well to millions of rows

---

## Data Processing

Python libraries:

* Polars
* NumPy
* Pandas

Responsibilities:

* parsing market datasets
* cleaning raw data
* generating training features
* constructing ML datasets

---

## Machine Learning

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

## Optimisation

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

## API Layer

FastAPI exposes model predictions and strategy results.

Example endpoints:

POST /predict
Returns predicted electricity prices.

GET /forecast
Returns latest forecast data.

GET /strategy_results
Returns optimisation and backtesting results.

---

## Visualisation

Streamlit dashboard visualises:

* predicted vs actual prices
* model performance metrics
* electricity demand patterns
* trading strategy profitability

---

# System Components

## 1. Data Ingestion

Responsible for downloading and parsing raw electricity market data.

Process:

1. Download market files
2. Extract CSV data
3. Clean and standardise schema
4. Insert records into PostgreSQL

Main modules:

```
src/ingestion/
    fetch_aemo.py         # NEMDataFetcher, wraps the nemosis compiler
    main_ingestion.py     # stage entrypoint and default parameters
    ingestion_worker.py   # incremental fetch-and-load loop
```

---

## 2. Data Storage

All processed raw data is stored in PostgreSQL.

Example tables:

dispatch_prices

```
timestamp
region
rrp
```

regional_demand

```
timestamp
region
demand
scheduled_generation
net_interchange
```

generation_mix

```
timestamp
region
wind_generation
solar_generation
coal_generation
gas_generation
```

These tables are indexed by timestamp for efficient querying.

---

## 3. Feature Engineering

Transforms raw data into model-ready features.

Example features:

* lagged prices
* rolling averages
* rolling volatility
* net demand
* renewable penetration
* hour of day
* day of week

Feature pipeline:

```
load raw data
join datasets
generate lag features
compute rolling statistics
export training dataset
```

Output:

```
data/processed/training_dataset.parquet
```

---

## 4. Forecasting Models

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

## 5. Forecast Generation

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

## 6. Optimisation Engine

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

## 7. Backtesting System

Backtesting simulates strategy performance using historical prices.

Metrics evaluated:

* total profit
* Sharpe ratio
* maximum drawdown
* volatility

Backtests can run thousands of simulations using the C++ engine.

---

## 8. API Service

The API layer allows other systems to retrieve predictions and strategy results.

FastAPI service provides:

* prediction endpoints
* historical forecast queries
* strategy evaluation results

---

## 9. Dashboard

A Streamlit application provides a visual interface for exploring results.

Dashboard features:

* electricity price charts
* predicted vs actual comparisons
* demand and generation visualisation
* trading strategy performance

---

# Repository Structure

The repository is organised by pipeline layer. Each package owns exactly one
stage of the flow described in System Overview, so a change to how data is
fetched never requires touching how it is stored.

```
Naviec/
├── src/                        # Application source, one package per pipeline layer
│   ├── main.py                 # CLI entrypoint, selects and runs pipeline stages
│   ├── ingestion/              # Layer 1: acquire raw market data
│   │   ├── fetch_aemo.py       # NEMDataFetcher, pulls AEMO tables via nemosis
│   │   ├── main_ingestion.py   # Ingestion stage entrypoint and defaults
│   │   └── ingestion_worker.py # Incremental fetch-and-load loop
│   ├── storage/                # Layer 2: persistence
│   │   ├── postgres_store.py   # Connection handling and write path
│   │   └── queries.py          # Reusable SQL
│   └── utils/                  # Cross-cutting helpers, no pipeline logic
│       └── clean_data.py       # Removes generated files under data/
│
├── database/
│   └── schema.sql              # Table definitions (DDL) for the Postgres instance
│
├── scripts/                    # Operational one-offs, never imported by src/
│   └── check_db_connection.py  # Smoke test for database connectivity
│
├── tests/                      # Unit and integration tests (pytest)
│
├── research/                   # Exploratory statistical analysis in R
│   ├── HourlySampling.r
│   └── archive/                # Superseded experiments, kept for reference
│
├── docs/                       # LaTeX knowledge base and applied write-ups
│
├── data/                       # Git-ignored, regenerated by the pipeline
│   ├── raw/                    # Unmodified AEMO downloads
│   └── processed/              # Cleaned, analysis-ready extracts
│
├── docker-compose.yml          # Local Postgres service
├── Dockerfile                  # Pipeline runtime image
├── requirements.txt
├── .env.example                # Template for local credentials (.env is ignored)
└── README.md
```

## Module Boundaries

| Layer | Package | Responsibility | May import |
|---|---|---|---|
| Ingestion | `src/ingestion` | Fetch raw market data and return DataFrames | `src.utils` |
| Storage | `src/storage` | Persist and retrieve records in Postgres | `src.utils` |
| Utilities | `src/utils` | Filesystem and logging helpers | nothing in `src` |
| Entrypoint | `src/main.py` | Compose stages, parse CLI arguments | all of the above |

The dependency direction is one-way: ingestion never imports storage, and
storage never imports ingestion. `src/main.py` is the only module permitted to
wire them together. This keeps each layer independently testable and means a
new data source or a new database backend can be swapped in isolation.

## Where New Components Go

The remaining components described in System Components attach as new sibling
packages under `src/`, without modifying the existing layers:

| Component | Planned location |
|---|---|
| Feature engineering | `src/features/` |
| Forecasting models | `src/models/` |
| Optimisation engine and its wrapper | `src/optimizer/` |
| API service | `src/api/` |
| Dashboard | `src/dashboard/` |

These directories are created when the first real module lands in them, rather
than being committed empty.

## Implementation Status

| Stage | Status |
|---|---|
| Data ingestion (AEMO to DataFrame to CSV) | Implemented |
| Database schema | Defined in `database/schema.sql`, not yet applied automatically |
| Storage write path | Stubbed. `IngestionWorker` calls `latest_timestamp` and `upsert`, which do not exist yet |
| Feature engineering, models, optimiser, API, dashboard | Not started |

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

Potential extensions include:

* probabilistic price forecasting
* regime detection models
* spike prediction models
* reinforcement learning trading strategies
* real-time market data ingestion

