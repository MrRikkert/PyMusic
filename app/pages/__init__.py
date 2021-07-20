from app import data_callbacks
from app.components import navbar
from app.pages import listening_report
import dash_core_components as dcc
import dash_html_components as html
from app.app import app
from dash.dependencies import Input, Output, State


def get_layout():
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            navbar.get_layout(),
            html.Div(id="page-content"),
            data_callbacks.get_layout(),
        ]
    )


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def _get_page(url):
    if url == "/":
        return listening_report.get_layout()
    elif url == "/listening-report":
        return listening_report.get_layout()
