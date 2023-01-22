import pandas as pd
from datetime import datetime
from itertools import cycle
from enum import Enum, auto

class BatchMode(Enum):
    LIST = auto()
    DICT = auto()
    DF = auto()
    TIME_DICT = auto()

timestamp = int(datetime.strptime("2000-01-01", "%Y-%m-%d").timestamp())
headers = ["timestamp", "open", "high", "low", "close", "volume"]

def gen_data():
    global timestamp
    pool = cycle([
        [15854.48, 15859.45, 15849.28, 15856.67, 0.68881],
        [15851.98, 15855.82, 15844.21, 15845.07, 1.06081],
        [15845.97, 15853.87, 15844.49, 15848.21, 0.77838],
        [15849.56, 15852.57, 15845.63, 15848.59, 0.33867],
        [15847.0, 15854.56, 15844.45, 15847.62, 0.27937],
        [15847.85, 15853.62, 15841.75, 15841.75, 2.17907],
        [15840.0, 15842.47, 15833.9, 15834.03, 1.59663],
        [15834.16, 15845.08, 15834.16, 15836.04, 0.1585],
        [15836.44, 15839.3, 15835.01, 15836.07, 0.05736],
        [15838.15, 15841.82, 15834.22, 15841.26, 0.21867]
        ])
    
    for row in pool:
        yield [timestamp] + row
        timestamp += 1

data_it = gen_data()

def gen_aslist():
    for row in data_it:
        yield row


def dict_data_transformer(gen):
    for row in gen:
        yield {k: v for k, v in zip(headers, row)}


def time_dict__data_transformer(gen):
    for row in gen:
        d = {k: v for k, v in zip(headers[1:], row[1:])}
        d["timestamp"] = datetime.fromtimestamp(row[0])
        d["metadata"] = {"symbol": "BTCEUR", "interval": "1s"}
        yield d


def df_batch_transformer(batch):
    df = pd.DataFrame(batch)
    columns = ['timestamp', 'open', 'close', 'high', 'low', 'quantity']
    return df.rename(columns={i: c for i, c in enumerate(headers)})


data_generators = {
    BatchMode.LIST: data_it,
    BatchMode.DICT: dict_data_transformer(data_it),
    BatchMode.DF: data_it,
    BatchMode.TIME_DICT: time_dict__data_transformer(data_it)
}

batch_transformer = {
    BatchMode.DF: df_batch_transformer
}

def binance_data(n_batch, mode=BatchMode.LIST):
    gen = data_generators[mode]
    batch = []
    for _ in range(n_batch):
        batch.append(next(gen))
    
    try:
        return batch_transformer[mode](batch)
    except KeyError:
        return batch
