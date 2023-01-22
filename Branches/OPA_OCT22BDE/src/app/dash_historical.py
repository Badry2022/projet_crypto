# Page 1
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
import requests

api_host = os.environ.get('API_HOST', default='http://localhost:5000')


def date_to_timestamp(d):
    dt = datetime(year=d.year, month=d.month, day=d.day)
    return int(dt.timestamp())


# Transformation des données
# Appel des données Mongo
def getdata(pair, start, end):
    if os.environ.get('APP_FAKE') == '1':
        return getdatafake(pair, start, end)
    
    url = f"{api_host}/read_data"
    # symbol=BTC_USDT&interval=1d&start_time=1546300800&limit=10000
    data={'symbol':pair, 'interval':'1d', 'start_time': date_to_timestamp(start), 'end_time':date_to_timestamp(end)}
    response = requests.get(url,params=data).json()
    df = pd.DataFrame(response, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    
    return df

def getdatafake(pair, start, end):
    # Création du dataframe de données à partir du fichier csv ethusdt
    df = pd.read_csv(f'{pair}.csv')

    # Conversion de la colonne Time en objet datetime
    df['Time'] = pd.to_datetime(df['Time'])

    # Suppresion colonne 0
    df = df.drop('Unnamed: 0', axis=1)
    
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    
    filtered_df = df.loc[(df['Time'] >= start)
                     & (df['Time'] <= end)]
    
    return filtered_df

def dropdown_pairs():
    if os.environ.get('APP_FAKE') == '1':
        pairs = ['BTC_USDT', 'ETH_USDT']
    else:
        url = f"{api_host}/symbols"
        pairs = requests.get(url).json()
    
    return [{'label':v.replace('_', ''), 'value':v} for v in pairs]

app = __main__.app

layout_1 = html.Div([
    html.H1('Données Historiques'),
    html.Div([
        dcc.Link("< Retour", href='/', style={'textDecoration': "none"})
    ], className="backlink"),
    html.Table([
        html.Tbody([
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        id = 'pair',
                        options=dropdown_pairs(),
                        multi = False,
                        placeholder="Choisissez une paire"
                    )
                ),
                html.Td(
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date(2020, 1, 2),
                        max_date_allowed=date.today(),
                        start_date=date(2021, 1, 2),
                        end_date=date.today()
                    )                   
                )
            ])
        ])
    ], className="main"),    
    
    
    html.Div(dcc.Graph(id='page-1-graph')),
    
], className='page historical')

@app.callback(
    Output(component_id='page-1-graph', component_property='figure'),
    # En fait, le nom des component id sera important dans le html, mais dans le callback, il n'est pas nécessaire de respecter une nomenclature particulière
    [
        Input(component_id='pair', component_property='value'),
        Input(component_id='my-date-picker-range', component_property='start_date'),
        Input(component_id='my-date-picker-range', component_property='end_date')
    ]
            
)
def update_graph(pair, start_date, end_date):
    if pair is None:
        return go.Figure()
    start = None
    end = None
    if start_date is not None:
        start = date.fromisoformat(start_date)
    if end_date is not None:
        end = date.fromisoformat(end_date)
    
    df = getdata(pair, start, end)
    # Création de la figure plotly
    fig = drawgraph(df)    
    
    return fig