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

---

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

These signals strongly influence electricity price formation.

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

Main scripts:

```
ingestion/
    aemo_downloader.py
    weather_downloader.py
    data_cleaner.py
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

# Project Structure

```
nem-forecasting/

ingestion/
    aemo_downloader.py

database/
    schema.sql

features/
    feature_engineering.py

models/
    train_models.py
    evaluate_models.py

forecast/
    generate_forecast.py

optimizer/
    battery_optimizer.cpp
    backtest.cpp

api/
    service.py

dashboard/
    app.py
```

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


# Repo structure
Naviec/
│
├── data/                      # Raw & processed data
│   ├── raw/                   # Raw CSV/API dumps
│   ├── processed/             # Cleaned / feature-engineered data
│   └── aemo/                  # Direct AEMO datasets or API scripts
│
├── notebooks/                 # Jupyter notebooks for EDA & prototyping
│   ├── 01_data_exploration.ipynb
│   └── 02_model_testing.ipynb
│
├── src/                       # Main source code
│   ├── data_ingestion/        # Data ingestion & preprocessing
│   │   ├── fetch_aemo.py
│   │   └── preprocess.py
│   │
│   ├── models/                # ML/DL forecasting models
│   │   ├── train_model.py
│   │   └── evaluate_model.py
│   │
│   ├── optimizer/             # Stochastic / C++ optimizer wrapper
│   │   ├── cpp/               # C++ source files
│   │   ├── build/             # Compiled binaries
│   │   └── run_optimizer.py   # Python wrapper for C++ code
│   │
│   ├── api/                   # FastAPI / Flask for serving forecasts
│   │   ├── main.py
│   │   └── routes.py
│   │
│   └── utils/                 # Helper functions, logging, metrics
│       ├── logger.py
│       └── metrics.py
│
├── tests/                     # Unit / integration tests
│   ├── test_data.py
│   ├── test_models.py
│   └── test_optimizer.py
│
├── scripts/                   # Helper scripts (e.g., db load, run experiments)
│   ├── run_full_pipeline.sh
│   └── update_postgres.py
│
├── config/                    # Config files (YAML/JSON)
│   ├── db_config.yaml
│   ├── model_config.yaml
│   └── optimizer_config.yaml
│
├── requirements.txt           # Python dependencies
├── CMakeLists.txt             # If building C++ optimizer
├── README.md                  # Project overview, setup, and usage
└── .gitignore