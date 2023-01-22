from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from collections import deque
from datetime import datetime
from kafka import KafkaConsumer

d = deque(maxlen=1200)

kafka_consumer = KafkaConsumer(
    "BTCEUR-1s", consumer_timeout_ms=800, bootstrap_servers="192.168.1.59", auto_offset_reset="earliest", group_id=f"dash-{datetime.now().timestamp():.0f}"
)

def pull_data():
    try:
        for kafka_message in kafka_consumer:
            kline = json.loads(kafka_message.value)
            d.append([int(kline["k"]["t"]), float(kline["k"]["o"]), float(kline["k"]["h"]), float(kline["k"]["l"]), float(kline["k"]["c"])])
    except Exception as e:
        pass

pull_data()

app = Dash(__name__)

df = pd.DataFrame({"c": d})
fig = px.line(df["c"])

app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for your data.
    """
        ),
        dcc.Input(id="nb-values", type="text", value="500"),
        html.Button('Start/Stop', id='start-stop-button'),
        dcc.Graph(id="interval-graph", figure=fig),
        dcc.Store(id='graph-n-values', data=500),
        dcc.Interval(
            id="interval-component", interval=0.3 * 1000, n_intervals=1  # in milliseconds
        ),
    ],
    style={"background-color": "#D5E3EA", "color": "black", "height": "100%", "width": "100%"},
)

@app.callback(
    Output('graph-n-values', 'data'),
    [Input('nb-values', 'value')],
)
def callback_n_values(input_n_values):
    return int(input_n_values)

@app.callback(
    Output('interval-component', 'disabled'),
    [Input('start-stop-button', 'n_clicks')],
    [State('interval-component', 'disabled')],
)
def callback_func_start_stop_interval(button_clicks, disabled_state):
    if button_clicks is not None and button_clicks > 0:
        return not disabled_state
    else:
        return disabled_state

@app.callback(
    Output("interval-graph", "figure"),
    Input("interval-component", "n_intervals"),
    State('graph-n-values', 'data')
)
def update_figure(_, n_values):
    pull_data()

    df = pd.DataFrame(d, columns=['Time', 'Open', 'High', 'Low', 'Close'])
    df["Time"] = pd.to_datetime(df["Time"], unit='ms')
    df = df.iloc[-min(n_values, df.shape[0]):]
    fig = go.Figure(data=[go.Candlestick(x=df['Time'],
    open = df['Open'],
    high = df['High'],
    low = df['Low'],
    close = df['Close'])])

    fig.update_xaxes(title_text = 'Date')
    fig.update_yaxes(title_text = 'Prices')
    fig.update_layout(xaxis_rangeslider_visible=True, 
        title = 'Bitcoin/USDT'
    )

    fig.update_layout(plot_bgcolor="rgb(191,204,210)", paper_bgcolor="rgb(213,227,234)")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

