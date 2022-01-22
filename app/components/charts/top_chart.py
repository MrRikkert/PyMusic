import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, State
from pony.orm import db_session

from app.app import app
from app.utils import (
    get_agg,
    get_default_graph,
    get_df_from_sql,
    get_min_max_date,
    set_length_scale,
)


def get_layout(_type, reverse=False):
    def get_card(id, className=""):
        return (
            dbc.Card(
                dbc.CardBody(get_default_graph(id=id, className=className)),
                color="light",
                outline=True,
                className="top-chart",
                style={"height": "220px"},
            ),
        )

    if _type == "mixed":
        _id = "top-mixed-chart"
    elif _type == "artist":
        _id = "top-artist-chart"
    elif _type == "album":
        _id = "top-album-chart"

    if reverse:
        return get_card(_id, "reversed")
    return get_card(_id)


def _get_graph(df, x, y, title, xaxis_title, className=""):
    fig = px.bar(
        df, x=x, y=y, orientation="h", title=title, hover_data=["Time"], text=y
    )
    fig.update_layout(
        xaxis=dict(title=xaxis_title), uniformtext=dict(minsize=13, mode="show")
    )
    fig.update_traces(textposition="inside", insidetextanchor="start", textangle=0)
    fig.update_yaxes(showticklabels=False)
    if "reversed" in className:
        fig.update_xaxes(autorange="reversed")

    return fig


@app.callback(
    Output("top-mixed-chart", "figure"),
    Input("date-select", "value"),
    Input("use-playtime", "value"),
    State("date-range-select", "value"),
)
@db_session
def _top_tag(min_date, playtime, date_range):
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
    min_date, max_date = get_min_max_date(min_date, date_range)
    df = get_df_from_sql(sql, min_date, max_date, parse_dates=["Date"])
    df = df.rename(
        columns={df.columns[0]: "Type", df.columns[1]: "Name", df.columns[2]: "Time"}
    )
    df = df.sort_values("Time", ascending=True)
    df, scale = set_length_scale(df, "Time", playtime)

    if playtime:
        title = "Top tag (playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top tag (plays)"
        xaxis_title = "Total Plays"

    return _get_graph(df=df, x="Time", y="Name", title=title, xaxis_title=xaxis_title)
