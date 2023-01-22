# dash_app.py

import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
# import plotly.express as px
import pandas as pd

df_raw = pd.read_csv("nba_2013.csv")
df = df_raw[(df_raw["bref_team_id"] != "TOT") & (df_raw["pos"] != "G")]

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True
)

from teams import layout as teams_layout
from players import layout as players_layout

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    # Contenu de la page à modifier 
    html.Div(id='page-content')
])

index_layout = html.Div([
    html.H1("Statistiques NBA 2013"),
    dcc.Link(html.Div("Comparatif de joueurs", className="btn"), href='/players', style={'textDecoration': "none"}),
    html.Br(),
    dcc.Link(html.Div("Comparatif d'équipes", className="btn"), href='/teams', style={'textDecoration': "none"}),
    html.Div(" ", id="bidon")
], style={'textAlign': 'center', 'width': '50%', 'marginLeft': '50%'})

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/players':
        return players_layout
    elif pathname == '/teams':
        return teams_layout
    else:
        return index_layout

app.clientside_callback(
    """
    function setClass(pathname) {
        c = (function() {
            if (pathname == '/players') {
                return "players page"
            } else if (pathname == '/teams') {
                return "teams page"
            } else {
                return "index"
            }
        })()

        console.log("clientside_callback", pathname, c)
        document.getElementsByTagName( 'html' )[0].className = c
        return c
    }
    """,
    output=Output('bidon', 'className'),
    inputs=[Input('url', 'pathname')]
)

if __name__ == '__main__':
    app.run_server(debug = True, host = '0.0.0.0', port = 5080)