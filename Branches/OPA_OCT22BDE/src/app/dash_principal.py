import dash
from dash import dcc, html
from dash.dependencies import Output,Input

app = dash.Dash(__name__,suppress_callback_exceptions=True)

# Layout Principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id = 'page-content')
])

index_page = html.Div([
    html.H1('Dashboard pour Binance'),
    dcc.Link(html.Div("Données historiques", className="btn"), href='/historical', style={'textDecoration': "none"}),
    html.Br(),
    dcc.Link(html.Div("Données live", className="btn"), href='/live', style={'textDecoration': "none"}),
], style={'textAlign': 'center', 'width': '50%', 'marginRight': '50%'})


# Mise à jour de l'index
from dash_historical import layout_1 as historical
from dash_live import layout_2  as live


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/historical':
        return historical
    elif pathname == '/live':
        return live
    else:
        return index_page



if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")