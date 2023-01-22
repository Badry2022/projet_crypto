#!/usr/bin/env python3

import os
from datetime import datetime, timedelta, timezone
import json

# Module Kafka
from kafka import KafkaProducer

# Modules FastAPI
from fastapi import FastAPI, Path
from fastapi import Header, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Module MongoDB
from mongo import MongoAtlas

# Modules project
from binance import Kline

############################################################################################
# step 0: Instanciation de l'API
############################################################################################
api = FastAPI(
    title = "API CryptoBot",
    description = "API for the OPA project",
    version = "1.0",
    openapi_tags = [
        {
            'name':'Home section',
            'description': 'Home page of API'
        },
        {
            'name':'Data section',
            'description':'Displaying some data'
        },
        {
            'name':'CRUD section',
            'description':'Creating, reading, updating and deleting data.'
        }
    ]
)


############################################################################################
# STEP 1: Home Section
############################################################################################
connexion = MongoAtlas()
dbase = connexion.create_database('financeDB')

@api.get('/', name = 'Home section', tags = ['Home section'])
def get_infos():
    """Get last informations from our MongoDB database's informations"""
    output = []
    output.append("################################## Last update informations ##################################")
    informations = list(dbase["informations"].find())
    for ticker_infos in informations:
        current_ticker = ticker_infos["Ticker"] + "_" + ticker_infos["Frequency"] + "   :   "
        current_ticker += ticker_infos["Begin_date"].strftime('%Y-%m-%d') + " ----> " + ticker_infos["End_date"].strftime('%Y-%m-%d') 
        output.append(current_ticker)

    return output

############################################################################################
# STEP 2: Data Section
############################################################################################
@api.get("/symbols", name = 'Diplay all symbols', tags = ['Data section'])
def get_symbols():
    """Get all tickers from our MongoDB database's informations"""
    informations = list(dbase["informations"].find())
    rslt = []
    for tickerinfos in informations:
       x = tickerinfos["Ticker"]
       rslt.append(x)
    return set(rslt)

@api.get("/collections", name = 'Diplay all collections', tags = ['Data section'])
def get_collections():
    """Get all collections from our MongoDB database's informations"""
    informations = list(dbase["informations"].find())
    rslt = []
    for tickerinfos in informations:
        x = tickerinfos["Ticker"] + "_" + tickerinfos["Frequency"]
        rslt.append(x)
    return rslt


############################################################################################
# STEP 3: Users & Admin authentification section
############################################################################################
users = {
    "kevin": "first",
    "marouane": "second",
    "sofia": "third",
    "vianney": "fourth",
    "admin": "4dm1N"
    }

admins = {
    "admin": "4dm1N"
}

security = HTTPBasic()

def verify_user(credentials: HTTPBasicCredentials = Depends(security)): 
    username = credentials.username
    if not username in users.keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    password = credentials.password
    if users[username] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if not username in admins.keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    password = credentials.password
    if admins[username] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

############################################################################################
# STEP 4: CRUD section
############################################################################################
def kline_to_documents(klines):
    list_documents = []
    if klines:
        for kline in klines:
            list_documents.append({
                "Time" : datetime.utcfromtimestamp(kline[0]), 
                "Open" : kline[1], 
                "High" : kline[2], 
                "Low" : kline[3], 
                "Close" : kline[4], 
                "Volume" : kline[5]})
    
    return list_documents


def update_collection_data(collection_name):
    currency_1 = collection_name.split('_')[0]
    currency_2 = collection_name.split('_')[1]
    frequency = collection_name.split('_')[2]
    ticker = currency_1 + "_" + currency_2
    ticker_infos = list(dbase["informations"].find({"Ticker": ticker, "Frequency": frequency}))
    last_existing_date = ticker_infos[0]["End_date"]
    ticker_binance = currency_1 + currency_2
    kline_engine = Kline(ticker_binance, frequency)
    klines = kline_engine.get_recent_data(last_existing_date)
    list_documents = kline_to_documents(klines)
    if list_documents:
        dbase[collection_name].insert_many(list_documents)

    return (collection_name + "  :  update data done")

def update_collection_infos(collection_name):
    currency_1 = collection_name.split('_')[0]
    currency_2 = collection_name.split('_')[1]
    frequency = collection_name.split('_')[2]
    ticker = currency_1 + "_" + currency_2
    #get updated infos from collection data
    collection_data = list(dbase[collection_name].find())
    dates = [d['Time'] for d in collection_data]
    updated_infos = {"Ticker" : ticker, 
    "Frequency" : frequency,
    "Currency_1" : currency_1,
    "Currency_2" : currency_2,
    "Begin_date" : min(dates),
    "End_date" : max(dates)}
    update = {'$set': updated_infos}
    #update infos for existing ticker and create new document for new ticker
    ticker_infos = list(dbase["informations"].find({"Ticker": ticker, "Frequency": frequency}))
    if ticker_infos:
        ticker_dict = ticker_infos[0]
        dbase["informations"].update_one(ticker_dict, update)
    else:
        print("Nouvelle Collection : ", collection_name)
        dbase["informations"].insert_one(updated_infos)

    return (collection_name + "  :  update infos done")


