CREATE SCHEMA IF NOT EXISTS nem_dispatches;

CREATE TABLE IF NOT EXISTS nem_dispatches.dispatch_prices (
    settlement_time TIMESTAMPTZ NOT NULL,
    region_id TEXT NOT NULL,
    rrp DOUBLE PRECISION,
    intervention SMALLINT,
    price_status TEXT,
    PRIMARY KEY (settlement_time, region_id)
);