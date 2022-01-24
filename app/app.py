import os

import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from flask import Flask
import plotly.io as pio
import plotly.graph_objects as go

assets_path = os.getcwd() + "/app/assets/"
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
)

load_figure_template("darkly")
pio.templates["myname"] = go.layout.Template(
    layout=dict(
        dragmode=False,
        margin=dict(l=10, r=10, b=10, t=40),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        colorway=["#0567a4", "#0795ED"],
        xaxis=dict(tickfont=dict(color="#adb5bd"), fixedrange=True),
        yaxis=dict(tickfont=dict(color="#adb5bd"), fixedrange=True),
        polar=dict(bgcolor="rgba(0, 0, 0, 0)"),
    )
)
pio.templates.default = "darkly+myname"

server = Flask(__name__)
app = dash.Dash(
    server=server,
    assets_folder=assets_path,
    external_stylesheets=[dbc.themes.DARKLY, dbc_css],
    suppress_callback_exceptions=True,
)
