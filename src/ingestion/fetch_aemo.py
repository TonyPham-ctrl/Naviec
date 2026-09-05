import argparse
import datetime as dt
import os
import typing

import pandas as pd
from nemosis import dynamic_data_compiler

DEFAULT_END = dt.datetime(2016, 4, 20, 0, 0, 0)
DEFAULT_START = DEFAULT_END - dt.timedelta(days=10)
DEFAULT_TABLE = "DISPATCHPRICE"


class NEMDataFetcher:
    def __init__(self, data_dir: typing.Optional[str] = None) -> None:
        self.__data_path = data_dir or os.path.join(os.getcwd(), "data")
        self.__raw_path = os.path.join(self.__data_path, "raw")
        self.__processed_path = os.path.join(
            self.__data_path, "processed", "dispatch_prices"
        )
        os.makedirs(self.__raw_path, exist_ok=True)
        os.makedirs(self.__processed_path, exist_ok=True)

    def get_file_path(self):
        return self.__data_path

    def __processed_file_path(
        self,
        start_time: dt.datetime,
        end_time: dt.datetime,
        table: str,
        filename: typing.Optional[str],
    ) -> str:
        if filename is None:
            start_label = start_time.strftime("%Y%m%dT%H%M%S")
            end_label = end_time.strftime("%Y%m%dT%H%M%S")
            filename = f"{table.lower()}_SA1_{start_label}_{end_label}.csv"
        return os.path.join(self.__processed_path, filename)

    def fetch_dispatch(
        self,
        start_time: dt.datetime,
        end_time: dt.datetime,
        table: str = "DISPATCHPRICE",
        filename: typing.Optional[str] = None,
    ) -> typing.Optional[pd.DataFrame]:

        date_format = "%Y/%m/%d %H:%M:%S"
        start = start_time.strftime(date_format)
        end = end_time.strftime(date_format)
        data = dynamic_data_compiler(
            start_time=start,
            end_time=end,
            table_name=table,
            raw_data_location=self.__raw_path,
            fformat="csv",
            filter_cols=["REGIONID"],
            filter_values=(['SA1'],),
        )

        if data is None or data.empty:
            print('Empty data fetched.')
            return None
        
        output_path = self.__processed_file_path(
            start_time=start_time,
            end_time=end_time,
            table=table,
            filename=filename,
        )
        data.to_csv(output_path, index=False)
        return data

    


def run_fetch(
    start_time: dt.datetime = DEFAULT_START,
    end_time: dt.datetime = DEFAULT_END,
    table: str = DEFAULT_TABLE,
    data_dir: typing.Optional[str] = None,
) -> None:
    fetcher = NEMDataFetcher(data_dir=data_dir)
    fetcher.fetch_dispatch(start_time=start_time, end_time=end_time, table=table)


def _parse_dt(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


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
