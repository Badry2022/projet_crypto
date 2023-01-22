import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import pandas as pd
import __main__
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime
from graph_util import drawgraph
from collections import deque
from kafka import KafkaConsumer
import json
import requests

live_data = {}
api_host = os.environ.get('API_HOST', default='http://localhost:5000')

def get_kafka_pair(pair):
    if pair not in live_data:
        url = f"{api_host}/kafka-info/{pair}"
        response = requests.get(url).json()
        live_data[pair] = {
            'kafka_consumer': KafkaConsumer(
                response['topic'], consumer_timeout_ms=800, bootstrap_servers=response['server'], auto_offset_reset="earliest", group_id=f"dash-{datetime.now().timestamp():.0f}"
            ),
            'data': deque(maxlen=1200)
        }
        
    return live_data[pair]    

def pull_data(pair):
    kafka_pair = get_kafka_pair(pair)
    kafka_consumer = kafka_pair['kafka_consumer']
    try:
        for kafka_message in kafka_consumer:
            kline = json.loads(kafka_message.value)
#            print(pair,kline)
#            kafka_pair['data'].append([int(kline["k"]["t"]), float(kline["k"]["o"]), float(kline["k"]["h"]), float(kline["k"]["l"]), float(kline["k"]["c"]), float(kline["k"]["v"])])
            kafka_pair['data'].append([int(kline["Time"]), float(kline["Open"]), float(kline["High"]), float(kline["Low"]), float(kline["Close"]), float(kline["Volume"])])
    except Exception as e:
#        print(pair,e)
        pass

# Transformation des données
# Appel des données Mongo
def getdata(pair):
    if os.environ.get('APP_FAKE') == '2':
        return getdatafake(pair)
    
    pull_data(pair)
    df = pd.DataFrame(live_data[pair]['data'], columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df["Time"] = pd.to_datetime(df["Time"], unit='ms')
    
    return df

def getdatafake(pair):
    # Création du dataframe de données à partir du fichier csv ethusdt
    df = pd.read_csv(f'{pair}.csv')

    # Conversion de la colonne Time en objet datetime
    df['Time'] = pd.to_datetime(df['Time'])

    # Suppresion colonne 0
    df = df.drop('Unnamed: 0', axis=1)
    
    return df

def dropdown_pairs():
    if os.environ.get('APP_FAKE') == '1':
        pairs = ['BTCUSDT', 'ETHUSDT']
    else:
        url = f"{api_host}/symbols"
        pairs = requests.get(url).json()
    
    return [{'label':v.replace('_', ''), 'value':v} for v in pairs]



app = __main__.app

layout_2 = html.Div([
    html.H1('Données Live'),
    html.Div([
        dcc.Link("< Retour", href='/', style={'textDecoration': "none"})
    ], className="backlink"),
    html.Table([
        html.Tbody([
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        id = 'pair_live',
                        options=dropdown_pairs(),
                        multi = False,
                        placeholder="Choisissez une paire"
                    )
                ),
                
            ])
        ])
    ], className="main"),    
    
    
    html.Div(dcc.Graph(id='page-2-live')),
    dcc.Interval(
            id="interval-component", interval=0.3 * 1000, n_intervals=1  # in milliseconds
        )
    
], className='page live')

@app.callback(
    Output(component_id='page-2-live', component_property='figure'),
    # En fait, le nom des component id sera important dans le html, mais dans le callback, il n'est pas nécessaire de respecter une nomenclature particulière
    [
        Input(component_id='pair_live', component_property='value'),
        Input("interval-component", "n_intervals"),
    ]   
)

def update_graph(pair, _):
    if pair is None:
        return go.Figure()
           
    df = getdata(pair)
    # Création de la figure plotly
    fig = drawgraph(df)    
    
    return fig