from threading import Thread
import asyncio
import websockets
import requests
from datetime import datetime, timedelta
from time import sleep
import re
import numbers
from project.websocket_threaded import WebsocketThreaded

REQUEST_MAX_RETRY = 3
BASE_ENDPOINT = "https://api.binance.com"
KLINE_PATH = "/api/v3/klines"

WS_BASE_ENDPOINT = "wss://stream.binance.com:9443"
WS_PATH = "/ws"

KLINE_FIRST_DATETIME = "2020-01-01T00:00:00"
KLINE_INTERVAL_1SECOND = '1s'
KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_1DAY = '1d'


def binance_request(path, params, trial=0):
    print("requests.get", BASE_ENDPOINT + path, params)
    response = requests.get(BASE_ENDPOINT + path, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429 or response.status_code == 418:
        if trial == REQUEST_MAX_RETRY:
            assert response.status_code not in [429, 418] 
        else:
            sleep(float(response.header()["Retry-After"]))
            return binance_request(path, params, trial+1)
    else:
        print("Unexpected value", response.status_code)
        print("url", BASE_ENDPOINT + path)
        print("params", params)
        assert response.status_code == 200


def time_interval(interval):
    if interval == KLINE_INTERVAL_1SECOND:
        return 1
    elif interval == KLINE_INTERVAL_1MINUTE:
        return 60
    elif interval == KLINE_INTERVAL_1HOUR:
        return 3600
    elif interval == KLINE_INTERVAL_1DAY:
        return 86400
    raise ValueError
    
def clean_time(rawTime, interval):
    if isinstance(rawTime, numbers.Number):
        rawTime = datetime.fromtimestamp(int(rawTime)).strftime("%Y-%m-%dT%H:%M:%S")
    
    if interval == KLINE_INTERVAL_1MINUTE:
        return re.sub("^(.*):[^:]+$", "\\1:00", rawTime)
    elif interval == KLINE_INTERVAL_1HOUR:
        return re.sub("^(.*):[^:]+:[^:]+$", "\\1:00:00", rawTime)
    elif interval == KLINE_INTERVAL_1DAY:
        return re.sub("^(.*)T.*$", "\\1T00:00:00", rawTime)
    else:
        return rawTime

def cleaned_klines(klines_iterator):
    for kline in klines_iterator:
        yield [kline[0]//1000, *[float(v) for v in kline[1:6]]]

def KlineSingleton(myClass):
    kline_instances={}
    def kline_id(pair, interval=KLINE_INTERVAL_1SECOND):
        return f"{pair}-{interval}"
    
    def getInstance(*args, **kwargs):
        instance_id = kline_id(*args, **kwargs)
        if instance_id not in kline_instances:
            kline_instances[instance_id] = myClass(*args, **kwargs)
        return kline_instances[instance_id]

    return getInstance
 
@KlineSingleton
class Kline:
    def __init__(self, pair, interval=KLINE_INTERVAL_1SECOND):
        self._pair = pair
        self._interval = interval
        self._subscribe_count = 0
        self._callbacks = dict()
        self._socket = None
    
    def get_historical(self, start_time=KLINE_FIRST_DATETIME, exclude_start=True, end_time=None, exclude_end=True):
        interval = self._interval
        symbol = self._pair
        dt = time_interval(interval)*1000
        timestamp = int(datetime.strptime(clean_time(start_time, interval), "%Y-%m-%dT%H:%M:%S").strftime("%s"))*1000
        if exclude_start:
            timestamp += dt
        if end_time is not None:
            end_timestamp = int(datetime.strptime(clean_time(end_time, interval), "%Y-%m-%dT%H:%M:%S").strftime("%s"))*1000
            if exclude_end:
                end_timestamp -= dt
        while True:
            data = {"symbol": symbol, "interval": interval, "startTime": timestamp, "limit": 1000}
            if end_time is not None:
                data["endTime"] = end_timestamp
            klines = binance_request(KLINE_PATH, data)
            n = len(klines)
            if n == 0:
                return
            else:
                yield from cleaned_klines(klines)
            if n < 1000:
                return
            else:
                timestamp = klines[-1][0] + dt
    
    def _handle_socket_message(self, message):
        for callback in self._callbacks.values():
            callback(message)

    def _websocket_url(self):
        return f"{WS_BASE_ENDPOINT}{WS_PATH}/{self._pair.lower()}@kline_{self._interval}"

    def subscribe_socket(self, callback):
        subscribe_id = self._subscribe_count
        self._subscribe_count += 1
        self._callbacks[subscribe_id] = callback
        if self._socket is None:
            self._socket = WebsocketThreaded(self._websocket_url(), self._handle_socket_message)
            self._socket.start()
        
        return subscribe_id
    
    def unsubscribe_socket(self, subscribe_id):
        del self._callbacks[subscribe_id]
        if not self._callbacks:
            self._socket.stop()
            self._socket = None

