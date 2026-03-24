import os
import pandas as pd
from nemosis import dynamic_data_compiler
from datetime import datetime, timedelta

class NEMDataFetcher:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def _generate_date_range(self, start_time: str, end_time: str):
        start = datetime.strptime(start_time, "%Y/%m/%d %H:%M:%S")
        end = datetime.strptime(end_time, "%Y/%m/%d %H:%M:%S")
        dates = []
        current = start
        while current < end:
            dates.append(current)
            current += timedelta(days=1)
        return dates

    def _get_save_path(self, date: datetime, table: str):
        year = str(date.year)
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)
        folder = os.path.join(self.raw_data_cache, year, month, day)
        os.makedirs(folder, exist_ok=True)
        filename = f"{table}.csv"
        return os.path.join(folder, filename)

    def fetch_and_store(self, start_time: str, end_time: str, table: str):
        saved_files = []
        for date in self._generate_date_range(start_time, end_time):
            day_start = date.strftime("%Y/%m/%d 00:00:00")
            day_end = (date + timedelta(days=1)).strftime("%Y/%m/%d 00:00:00")
            
            df = dynamic_data_compiler(day_start, day_end, table, self.raw_data_cache)
            if df is None or df.empty:
                continue  
            
            save_path = self._get_save_path(date, table)
            df.to_csv(save_path, index=False)
            saved_files.append(save_path)
            print(f"Saved {table} data for {day_start} to {save_path}")
        
        return saved_files


fetcher = NEMDataFetcher("~/Documents/Project/Naviec/data/")
files = fetcher.fetch_and_store(
    start_time="2024/01/01 00:00:00",
    end_time="2024/02/01 00:00:00",
    table="DISPATCHPRICE"
)