import argparse
import datetime as dt
import os
import typing

import numpy as np
import pandas as pd
from nemosis import dynamic_data_compiler, static_table

from constants import DEFAULT_LOOKBACK_DAYS, DEFAULT_REGION, DEFAULT_TABLE, DROPPED_FCAS_COLUMNS

DEFAULT_END = dt.datetime.now().replace(microsecond=0)
DEFAULT_START = DEFAULT_END - dt.timedelta(days=DEFAULT_LOOKBACK_DAYS)


class NEMDataFetcher:
    def __init__(self, path: typing.Optional[str]=None) -> None:
        if path == None:
            self.__datapath = os.path.join(os.getcwd(),'data')
            os.makedirs(self.__datapath, exist_ok=True)
        else:
            self.__datapath = os.path.join(path, 'data')
            os.makedirs(self.__datapath, exist_ok=True)


    def get_file_path(self):
        return self.__datapath

    def __generate_date_range(self, start_time: dt.datetime, end_time: dt.datetime) -> np.ndarray[dt.datetime]:

        inclusive_days_interval = (end_time-start_time).days + 1    # This means [start_time, end_time], not (start_time, end_time) in mathmatical notation.
        dates = np.empty(shape=inclusive_days_interval,dtype=dt.datetime)   # This create an empty (uninitialised) numpy array with the size of days in between.

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

        # This makes sure that the name would be consistent, say, 2020|00|00 (The "|" is for visualisation).
        #===================================

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
        # saved_files = []

        # dates =  self._generate_date_range(start_time, end_time)

        self.__full_csv_filepath = os.path.join(self.__datapath, filename)

        format='%Y/%m/%d %H:%M:%S'
        start=start_time.strftime(format)
        end=end_time.strftime(format)
        csv=dynamic_data_compiler(start_time=start,end_time=end, table_name=table, raw_data_location=self.__datapath, fformat='csv', filter_cols=['REGIONID'], filter_values=([DEFAULT_REGION],))

        if csv is None or csv.empty:
            print('Empty data fetched.')
            return

        csv['SETTLEMENTDATE'] = pd.to_datetime(csv['SETTLEMENTDATE'])

        if os.path.exists(self.__full_csv_filepath):
            existing = pd.read_csv(self.__full_csv_filepath, sep=',')
            existing['SETTLEMENTDATE'] = pd.to_datetime(existing['SETTLEMENTDATE'])
            csv = pd.concat([existing, csv], ignore_index=True)

        csv = csv.drop_duplicates(subset=['SETTLEMENTDATE', 'REGIONID'], keep='last')
        csv = csv.sort_values('SETTLEMENTDATE')

        cutoff = csv['SETTLEMENTDATE'].max() - dt.timedelta(days=DEFAULT_LOOKBACK_DAYS)
        csv = csv[csv['SETTLEMENTDATE'] >= cutoff]

        # save_path = self.__get_files_save_path(start_time, table)
        csv.to_csv(self.__full_csv_filepath, index=False)


        # format="%Y/%m/%d 00:00:00"
        # for date in dates:
            # day_start = date.strftime(format)
            # day_end = (date + dt.timedelta(days=1)).strftime(format)
            #
            # csv_file = dynamic_data_compiler(start_time=day_start,end_time=day_end,table_name=table,raw_data_location=self.datapath,fformat='csv')

            # if csv_file is None or csv_file.empty:
                # continue

            # file_path = self._get_save_path(date, table)
            # csv_file.to_csv(file_path, index=False)
            # saved_files.append(file_path)

        # return saved_files

    def get_working_dataset(self, filename: typing.Optional[str]='full_data.csv'):
        # Using pandas to drop the unnecessary columns for now. Only focus on RRP, SETTLEMENTDATE. The REGIONID is SA1 by default.
        df=pd.read_csv(self.__full_csv_filepath,sep=',')

        dropping_cols=DROPPED_FCAS_COLUMNS
        df.drop(columns=dropping_cols,inplace=True)

        filename=os.path.join(self.__datapath, filename)
        df.to_csv(filename, sep=',', index=False, header=True)


def run_fetch(
    start_time: dt.datetime = DEFAULT_START,
    end_time: dt.datetime = DEFAULT_END,
    table: str = DEFAULT_TABLE,
    data_dir: typing.Optional[str] = None,
) -> None:
    fetcher = NEMDataFetcher(path=data_dir)
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


if __name__ == "__main__":
    main()
