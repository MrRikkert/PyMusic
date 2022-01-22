import dash_bootstrap_components as dbc
from app.components import navbar, titlebar
from dash import html


def get_layout():
    return html.Div(
        [
            navbar.get_layout(),
            dbc.Container([titlebar.get_layout()], fluid=False, id="main-content"),
        ]
    )
