from ast import Div
import dash_bootstrap_components as dbc
import dash_html_components as html
from app.dash.app import app
from app.dash.utils import convert_dates
from dash.dependencies import Input, Output
from pony.orm import db_session


def get_layout(_type):
    def get_card(title, name_id, artist_id=None):
        return dbc.Card(
            [
                html.Div(title, className="title"),
                dbc.CardImg(src="/assets/img/album.png", top=True),
                html.Div(
                    [
                        html.Div(id=name_id),
                        html.Div(id=artist_id, className="artist")
                        if artist_id
                        else None,
                    ],
                    className="name",
                ),
            ],
            color="light",
            outline=True,
            className="top-image",
        )

    if _type == "series":
        name_id = "top-series-image-name"
        return get_card("Top series", name_id)
    elif _type == "album":
        name_id = "top-album-image-name"
        artist_id = "top-album-image-artist"
        return get_card("Top album", name_id, artist_id)
    elif _type == "artist":
        name_id = "top-artist-image-name"
        return get_card("Top artist", name_id)


@app.callback(
    Output("top-series-image-name", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def _top_image_series_stats(min_date, max_date):
    return "Attack on Titan"


@app.callback(
    Output("top-album-image-name", "children"),
    Output("top-album-image-artist", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def _top_image_album_stats(min_date, max_date):
    return ("Attack on Titan Season 3 Original Soundtrack", "Hiroyuki Sawano")


@app.callback(
    Output("top-artist-image-name", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def _top_image_artist_stats(min_date, max_date):
    return "Hiroyuki Sawano"
