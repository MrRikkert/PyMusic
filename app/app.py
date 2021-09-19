import os

import dash
import plotly.graph_objects as go
import plotly.io as pio

from flask import Flask

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
pio.templates.default = "plotly_dark+myname"

assets_path = os.getcwd() + "/app/assets/"

server = Flask(__name__)
app = dash.Dash(server=server, assets_folder=assets_path)
