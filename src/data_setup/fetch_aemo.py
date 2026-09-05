import argparse
import datetime as dt
import os
import typing

import numpy as np
import pandas as pd
from nemosis import cache_compiler, defaults, dynamic_data_compiler

DEFAULT_END = dt.datetime(2016, 4, 20, 0, 0, 0)
DEFAULT_START = DEFAULT_END - dt.timedelta(days=10)
DEFAULT_TABLE = "DISPATCHPRICE"


class NEMDataFetcher:
    def __init__(self) -> None:
        '''
        Initialise the Data Fetcher
        '''

        self.__datapath = os.path.join(os.getcwd(),'data')
        os.makedirs(self.__datapath, exist_ok=True)

    def get_file_path(self):
        return self.__datapath

    def __generate_date_range(self, start_time: dt.datetime, end_time: dt.datetime) -> np.ndarray[dt.datetime]:
        '''
            Generate a numpy array of dates using the given start_time and end_time

            Args:
                start_time (datetime.datetime): Starting time of the NEM data files.
                end_time (datetime.datetime): Ending time of the NEM data files.

            Returns:
                np.ndarray[datetime.datetime]: A numpy array of datetime.datetime
        '''

        inclusive_days_interval = (end_time-start_time).days + 1    
        dates = np.empty(shape=inclusive_days_interval,dtype=dt.datetime)  

        current = start_time
        index=0
        while current < end_time:
            dates[index]=current
            current += dt.timedelta(days=1)
            index+=1

        return dates

    def __get_files_save_path(self, date: dt.datetime, table: str) -> str:
        '''
            Generate directories for each of sub csv files. 

            Args:
                date (datetime.datetime): The date of the current file.
                table (str): The name of the type of table extracting (type of NEM table).

            Returns:
                str: Path to the folder of that csv files.
        '''
        year = str(date.year)
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        folder = os.path.join(self.__datapath, year, month, day)
        os.makedirs(folder, exist_ok=True)

        return os.path.join(folder, f"{table}.csv")

    def fetch_and_store(self, start_time: dt.datetime, end_time: dt.datetime, table: str='DISPATCHPRICE', filename: typing.Optional[str]='full_data.csv'):
        '''
            Fetch and Store The CSV Files From NEM. 

            Args:
                start_time (datetime.datetime): Format of 'yyyy/mm/dd HH:MM:SS'.
                end_time (datetime.datetime): Format of 'yyyy/mm/dd HH:MM:SS'.
                table (str): Wanted table name from NEM.
        '''
        self.__raw_csv_filepath = os.path.join(self.__datapath + "/raw", filename)

        format='%Y/%m/%d %H:%M:%S'
        start=start_time.strftime(format)
        end=end_time.strftime(format)
        csv=dynamic_data_compiler(start_time=start,end_time=end, table_name=table, raw_data_location=self.__datapath + "/raw", fformat='csv', filter_cols=['REGIONID'], filter_values=(['SA1'],))

        if csv is None or csv.empty:
            print('Empty data fetched.')
            return
        
        csv.to_csv(self.__raw_csv_filepath, index=False)

    
    def get_working_dataset(self, filename: typing.Optional[str]='full_data.csv'):
        df=pd.pandas.read_csv(self.__raw_csv_filepath,sep=',')


def run_fetch(
    start_time: dt.datetime = DEFAULT_START,
    end_time: dt.datetime = DEFAULT_END,
    table: str = DEFAULT_TABLE,
    data_dir: typing.Optional[str] = None,
) -> None:
    fetcher = NEMDataFetcher()
    fetcher.fetch_and_store(start_time=start_time, end_time=end_time, table=table)


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
