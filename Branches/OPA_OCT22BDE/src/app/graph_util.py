import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fonction pour créer le graphique
def drawgraph(df):
    candlestick = go.Candlestick(
        x=df['Time'],
        open = df['Open'],
        high = df['High'],
        low = df['Low'],
        close = df['Close'],
        yaxis='y1',
        showlegend=False
    )

    #Graphe du volume
    df.loc[df.Open < df.Close, "Color"] = "green"
    df.loc[df.Open >= df.Close, "Color"] = "red"
    #
    volume = go.Bar(
        x=df['Time'],
        y=df['Volume'],
        yaxis='y2',
        showlegend=False,
        marker_color=df['Color']
    )

    #Organiser le rendu
    fig = make_subplots(rows=2, 
        cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.25,
        row_heights=[0.6,0.4]
    )
    
    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(volume, row=2, col=1)

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_layout(height=720)

    # fig.show()

    return fig