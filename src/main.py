from fetch_aemo import NEMDataFetcher, dt

fetcher = NEMDataFetcher()

start_time = dt.datetime(2025,1,1)
end_time = dt.datetime(2025,1,2)

fetcher.fetch_and_store(start_time=start_time, end_time=end_time, table='DISPATCHPRICE', filename='single_day.csv')
fetcher.get_working_dataset(filename='partial_single_day.csv')
