import sqlite3, sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, MetaData, create_engine

class InsertSQLite:
    def __init__(self):
        self._engine = create_engine('sqlite:///sqlite-insert-timings.db', echo=False)
        meta = MetaData()

        self._engine.execute(f"DROP TABLE IF EXISTS TIMINGS_TABLE")
        self._table = Table("TIMINGS_TABLE", meta,
                        Column('timestamp', Integer, nullable=False),
                        Column('open', Float),
                        Column('close', Float),
                        Column('high', Float),
                        Column('low', Float),
                        Column('volume', Float),
                        extend_existing=True
                    )
        meta.create_all(self._engine)
        self._conn = self._engine.connect()

    def write_batch(self, batch):
        self._conn.execute(sqlalchemy.insert(self._table), batch)

class PandasSQLite:
    def __init__(self):
        self._engine = create_engine('sqlite:///sqlite-pandas-timings.db', echo=False)
        meta = MetaData()

        self._engine.execute(f"DROP TABLE IF EXISTS TIMINGS_TABLE")
        self._table = Table("TIMINGS_TABLE", meta,
                        Column('timestamp', Integer, nullable=False),
                        Column('open', Float),
                        Column('close', Float),
                        Column('high', Float),
                        Column('low', Float),
                        Column('volume', Float),
                        extend_existing=True
                    )
        meta.create_all(self._engine)

    def write_batch(self, batch):
        batch.to_sql("TIMINGS_TABLE",con = self._engine, index=False, if_exists='append')