# CREATE -----------------------------------------------------------------------------------
@api.post('/admin/create_data', name = 'Create new ticker', tags = ['CRUD section'])
def create_new_ticker(collection_name, start_time: int=1546300800, adminCredentials: str = Depends(verify_admin)):
    currency_1 = collection_name.split('_')[0] #ETH   #symbol:ETHUSDT
    currency_2 = collection_name.split('_')[1] 
    frequency = collection_name.split('_')[2]
    ticker = currency_1 + "_" + currency_2
    ticker_binance = currency_1 + currency_2
    ticker_infos = list(dbase["informations"].find({"Ticker": ticker, "Frequency": frequency}))
    if ticker_infos:
        return "Collection " + collection_name + " already exists"
    kline = Kline(ticker_binance, frequency)
    start_time_date = datetime.fromtimestamp(start_time)
    start_time_date = start_time_date.strftime("%Y-%m-%dT%H:%M:%S")
    klines = kline.get_historical(start_time = start_time_date)
    list_documents = kline_to_documents(klines)
    status = []
    if list_documents:
        dbase[collection_name].insert_many(list_documents)
        status.append("Collection created  :  " + collection_name)
    status.append(update_collection_infos(collection_name))

    return status

# READ ------------------------------------------------------------------------------------
@api.get('/read_data', name = 'Read collection', tags = ['CRUD section'])
def get_data(symbol, interval, start_time: int=1546300800, end_time=None, limit: int=10000, userCredentials: str = Depends(verify_user)):#1546297200
    collection_name = symbol + "_" + interval
    data = list(dbase[collection_name].find())
    if not end_time:
        end_time = int((datetime.now() + timedelta(days=1)).timestamp())
    data_out = []
    for elt in data:
        current_time = elt["Time"].replace(tzinfo=timezone.utc).timestamp()
        if current_time >= start_time and current_time <= end_time:
            current_dic = dict()
            current_dic["Time"] = elt["Time"].replace(tzinfo=timezone.utc).timestamp()
            current_dic["Close"] = elt["Close"]
            current_dic["Open"] = elt["Open"]
            current_dic["High"] = elt["High"]
            current_dic["Low"] = elt["Low"]
            current_dic["Volume"] = elt["Volume"]
            data_out.append(current_dic)

    if (len(data_out) > limit):
        data_out = data_out[:limit] 

    return data_out


# UPADATE ------------------------------------------------------------------------------------
@api.put('/admin/update_data', name = 'Update collection', tags = ['CRUD section'])
def update_data(adminCredentials: str = Depends(verify_admin)):
    existing_collections = list(dbase["informations"].find())
    collections_name = [d['Ticker'] + "_" + d['Frequency'] for d in existing_collections]
    status = []
    for collection in collections_name:
        status.append(update_collection_data(collection))
        status.append(update_collection_infos(collection))

    return status
    
# DELETE ------------------------------------------------------------------------------------
@api.delete('/admin/delete_data', name = 'Delete collection', tags = ['CRUD section'])
def delete_ticker(collection_name, adminCredentials: str = Depends(verify_admin)):
    currency_1 = collection_name.split('_')[0]
    currency_2 = collection_name.split('_')[1] 
    frequency = collection_name.split('_')[2]
    ticker = currency_1 + "_" + currency_2
    ticker_infos = list(dbase["informations"].find({"Ticker": ticker, "Frequency": frequency}))
    if not ticker_infos:
        return "Collection " + collection_name + " does not exist"
    
    dbase[collection_name].drop()

    dbase["informations"].delete_one({"Ticker": ticker, "Frequency": frequency})

    return "Collection " + collection_name + " deleted"



# #####################################---------------------------------------Streaming---------------

# kafka_host = os.environ.get('KAFKA_HOST', default="192.168.1.75")
# kafka_producer = {}

# def active_kakfa(pair):
#     if pair in kafka_producer:
#         return # Pourquoi ?
#     kafka_producer[pair] = KafkaProducer(bootstrap_servers=kafka_host)
#     kline_object = Kline(pair)
    
#     initialized = False
#     def handle_socket_message(msg):
# #        print(msg)
#         nonlocal initialized
#         kline = json.loads(msg)
#         json_opa = {
#             "Time":int(kline["k"]["t"]), 
#             "Open":float(kline["k"]["o"]), 
#             "High":float(kline["k"]["h"]), 
#             "Low":float(kline["k"]["l"]), 
#             "Close":float(kline["k"]["c"]),
#             "Volume":float(kline["k"]["v"])
#         }
#         if not initialized:
#             end_time = int(json_opa["Time"]) // 1000
#             stream_start_date = datetime.fromtimestamp(end_time)
#             start_time = int((stream_start_date - timedelta(seconds=1200)).strftime("%s"))
#             for kline in kline_object.get_historical(start_time=start_time, exclude_start=False, end_time=end_time, exclude_end=True):
#                 json_like = dict(
#                     Time = int(kline[0] * 1000),
#                     Open = float(kline[1]),
#                     High = float(kline[2]),
#                     Low = float(kline[3]),
#                     Close = float(kline[4]),
#                     Volume = float(kline[5])
#                 )
                
#                 kafka_producer[pair].send(
#                     topic=pair,
#                     value=json.dumps(json_like).encode("utf-8")
#                 )
#             initialized = True
            
#         kafka_producer[pair].send(
#             topic=pair,
#             value=json.dumps(json_opa).encode("utf-8")
#         )
        
    
#     kline_object.subscribe_socket(handle_socket_message)
    
# # API pour appeler nos données Kafka
# @api.get('/kafka-info/{pair}')
# def get_kafka_info(pair: str = Path(None, description="the pair we want to return")):
#     active_kakfa(pair)
#     return {'server':kafka_host, 'topic':pair}