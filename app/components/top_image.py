import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from pony.orm import db_session

from app.app import app
from app.utils import add_date_clause, convert_dates, get_agg
from shared.db.base import db
from shared.settings import IMG_URL


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
        return get_card("Top tag", name_id, art_id)
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
    Input("top-tags", "data"),
    State("date-range-select", "value"),
    State("date-select", "value"),
    State("use-playtime", "value"),
)
@convert_dates
@db_session
def _top_image_tags_stats(df, date_range, min_date, playtime, max_date):
    df = pd.read_json(df, orient="split")

    sql = f"""
    SELECT art
    FROM album a
    INNER JOIN albumdb_songdb a_s
        ON a_s.albumdb = a.id
    INNER JOIN song s
        ON a_s.songdb = s.id
    INNER JOIN scrobble sc
        ON sc.song = s.id
    INNER JOIN songdb_tagdb s_t
        ON s_t.songdb = s.id
    INNER JOIN tag t
        ON s_t.tagdb = t.id
    WHERE t.value = %(tag)s
        :date:
    GROUP BY art
    ORDER BY {get_agg(playtime)}(s.length) DESC
    LIMIT 1
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df_art = pd.read_sql_query(
        sql,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date, "tag": df.iloc[-1]["Name"]},
    ).iloc[0]
    art = IMG_URL + df_art.art

    return (df.iloc[-1]["Name"], art)


@app.callback(
    Output("top-album-image-name", "children"),
    Output("top-album-image-art", "src"),
    Output("top-album-image-artist", "children"),
    Input("top-albums", "data"),
)
def _top_image_album_stats(df):
    df = pd.read_json(df, orient="split")

    top = df.iloc[-1]
    art = IMG_URL + top.Art
    return (top.Album, art, top.Artist)


@app.callback(
    Output("top-artist-image-name", "children"),
    Output("top-artist-image-art", "src"),
    Input("top-artists", "data"),
)
def _top_image_artist_stats(df):
    df = pd.read_json(df, orient="split")

    top = df.iloc[-1]
    art = IMG_URL + top.Art
    return (top.Artist, art)
