import pandas as pd
from datetime import datetime, timedelta
from binance import Kline
from mongo import MongoAtlas

#################### Collections des données
"""data_folder = './../data/'
data_file = 'Binance_BTCUSDT_1d.csv'
df = pd.read_csv(data_folder+data_file)
df = df[['date', 'open', 'high', 'low', 'close', 'Volume BTC']]
df.date = df.date.apply(lambda x: x.split(' ')[0])
df.date = df.date.apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
list_documents = []
for index, row in df.iterrows():
    list_documents.append({
        "Time" : row['date'], 
        "Open" : row['open'], 
        "High" : row['high'], 
        "Low" : row['low'], 
        "Close" : row['close'], 
        "Volume" : row['Volume BTC']})

connexion = MongoAtlas()
dbase = connexion.create_database('financeDB')
collection_name = "BTC_USDT_1d"
collection = dbase.create_collection(collection_name, timeseries = {"timeField": "Time"})
dbase[collection_name].insert_many(list_documents)
print(dbase[collection_name].count_documents({}))"""

################################## Collection des informations 
"""connexion = MongoAtlas()
dbase = connexion.create_database('financeDB')
frequency = "1d"
currency_1 = "BTC"
currency_2 = "USDT"
collection_name = currency_1 + "_" + currency_2 + "_" + frequency
print(dbase[collection_name].count_documents({}))

df = pd.DataFrame(list(dbase[collection_name].find()))
df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
collection = dbase.create_collection("informations")
infos_btc_usdt = {"Ticker" : currency_1 + "_" + currency_2, 
"Frequency" : frequency,
"Currency_1" : currency_1,
"Currency_2" : currency_2,
"Begin_date" : df.Time.min().to_pydatetime(),
"End_date" : df.Time.max().to_pydatetime()}
dbase["informations"].insert_one(infos_btc_usdt)
print(dbase["informations"].count_documents({}))"""


########################### Récuperer les nouvelles historical data
connexion = MongoAtlas()
dbase = connexion.create_database('financeDB')
collection_name = "BTC_USDT_1d"
df = pd.DataFrame(list(dbase[collection_name].find()))
df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
end_date = df.Time.max()
ticker = "BTCUSDT"
frequency = "1d"
kline_engine = Kline(ticker, frequency)
klines = kline_engine.get_recent_data(end_date)
########################## Rajouter les données à la collection des données
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
###
#dbase[collection_name].insert_many(list_documents)
#print(dbase[collection_name].count_documents({}))

