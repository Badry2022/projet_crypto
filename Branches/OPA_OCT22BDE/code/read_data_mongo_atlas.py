from mongo import MongoAtlas
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

connexion = MongoAtlas()

dbase = connexion.create_database('financeDB')

collection_name = "BTC_USDT_1d"

print(dbase[collection_name].count_documents({}))

df = pd.DataFrame(list(dbase[collection_name].find()))

df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

print(df.iloc[-10:])

#Graphe des cours
"""candlestick=go.Candlestick(x=df['Time'],
open = df['Open'],
high = df['High'],
low = df['Low'],
close = df['Close'],
yaxis='y1',
showlegend=False)

#Graphe du volume
df.loc[df.Open < df.Close, "Color"] = "green"
df.loc[df.Open >= df.Close, "Color"] = "red"
volume = go.Bar(x=df['Time'],
y=df['Volume'],
yaxis='y2',
showlegend=False,
marker_color=df['Color']
)

#Organiser le rendu
fig = make_subplots(rows=2, 
cols=1, 
shared_xaxes=True,
vertical_spacing=0.01,
row_heights=[0.8,0.2])
fig.add_trace(candlestick, row=1, col=1)
fig.add_trace(volume, row=2, col=1)


fig.update_layout(
     xaxis=dict(
          rangeselector=dict(
               buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")])),
               rangeslider=dict(visible=False),
               type="date"
          ),
     bargap=0
)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)

fig.show()"""