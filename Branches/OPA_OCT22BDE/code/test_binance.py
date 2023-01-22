from binance import Kline
from datetime import datetime, timedelta
from pymongo import MongoClient
import time
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import os

import pandas as pd

####Requete binance
####On récupère 1000 observations
kline_btceur_1m = Kline("BTCUSDT", interval="1d")
klines1 = kline_btceur_1m.get_historical(start_time="2020-01-01T00:00:00")
klines2 = kline_btceur_1m.get_historical(start_time="2019-08-01T19:30:00", end_time="2019-09-01T00:00:00")
####stocker les données dans un dataframe afin de les stocker dans une base sql
start_time = time.time()
df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
i = 0
for kline in klines1:
    df.loc[i, 'Time'] = datetime.utcfromtimestamp(kline[0])
    df.loc[i, 'Open'] = kline[1]
    df.loc[i, 'High'] = kline[2]
    df.loc[i, 'Low'] = kline[3]
    df.loc[i, 'Close'] = kline[4]
    df.loc[i, 'Volume'] = kline[5]
    i += 1
df_prep_time = time.time()-start_time
df.to_csv("aa.csv")
####stocker les données dans une liste de dictionnaires afin de les stocker dans une base mongodb
start_time = time.time()
list_documents = []
for kline in klines2:
    list_documents.append({
        "Time" : datetime.utcfromtimestamp(kline[0]), 
        "Open" : kline[1], 
        "High" : kline[2], 
        "Low" : kline[3], 
        "Close" : kline[4], 
        "Volume" : kline[5]})
ld_prep_time = time.time()-start_time

print("#####################Preparation des données###################")
print("DataFrame preparation run time : ", df_prep_time)
print("Nombre de lignes dans le dataframe : ", df.shape[0])
print("##############")
print("liste des documents preparation run time : ", ld_prep_time)    
print("Nombre de documents dans la liste : ", len(list_documents))

"""#Création de la base Mongodb
clientMongo = MongoClient('localhost', 27017)
dbMongo = clientMongo["mydatabase"]
db_collections = dbMongo.list_collection_names()
collection_name = "ticker"

#Création de la base SQL
#Il faut créer une db mydb.sqlite avant de créer la connexion
engine = create_engine('sqlite:///mydb.sqlite', echo=False)
table_name = "ticker"
#inspect(engine).has_table(table_name)

print("#######################Test Lecture#####################")
print(f"#####Nombre d'observations = {nb_dup*1000}")
nb_test = 1
avg = 0
size = 0
for i in range(nb_test):
    dbMongo.drop_collection(collection_name)
    start_time = time.time()
    collection = dbMongo.create_collection(collection_name, timeseries = {"timeField": "Time"})
    size_init = dbMongo.command('collstats', collection_name)['size']
    dbMongo[collection_name].insert_many(list_documents)
    size_end = dbMongo.command('collstats', collection_name)['size']
    size += (size_end - size_init)
    avg += (time.time() - start_time)
print("MongoDB run time : ", avg / nb_test)
print("MongoDB storage : ", size / nb_test / (1024*1024))
print("##############")
################
avg = 0
size = 0
for i in range(nb_test):
    engine.execute("DROP table IF EXISTS ticker")
    start_time = time.time()
    size_init = os.path.getsize('mydb.sqlite')
    df.to_sql(table_name, engine)
    size_end = os.path.getsize('mydb.sqlite')
    size += (size_end - size_init)
    avg += (time.time() - start_time)
print("SQL run time : ", avg / nb_test)
print("SQL storage : ", size / nb_test / (1024*1024))
print("##############")
#############
avg = 0
for i in range(nb_test):
    dbMongo.drop_collection(collection_name)
    start_time = time.time()
    collection = dbMongo.create_collection(collection_name, timeseries = {"timeField": "Time"})
    for i in range(len(list_documents)):
        dbMongo[collection_name].insert_one(list_documents[i])
    avg += (time.time() - start_time)
print("MongoDB run time one element : ", avg / nb_test)
print("##############")
##############
avg = 0
for i in range(nb_test):
    engine.execute("DROP table IF EXISTS ticker")
    start_time = time.time()
    query = "INSERT INTO  ticker (`Time` ,`Open` ,`High` ,`Low`, `Close`, `Volume`)  VALUES(?,?,?,?,?,?)"
    df[0:1].to_sql(table_name, engine)
    for i in range(1,len(df)):
        my_data = (df.loc[i, 'Time'], df.loc[i, 'Open'], df.loc[i, 'High'], 
        df.loc[i, 'Low'], df.loc[i, 'Close'], df.loc[i, 'Volume'])
        engine.execute(query, my_data)
    avg += (time.time() - start_time)
print("SQL run time one element : ", avg / nb_test)
print("##############")"""
    
"""
print("#####################Test ECRITURE###################")
print(f"#####Nombre d'observations = {nb_dup*1000}")
nb_test = 10
avg = 0
start = datetime.strptime("2022-11-20T19:31:00", "%Y-%m-%dT%H:%M:%S")
end = start + timedelta(minutes = 5)
for i in range(nb_test):
    start_time = time.time()
    query = dbMongo[collection_name].find( {'Time': {'$lt': end, '$gte': start}}, {"volume": 1})
    avg += (time.time() - start_time)
print("MongoDB : ", avg / nb_test)
avg = 0
Session = sessionmaker(bind =engine)
session = Session()
for i in range(nb_test):
    start_time = time.time()
    res = engine.execute(f"SELECT * FROM ticker WHERE Time >= '2022-11-20 19:31:00.000000'  AND Time < '2022-11-20 19:36:00.000000'")
    avg += (time.time() - start_time)
print("SQL : ", avg / nb_test) 
"""