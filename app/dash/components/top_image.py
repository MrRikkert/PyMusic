import dash_bootstrap_components as dbc
import dash_html_components as html
from app.dash.app import app
from app.dash.utils import convert_dates
from dash.dependencies import Input, Output
from pony.orm import db_session


@app.callback(
    Output("top-series", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def get_stats(min_date, max_date):
    return dbc.Card(
        [
            html.Div("Series", className="title"),
            dbc.CardImg(src="/assets/img/album.png", top=True),
            html.Div("Attack on Titan", className="name"),
        ],
        color="light",
        outline=True,
        className="top-image",
    )
