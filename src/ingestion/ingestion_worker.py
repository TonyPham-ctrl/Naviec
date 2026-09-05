import datetime as dt
from src.ingestion.fetch_aemo import NEMDataFetcher


class IngestionWorker:
    def __init__(self, fetcher: NEMDataFetcher, store, region="SA1"):
        self.fetcher = fetcher
        self.store = store
        self.region = region

    def run_once(self):
        latest = self.store.latest_timestamp(self.region)
        start = latest + dt.timedelta(minutes=5)
        end = dt.datetime.now(dt.timezone.utc)

        data = self.fetcher.fetch_dispatch(start, end)
        self.store.upsert(data)