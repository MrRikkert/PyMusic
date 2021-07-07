import os

import dash_bootstrap_components as dbc

import dash

assets_path = os.getcwd() + "/app/dash/assets/"

app = dash.Dash(__name__, assets_folder=assets_path)
