from ast import Div
import dash_bootstrap_components as dbc
import dash_html_components as html
from app.dash.app import app
from app.dash.utils import convert_dates
from dash.dependencies import Input, Output
from pony.orm import db_session


@app.callback(
    Output("top-series", "children"),
    Output("top-album", "children"),
    Output("top-artist", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def get_stats(min_date, max_date):
    def get_card(title, name, artist=None):
        return dbc.Card(
            [
                html.Div(title, className="title"),
                dbc.CardImg(src="/assets/img/album.png", top=True),
                html.Div(
                    [
                        html.Div(name),
                        html.Div(artist, className="artist") if artist else None,
                    ],
                    className="name",
                ),
            ],
            color="light",
            outline=True,
            className="top-image",
        )

    return (
        get_card("Top series", "Attack on Titan"),
        get_card(
            "Top album",
            "Attack on Titan Season 3 Original Soundtrack",
            "Hiroyuki Sawano",
        ),
        get_card("Top artist", "Hiroyuki Sawano"),
    )
