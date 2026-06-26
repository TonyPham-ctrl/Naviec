from fetch_aemo import NEMDataFetcher, dt

fetcher = NEMDataFetcher()

start_time = dt.datetime(2025,1,1)
end_time = dt.datetime(2025,12,31)

fetcher.fetch_and_store(start_time=start_time, end_time=end_time, table='DISPATCHPRICE')
fetcher.get_working_dataset()
