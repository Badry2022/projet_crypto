from fastapi import FastAPI, Path, Query, HTTPException, Header
import json
from typing import Optional
from pydantic import BaseModel
import random
import os
from project.binance import Kline
from kafka import KafkaProducer
from datetime import datetime, timedelta

kafka_host = os.environ.get('KAFKA_HOST', default="192.168.1.75")

api = FastAPI(
    title = "API Kafka",
    description = "Complément d'API pour le projet OPA Bot",
    version = "1.0.1")

# Première page de notre API
@api.get('/', name='home', tags=['home'])
def home():
    """First page of our API
    """
    return {"Data":"API OPA Bot"}

kafka_producer = {}

def active_kakfa(pair):
    if pair in kafka_producer:
        return
    kafka_producer[pair] = KafkaProducer(bootstrap_servers=kafka_host)
    kline_object = Kline(pair.replace('_',''))
    
    initialized = False
    def handle_socket_message(msg):
#        print(msg)
        nonlocal initialized
        kline = json.loads(msg)
        json_opa = {
            "Time":int(kline["k"]["t"]), 
            "Open":float(kline["k"]["o"]), 
            "High":float(kline["k"]["h"]), 
            "Low":float(kline["k"]["l"]), 
            "Close":float(kline["k"]["c"]),
            "Volume":float(kline["k"]["v"])
        }
        if not initialized:
            end_time = int(json_opa["Time"]) // 1000
            stream_start_date = datetime.fromtimestamp(end_time)
            start_time = int((stream_start_date - timedelta(seconds=1200)).strftime("%s"))
            for kline in kline_object.get_historical(start_time=start_time, exclude_start=False, end_time=end_time, exclude_end=True):
                json_like = dict(
                    Time = int(kline[0] * 1000),
                    Open = float(kline[1]),
                    High = float(kline[2]),
                    Low = float(kline[3]),
                    Close = float(kline[4]),
                    Volume = float(kline[5])
                )
                
                kafka_producer[pair].send(
                    topic=pair,
                    value=json.dumps(json_like).encode("utf-8")
                )
            initialized = True
            
        kafka_producer[pair].send(
            topic=pair,
            value=json.dumps(json_opa).encode("utf-8")
        )
        
    
    kline_object.subscribe_socket(handle_socket_message)
    
# API pour appeler nos données Kafka
@api.get('/kafka-info/{pair}')
def get_kafka_info(pair: str = Path(None, description="the pair we want to return")):
    active_kakfa(pair)
    return {'server':kafka_host, 'topic':pair}