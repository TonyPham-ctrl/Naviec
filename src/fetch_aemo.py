import os
import typing
import pandas as pd
import numpy as np
from nemosis import dynamic_data_compiler, static_table
import datetime as dt

class NEMDataFetcher:
    def __init__(self, path: typing.Optional[str]=None) -> None:
        '''
            Initialise the Data Fetcher

            Args:
                path (str | None): Absolute path to the data storage directory. If None automatically generate absolute path.
            
            Return:
                None
        '''
        if path == None:
            self.__datapath = os.path.join(os.getcwd(),'data')
            os.makedirs(self.__datapath, exist_ok=True)
        else:
            self.__datapath = os.path.join(path, 'data')
            os.makedirs(self.__datapath, exist_ok=True)
        
        self.__filepath = os.path.join(self.__datapath, 'full_data.csv')

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
        #======= Date Naming Format ========
        year = str(date.year)
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        # This makes sure that the name would be consistent, say, 2020|00|00 (The "|" is for visualisation).
        #===================================

        folder = os.path.join(self.__datapath, year, month, day)
        os.makedirs(folder, exist_ok=True)

        return os.path.join(folder, f"{table}.csv")

    def fetch_and_store(self, start_time: dt.datetime, end_time: dt.datetime, table: str):
        '''
            Fetch and Store The CSV Files From NEM. 

            Args:
                start_time (datetime.datetime): Format of 'yyyy/mm/dd HH:MM:SS'.
                end_time (datetime.datetime): Format of 'yyyy/mm/dd HH:MM:SS'.
                table (str): Wanted table name from NEM.
        '''
        # saved_files = []

        # dates =  self._generate_date_range(start_time, end_time)

        format='%Y/%m/%d %H:%M:%S'
        start=start_time.strftime(format)
        end=end_time.strftime(format)
        csv=dynamic_data_compiler(start_time=start,end_time=end, table_name=table, raw_data_location=self.__datapath, fformat='csv', filter_cols=['REGIONID'], filter_values=(['SA1'],))

        if csv is None or csv.empty:
            print('Empty data fetched.')
            return
        
        # save_path = self.__get_files_save_path(start_time, table)
        csv.to_csv(self.__filepath, index=False)

        
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
    
    def get_working_dataset(self):
        # Using pandas to drop the unnecessary columns for now. Only focus on RRP, SETTLEMENTDATE. The REGIONID is SA1 by default.
        df=pd.pandas.read_csv(self.__filepath,sep=',')
        dropping_cols=['INTERVENTION','RAISE6SECRRP','RAISE60SECRRP','RAISE5MINRRP','RAISEREGRRP','LOWER6SECRRP','LOWER60SECRRP','LOWER5MINRRP','LOWERREGRRP','PRICE_STATUS','REGIONID']
        df.drop(columns=dropping_cols,inplace=True)
        filename=os.path.join(self.__datapath,'data.csv')
        df.to_csv(filename, sep=',', index=False, header=True)