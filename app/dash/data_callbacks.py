import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from pony.orm import db_session

from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates, get_agg, set_length_scale
from app.db.base import db
from dash.dependencies import Input, Output


def get_layout():
    return html.Div(
        [
            dcc.Store("top-tags"),
            dcc.Store("top-tags-scale"),
            dcc.Store("top-albums"),
            dcc.Store("top-albums-scale"),
            dcc.Store("top-artists"),
            dcc.Store("top-artists-scale"),
        ]
    )


@app.callback(
    Output("top-tags", "data"),
    Output("top-tags-scale", "data"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("top-mixed-chart", "className"),
    Input("use-playtime", "value"),
)
@convert_dates
@db_session
def _top_tags(date_range, min_date, className, playtime, max_date):
    sql = f"""
    SELECT
        CASE
            WHEN franchise IS NOT NULL THEN 'franchise'
            WHEN sort_artist IS NOT NULL THEN 'sort_artist'
            WHEN "type" IS NOT NULL THEN 'type'
        END AS "tag_type",
        CASE
            WHEN franchise IS NOT NULL THEN franchise
            WHEN sort_artist IS NOT NULL THEN sort_artist
            WHEN "type" IS NOT NULL THEN "type"
        END AS "name",
        {get_agg(playtime)}(agg) plays
    FROM (
        SELECT
            MIN(s.length) AS agg,
            MIN(franchise.value) AS franchise,
            MIN(sort_artist.value) AS sort_artist,
            MIN("type".value) AS "type"
        FROM scrobble sc
        INNER JOIN song s
            ON s.id = sc.song
        INNER JOIN songdb_tagdb st
            ON s.id = st.songdb
        LEFT JOIN tag franchise
            ON franchise.id = st.tagdb AND franchise.tag_type = 'franchise'
        LEFT JOIN tag sort_artist
            ON sort_artist.id = st.tagdb AND sort_artist.tag_type = 'sort_artist'
        LEFT JOIN tag "type"
            ON "type".id = st.tagdb AND "type".tag_type = 'type'
        :date:
        GROUP BY sc.id
    ) x
    GROUP BY tag_type, "name", "type"
    ORDER BY plays DESC
    LIMIT 5
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    df = df.rename(
        columns={df.columns[0]: "Type", df.columns[1]: "Name", df.columns[2]: "Time"}
    )
    df = df.sort_values("Time", ascending=True)
    df, scale = set_length_scale(df, "Time", playtime)
    return df.to_json(date_format="iso", orient="split"), scale


@app.callback(
    Output("top-albums", "data"),
    Output("top-albums-scale", "data"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("use-playtime", "value"),
)
@convert_dates
@db_session
def _top_albums(date_range, min_date, playtime, max_date):
    sql = f"""
    SELECT
        al.name_alt AS "album",
        al.art,
        ar.name_alt AS "artist",
        {get_agg(playtime)}(s.length) AS "length"
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
    LIMIT 5
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    df = df.rename(
        columns={
            df.columns[0]: "Album",
            df.columns[1]: "Art",
            df.columns[2]: "Artist",
            df.columns[3]: "Time",
        }
    )
    df = df.sort_values("Time", ascending=True)
    df, scale = set_length_scale(df, "Time", playtime)
    return df.to_json(date_format="iso", orient="split"), scale


@app.callback(
    Output("top-artists", "data"),
    Output("top-artists-scale", "data"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("use-playtime", "value"),
)
@convert_dates
@db_session
def _top_artists(date_range, min_date, playtime, max_date):
    sql = f"""
    SELECT
        a.name_alt AS "artist",
        {get_agg(playtime)}(s.length) AS "length",
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
            ORDER BY {get_agg(playtime)}(s.length) DESC
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
    LIMIT 5
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    df = df.rename(
        columns={df.columns[0]: "Artist", df.columns[1]: "Time", df.columns[2]: "Art"}
    )
    df = df.sort_values("Time", ascending=True)
    df, scale = set_length_scale(df, "Time", playtime)
    return df.to_json(date_format="iso", orient="split"), scale
