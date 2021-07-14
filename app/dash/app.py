import os

import plotly.graph_objects as go
import plotly.io as pio

import dash

pio.templates["myname"] = go.layout.Template(
    layout=dict(
        margin=dict(l=10, r=10, b=10, t=40),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        colorway=["#0567a4", "#0795ED"],
        xaxis=dict(tickfont=dict(color="#adb5bd")),
        yaxis=dict(tickfont=dict(color="#adb5bd")),
        polar=dict(bgcolor="rgba(0, 0, 0, 0)"),
    )
)
pio.templates.default = "plotly_dark+myname"

assets_path = os.getcwd() + "/app/dash/assets/"

app = dash.Dash(__name__, assets_folder=assets_path)
