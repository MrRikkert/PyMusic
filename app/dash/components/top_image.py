import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates
from app.db.base import db
from dash.dependencies import Input, Output
from pony.orm import db_session
from app.settings import IMG_URL


def get_layout(_type):
    def get_card(title, name_id, art_id, artist_id=None):
        return dbc.Card(
            [
                html.Div(title, className="title"),
                dbc.CardImg(
                    src="/assets/img/placeholder_album_art.png", id=art_id, top=True
                ),
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
        art_id = "top-series-image-art"
        return get_card("Top series", name_id, art_id)
    elif _type == "album":
        name_id = "top-album-image-name"
        art_id = "top-album-image-art"
        artist_id = "top-album-image-artist"
        return get_card("Top album", name_id, art_id, artist_id)
    elif _type == "artist":
        name_id = "top-artist-image-name"
        art_id = "top-artist-image-art"
        return get_card("Top artist", name_id, art_id)


@app.callback(
    Output("top-series-image-name", "children"),
    Output("top-series-image-art", "src"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def _top_image_series_stats(min_date, max_date):
    return ("Attack on Titan", "/assets/img/placeholder_album_art.png")


@app.callback(
    Output("top-album-image-name", "children"),
    Output("top-album-image-art", "src"),
    Output("top-album-image-artist", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def _top_image_album_stats(min_date, max_date):
    sql = """
    SELECT
        al.name_alt AS "album",
        al.art,
        ar.name_alt AS "artist",
        SUM(s.length) AS "length"
    FROM scrobble sc
    INNER JOIN song s
        ON s.id = sc.song
    INNER JOIN album al
        ON sc.album = al.id
    LEFT JOIN artist ar
        ON ar.id = al.album_artist
    WHERE "length" IS NOT NULL :date:
    GROUP BY al.name_alt, al.art, ar.name_alt
    ORDER BY "length" DESC
    LIMIT 1
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    ).iloc[0]
    art = IMG_URL + df.art
    return (df.album, art, df.artist)


@app.callback(
    Output("top-artist-image-name", "children"),
    Output("top-artist-image-art", "src"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def _top_image_artist_stats(min_date, max_date):
    return ("Hiroyuki Sawano", "/assets/img/placeholder_album_art.png")
