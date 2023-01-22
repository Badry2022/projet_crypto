# teams.py

from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import __main__

app = __main__.app

STATS_FIELDS = (
    "mp",
    "pts",
    "orb",
    "drb",
    "ast",
    "stl",
    "blk",
    "tov",
    "pf"
)
STATS_LABELS = (
    "Minutes jouées",
    "Points marqués",
    "Rebonds offensifs",
    "Rebonds défensifs",
    "Passes",
    "Interceptions",
    "Contres",
    "Pertes de balle",
    "Fautes"
)
STATS_LABEL_BY_FIELD = {k: v for k, v in zip(STATS_FIELDS, STATS_LABELS)}
POSITION_DICT = {0: "tous postes", ** {(idx+1): pos for idx, pos in enumerate(__main__.df["pos"].unique())}}

def dropdown_stats():
    dropdown = [{'label': label, 'value': field} for label, field in zip(STATS_LABELS, STATS_FIELDS)]
    return dropdown

    
layout = html.Div(children=[
    html.H1("Comparatif d'équipes"),
    html.Div([
        dcc.Link("< Retour", href='/', style={'textDecoration': "none"})
    ], className="backlink"),
    html.Table([
        html.Thead(
            html.Tr([
                html.Th('Statistique 1'),
                html.Th('Statistique 2')
            ])
        ),
        html.Tbody([
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        id = 'dropdown-stats1',
                        options=dropdown_stats(),
                        multi = False,
                        placeholder="Choisissez une statistique"
                    )
                ),
                html.Td(
                    dcc.Dropdown(
                        id = 'dropdown-stats2',
                        options=dropdown_stats(),
                        multi = False,
                        placeholder="Choisissez une statistique"
                    )                    
                )
            ])
        ])
    ], className="main"),
    html.Div([
        dcc.Slider(
            id = 'slider-position',
            step = None,
            value = 0,
            marks = POSITION_DICT
        )
    ]),
    html.Div([
        dcc.Graph(
            id = 'graph-result',
            figure = go.Figure(data=[go.Scatter(x=[], y=[])])
        )
    ], id="graph-result-wrapper", className="hidden")
], style={'textAlign': 'center'})

@app.callback(Output(component_id='graph-result-wrapper', component_property='className'),
            [Input(component_id='dropdown-stats1', component_property='value'), Input(component_id='dropdown-stats2', component_property='value')])
def update_visibility(stats_id_1, stats_id_2):
    if stats_id_1 is None:
        return "hidden"
    elif stats_id_2 is None:
        return "hidden"
    return "visible"

@app.callback(
    Output(component_id='graph-result', component_property='figure'),
    [
        Input(component_id='dropdown-stats1', component_property='value'),
        Input(component_id='dropdown-stats2', component_property='value'),
        Input(component_id='slider-position', component_property='value')
    ])
def update_graph(stats_id_1, stats_id_2, position_value):
    if stats_id_1 is None:
        return go.Figure(data=[go.Scatter(x=[], y=[])])
    elif stats_id_2 is None:
        return go.Figure(data=[go.Scatter(x=[], y=[])])
    df = __main__.df
    position_field = POSITION_DICT[position_value]
    position_label = position_field
    if position_value == 0:
        df_bypos = df
    else:
        df_bypos = df[df["pos"] == position_label]
        position_label = "poste " + position_label
    data1 = df_bypos.groupby("bref_team_id").sum(numeric_only=True)[stats_id_1].sort_values(ascending=False).iloc[:5]
    data2 = df_bypos.groupby("bref_team_id").sum(numeric_only=True)[stats_id_2].sort_values(ascending=False).iloc[:5]
    fig = make_subplots(rows=1, cols=2, subplot_titles=(STATS_LABEL_BY_FIELD[stats_id_1], STATS_LABEL_BY_FIELD[stats_id_2]))
    fig.add_trace(
        go.Bar(x=data1.index, y=data1),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=data2.index, y=data2),
        row=1, col=2
    )
    fig.update_layout(title=f"Statistiques par équipe ({position_label})", title_x=0.5, showlegend=False)
    return fig


