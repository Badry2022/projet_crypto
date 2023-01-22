# players.py

import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import __main__

app = __main__.app

STATS_FIELDS = (
    "age",
    "bref_team_id",
    "pos",
    "mp",
    "pts",
    "fg.",
    "efg.",
    "ft.",
    "orb",
    "drb",
    "ast",
    "stl",
    "blk",
    "tov",
    "pf"
)
STATS_LABELS = (
    "Âge",
    "Équipe",
    "Poste",
    "Minutes jouées",
    "Points marqués",
    "% tirs marqués",
    "% tir à 3 pts",
    "% lancers-francs",
    "Rebonds offensifs",
    "Rebonds défensifs",
    "Passes",
    "Interceptions",
    "Contres",
    "Pertes de balle",
    "Fautes"
)

def dropdown_rookies():
    df = __main__.df
    return [{'label': row["player"], 'value': index} for index, row in df[df["age"] < 24].iterrows()]


def dropdown_seniors():
    df = __main__.df
    return [{'label': row["player"], 'value': index} for index, row in df[df["age"] >= 24].iterrows()]

    
layout = html.Div(children=[
    html.H1('Comparatif de joueurs'),
    html.Div([
        dcc.Link("< Retour", href='/', style={'textDecoration': "none"})
    ], className="backlink"),
    html.Table([
        html.Thead(
            html.Tr([
                html.Th('Rookies'),
                html.Th('Seniors')
            ])
        ),
        html.Tbody([
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        id = 'dropdown-rookie',
                        options=dropdown_rookies(),
                        multi = False,
                        placeholder="Choisissez un rookie"
                    )
                ),
                html.Td(
                    dcc.Dropdown(
                        id = 'dropdown-senior',
                        options=dropdown_seniors(),
                        multi = False,
                        placeholder="Choisissez un senior"
                    )                    
                )
            ])
        ])
    ], className="main"),
    html.Div("", id="comparison-table")
], style={'textAlign': 'center'})

@app.callback(Output(component_id='comparison-table', component_property='children'),
            [Input(component_id='dropdown-rookie', component_property='value'), Input(component_id='dropdown-senior', component_property='value')])
def update_rookie(rookie_id, senior_id):
    if rookie_id is None:
        return ""
    elif senior_id is None:
        return ""
    
    rookie = __main__.df.loc[int(rookie_id)]
    senior = __main__.df.loc[int(senior_id)]

    rows = []
    for label, field in zip(STATS_LABELS, STATS_FIELDS):
        rows.append(html.Tr([
            html.Td(label, className="label left"),
            html.Td(rookie[field]),
            html.Td(senior[field]),
            html.Td(label, className="label right")
        ]))
    return html.Table([
        html.Thead(
            html.Tr([
                html.Th('', className="label left"),
                html.Th(rookie["player"]),
                html.Th(senior["player"]),
                html.Th('', className="label right")
            ])
        ),
        html.Tbody(rows)
    ])
