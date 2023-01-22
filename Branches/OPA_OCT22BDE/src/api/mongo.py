# import pymongo
from pymongo import MongoClient
import certifi

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

class MongoAtlas:
    def __init__(self):
        CONNECTION_STRING = "mongodb+srv://financeDB:qjbOxeonNAtvRvzc@cluster0.kobegyl.mongodb.net/test"
        ca = certifi.where()
        self._client = MongoClient(CONNECTION_STRING, tlsCAFile=ca)

    def create_database(self, db_name):
        self._mydb = self._client[db_name]
        return self._mydb