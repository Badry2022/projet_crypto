# import pymongo
from pymongo import MongoClient

class MongoBasic:
    def __init__(self):
        self._client = MongoClient('localhost', 27017)
        self._mydb = self._client["timing-simple"]
        try:
            self._mydb.ticker.drop()
        finally:
            pass

        self._mydb.create_collection(
            "ticker"
        )

    def write_batch(self, batch):
        self._mydb.ticker.insert_many(batch)


class MongoTimeSerie:
    def __init__(self):
        self._client = MongoClient('localhost', 27017)
        self._mydb = self._client["timing-timeserie"]
        try:
            self._mydb.ticker.drop()
        finally:
            pass

        self._mydb.create_collection(
            "ticker", 
            timeseries = {
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "seconds"
            }
        )

    def write_batch(self, batch):
        self._mydb.ticker.insert_many(batch)
