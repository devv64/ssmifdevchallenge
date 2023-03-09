# Run this app with `python3 app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
from LiveMarketData import *
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
from dash.exceptions import PreventUpdate



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# creating navbar
navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    # dbc.Col(html.Img(src="/assets/logo.png", height="30px")),
                    dbc.Col(dbc.NavbarBrand("PR0FIT P0RTAL", style={'margin-left': 40, 'font-size': '28px'})),
                ],
                align="center",
            ),
            href="/",
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Home", href="/", className='nav-link',
                 style={'border': '1px solid #ddd'})),
                dbc.NavItem(dbc.NavLink("About", href="/about", className='nav-link', 
                 style={'border': '1px solid #ddd'})),
                dbc.NavItem(dbc.NavLink("Contact", href="/contact", className='nav-link', 
                 style={'border': '1px solid #ddd'})),
            ],
            className="navbar navbar-expand-lg navbar-dark bg-dark",
            style={'margin-left': 950},
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
    sticky="top",
)

stockInput = html.Div([
        dcc.Input(
            id="inputStock".format('text'),
            type='text',
            placeholder="Ticker Name".format('text'),
            debounce=True,
            style={'margin-left': 1000}
        ),
        dcc.Input(
            id="inputShares".format('number'),
            type='number',
            placeholder="Shares Amount".format('number'),
            debounce=True
        ),
        html.Button(
            'Submit', id='submit-val', n_clicks=0
        )
    ]
    + [html.Div(id="output")]
    + [dcc.Graph(id="graph", style={'display': 'none'})]
)

# ****************************** #
# Callbacks (creating table and graph)

@app.callback(
    Output("output", "children"),
    Input("submit-val", "n_clicks"),
    State("inputStock", "value"),
    State("inputShares", "value")
)
def tableOutput(n_clicks,stock,shares):
    if stock:
        tic = yf.Ticker(stock)
        info = tic.history(period='7d',interval='1d')
        if len(info) == 0:
            return dbc.Alert("Not a valid ticker", color="danger")
        if shares == None:
            return dbc.Alert("Input amount of shares", color="danger")
        curStock = CurrentMarket(stock, "STOCK")
        change = curStock.Change()
        OYE = curStock.OneYearTarget()
        stockVal = curStock.Price() * shares
        d = {'Ticker': stock.upper(), 'Shares': shares, 'Total Value': stockVal, "Today's Change": change, 'One Year Estimate': OYE}
        df = pd.DataFrame(data=d, index=[0])
        return html.Div(
            [
                dash_table.DataTable(
                    data=df.to_dict("rows"),
                    columns=[{"id": x, "name": x} for x in df.columns],
                )
            ]
        )

@app.callback(
    Output("graph", "figure"), 
    Input("submit-val", "n_clicks"),
    State("inputStock", "value"),
    prevent_initial_call=True
    )
def display_candlestick(n_clicks, stock):
    data = yf.download(stock, start="2020-01-01", end="2023-03-08")
    df = pd.DataFrame(data)
    df.reset_index(inplace=True)
    fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

    return fig


@app.callback(
    Output("graph", "style"), 
    [Input("submit-val", "n_clicks"), Input("inputStock", "value")],
    prevent_initial_call=True
)
def update_graph_visibility(n_clicks, stock):
    time.sleep(1.285)
    if not stock or n_clicks == 0:
        raise PreventUpdate
    return {'display': 'block'}



# ****************************** #
# Layout (structuring page)


# Having trouble getting the spinner to not show up when only a stock name is typed in
app.layout = html.Div([
    navbar,
    # dbc.Spinner(
    html.Div([
        html.Div([
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Stock Input"),
                                    html.Div([
                                        dcc.Input(
                                            id="inputStock".format('text'),
                                            type='text',
                                            placeholder="Ticker Name".format('text'),
                                            debounce=True
                                        ),
                                        dcc.Input(
                                            id="inputShares".format('number'),
                                            type='number',
                                            placeholder="Shares Amount".format('number'),
                                            debounce=True
                                        ),
                                        html.Button(
                                            'Submit', id='submit-val', n_clicks=0
                                        ),
                                    ],
                                        style={'margin-bottom': '10px'}
                                    ),
                                    html.Div(id="output", style={'margin': 'auto'}),
                                ],
                                style={'border': '1px solid #ddd', 'padding': '10px', 'width': '100%', 'margin': 'auto'}
                            )
                        ],
                        md=4,
                        style={'margin-right': '10px'}
                    ),
                    dbc.Col(
                        dcc.Graph(id="graph", style={'display': 'none'}),
                        md=8
                    ),
                ],
                style={'margin-top': '50px'}
            )
        ], style={'text-align': 'center'})
    ])
    # , type="grow", color="primary", fullscreen=False),
])




if __name__ == '__main__':
    app.run_server(debug=True)
