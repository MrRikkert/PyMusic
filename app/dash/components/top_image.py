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
    sql = """
    SELECT
        t.value AS series,
        SUM(s.length) AS "length",
        (
            SELECT a.art
            FROM album a
            INNER JOIN albumdb_songdb a_s
                ON a_s.albumdb = a.id
            INNER JOIN song s
                ON a_s.songdb = s.id
            INNER JOIN songdb_tagdb s_t
                ON s_t.songdb = s.id
            INNER JOIN tag t2
                ON t2.id = s_t.tagdb
            INNER JOIN scrobble sc
                ON sc.song = s.id
            WHERE t2.value = t.value
                :date:
            GROUP BY a.art
            ORDER BY SUM(s.length) DESC
            LIMIT 1
        )
    FROM scrobble sc
    INNER JOIN song s
        ON s.id = sc.song
    INNER JOIN songdb_tagdb s_a
        ON s_a.songdb = s.id
    INNER JOIN tag t
        ON s_a.tagdb = t.id
    WHERE "length" IS NOT NULL
        AND t.tag_type = 'franchise'
        AND t.value != 'Initial D'
        :date:
    GROUP BY t.value
    ORDER BY "length" DESC
    LIMIT 1
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    ).iloc[0]
    art = IMG_URL + df.art
    return (df.series, art)


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
    # Uses top album art like series
    # No easy accessible API to get artist images
    sql = """
    SELECT
        a.name_alt AS "artist",
        SUM(s.length) AS "length",
        (
            SELECT al.art
            FROM album al
            INNER JOIN albumdb_songdb al_s
                ON al_s.albumdb = al.id
            INNER JOIN song s
                ON al_s.songdb = s.id
            INNER JOIN artistdb_songdb ar_s
                ON ar_s.songdb = s.id
            INNER JOIN artist ar
                ON ar_s.artistdb = ar.id
            INNER JOIN scrobble sc
                ON sc.song = s.id
            WHERE ar.name_alt = a.name_alt
                :date:
            GROUP BY al.art
            ORDER BY SUM(s.length) DESC
            LIMIT 1
        )
    FROM scrobble sc
    INNER JOIN song s
        ON s.id = sc.song
    INNER JOIN artistdb_songdb a_s
        ON a_s.songdb = s.id
    INNER JOIN artist a
        ON a_s.artistdb = a.id
    WHERE "length" IS NOT NULL
        :date:
    GROUP BY a.name_alt
    ORDER BY "length" DESC
    LIMIT 1
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    ).iloc[0]
    art = IMG_URL + df.art
    return (df.artist, art)
