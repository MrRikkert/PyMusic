import altair as alt
import dash_alternative_viz as dav
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output
from pony.orm import db_session

from app.app import app
from app.colors import streamgraph as colors
from app.utils import get_agg, get_df_from_sql


def get_layout():
    def get_card():
        return (
            dbc.Card(
                dbc.CardBody(dav.VegaLite(id="streamgraph")),
                color="light",
                outline=True,
                style={
                    "overflow": "auto",
                    "width": "95vw",
                    "position": "relative",
                    "left": "calc(-1 * (95vw - 100%)/2)",
                },
                class_name="align-items-center",
            ),
        )

    return get_card()


@app.callback(Output("streamgraph", "spec"), Input("use-playtime", "value"))
@db_session
def _get_streamgraph(playtime):
    sql = f"""
    SELECT
        "date",
        "tag_type",
        "name" AS "album",
        "plays" AS "length"
    FROM (
        SELECT
            "date",
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
                date_trunc('week', sc.date) as "date",
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
            GROUP BY "date", sc.id
        ) x
        GROUP BY "date", tag_type, "name", "type"
        ORDER BY "date", "plays" DESC
    ) y
    """
    df = get_df_from_sql(sql, None, None, where=False, parse_dates="date")
    df.index = df["date"]

    df = df.groupby("album").resample("D").mean(numeric_only=True).reset_index()

    d = df.set_index(["date", "album"])
    midx = pd.MultiIndex.from_product(
        [pd.date_range(df["date"].min(), df["date"].max()), df["album"].unique()],
        names=d.index.names,
    )
    df = d.reindex(midx, fill_value=0).reset_index()

    dfs = []
    for album in df["album"].unique():
        try:
            _df = df.loc[df["album"] == album].copy()
            _df2 = _df.copy()
            _df["length"] = _df["length"].interpolate(method="linear")
            _df.index = _df["date"]
            _df["length"] = _df["length"].clip(0, _df2["length"].max())
            _df["length"] = (
                _df["length"]
                .rolling(
                    window=60,
                    win_type="gaussian",
                    closed="neither",
                    center=True,
                    min_periods=1,
                )
                .mean(std=20)
            )
            dfs.append(_df)
        except Exception as e:
            print(e)

    df = pd.concat(dfs).reset_index(drop=True)

    alt.data_transformers.disable_max_rows()
    alt.themes.enable("dark")
    return (
        alt.Chart(df)
        .mark_area()
        .encode(
            alt.X("date:T", axis=alt.Axis(format="%b, %Y", domain=False, tickSize=0)),
            alt.Y("length:Q", stack="center", axis=None),
            alt.Color("album:N", legend=None),
            tooltip=["album", "date"],
        )
        .configure_range(category={"scheme": colors})
        .properties(width=3000, height=500)
        .to_dict()
    )
