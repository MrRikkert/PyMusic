import os

import dash
import dash_bootstrap_components as dbc
from flask import Flask

assets_path = os.getcwd() + "/app/assets/"
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
)

server = Flask(__name__)
app = dash.Dash(
    server=server,
    assets_folder=assets_path,
    external_stylesheets=[dbc.themes.DARKLY, dbc_css],
)
