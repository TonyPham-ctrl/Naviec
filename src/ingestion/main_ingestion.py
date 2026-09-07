
import argparse
import datetime as dt
import typing

from src.ingestion.fetch_aemo import NEMDataFetcher

DEFAULT_END = dt.datetime(2016, 4, 20, 0, 0, 0)
DEFAULT_START = DEFAULT_END - dt.timedelta(days=10)
DEFAULT_TABLE = "DISPATCHPRICE"


def _parse_dt(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def run_fetch(
    start_time: dt.datetime = DEFAULT_START,
    end_time: dt.datetime = DEFAULT_END,
    table: str = DEFAULT_TABLE,
    data_dir: typing.Optional[str] = None,
) -> None:
    fetcher = NEMDataFetcher(data_dir=data_dir)
    fetcher.fetch_dispatch(start_time=start_time, end_time=end_time, table=table)
    
def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store AEMO data.")
    parser.add_argument("--start", type=_parse_dt, default=DEFAULT_START)
    parser.add_argument("--end", type=_parse_dt, default=DEFAULT_END)
    parser.add_argument("--table", default=DEFAULT_TABLE)
    parser.add_argument("--data-dir", default=None)
    args = parser.parse_args()

    run_fetch(
        start_time=args.start,
        end_time=args.end,
        table=args.table,
        data_dir=args.data_dir,
    )
