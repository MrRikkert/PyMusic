import os

import dash_bootstrap_components as dbc

import dash

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
assets_path = os.getcwd() + "/app/dash/assets/"

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.DARKLY], assets_folder=assets_path
)
