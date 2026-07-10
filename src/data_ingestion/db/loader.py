import argparse
import os
import typing

import pandas as pd
from psycopg2.extras import execute_values

from data_ingestion.db.connection import get_connection

UPSERT_DISPATCH_PRICES = """
INSERT INTO dispatch_prices (settlementdate, regionid, rrp)
VALUES %s
ON CONFLICT (settlementdate, regionid)
DO UPDATE SET rrp = EXCLUDED.rrp;
"""


def _prepare_dispatch_prices(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df[['SETTLEMENTDATE', 'REGIONID', 'RRP']].copy()
    prepared['SETTLEMENTDATE'] = pd.to_datetime(prepared['SETTLEMENTDATE'])
    prepared = prepared.dropna(subset=['SETTLEMENTDATE', 'REGIONID', 'RRP'])
    return prepared


def load_dataframe(df: pd.DataFrame) -> int:
    prepared = _prepare_dispatch_prices(df)
    rows = list(prepared.itertuples(index=False, name=None))

    if not rows:
        return 0

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, UPSERT_DISPATCH_PRICES, rows)
        conn.commit()
    finally:
        conn.close()

    return len(rows)


def load_from_csv(csv_path: str) -> int:
    df = pd.read_csv(csv_path, sep=',')
    return load_dataframe(df)


def run_load(data_dir: typing.Optional[str] = None, filename: str = 'full_data.csv') -> int:
    base_dir = data_dir if data_dir is not None else os.getcwd()
    csv_path = os.path.join(base_dir, 'data', filename)
    return load_from_csv(csv_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load full_data.csv into dispatch_prices.")
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--filename", default="full_data.csv")
    args = parser.parse_args()

    loaded = run_load(data_dir=args.data_dir, filename=args.filename)
    print(f"Loaded {loaded} row(s) into dispatch_prices.")


if __name__ == "__main__":
    main()
