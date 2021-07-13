import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import (
    add_date_clause,
    convert_dates,
    get_agg,
    get_default_graph,
    set_length_scale,
    set_theme,
)
from app.db.base import db
from dash.dependencies import Input, Output
from pony.orm import db_session


def get_layout(_type, reverse=False):
    def get_card(id, className=""):
        return (
            dbc.Card(
                dbc.CardBody(get_default_graph(id=id, className=className)),
                color="light",
                outline=True,
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
        xaxis_title=xaxis_title, uniformtext_minsize=13, uniformtext_mode="show"
    )
    fig.update_traces(textposition="inside", insidetextanchor="start", textangle=0)
    fig.update_yaxes(showticklabels=False)
    if "reversed" in className:
        fig.update_xaxes(autorange="reversed")

    return fig


@app.callback(
    Output("top-mixed-chart", "figure"),
    Input("top-tags", "data"),
    Input("top-tags-scale", "data"),
    Input("top-mixed-chart", "className"),
    Input("use-playtime", "checked"),
)
@set_theme
def _top_tag(df, scale, className, playtime):
    df = pd.read_json(df, orient="split")
    if playtime:
        title = "Top tag (playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top tag (plays)"
        xaxis_title = f"Total Plays"

    return _get_graph(
        df=df,
        x="Time",
        y="Name",
        title=title,
        xaxis_title=xaxis_title,
        className=className,
    )


@app.callback(
    Output("top-artist-chart", "figure"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("top-artist-chart", "className"),
    Input("use-playtime", "checked"),
)
@set_theme
@convert_dates
@db_session
def _top_artist(date_range, min_date, className, playtime, max_date):
    sql = f"""
    SELECT
        a.name_alt,
        {get_agg(playtime)}(s.length) AS "length"
    FROM scrobble sc
    INNER JOIN song s
        ON sc.song = s.id
    INNER JOIN artistdb_songdb a_s
        ON a_s.songdb = s.id
    INNER JOIN artist a
        ON a_s.artistdb = a.id
    WHERE "length" IS NOT NULL
        :date:
    GROUP BY a.name_alt
    ORDER BY "length" desc
    LIMIT 5
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    df = df.rename(columns={df.columns[0]: "Artist", df.columns[1]: "Time"})
    df = df.sort_values("Time", ascending=True)
    df, scale = set_length_scale(df, "Time", playtime)

    if playtime:
        title = "Top artist (playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top artist (plays)"
        xaxis_title = f"Total Plays"

    return _get_graph(
        df=df,
        x="Time",
        y="Artist",
        title=title,
        xaxis_title=xaxis_title,
        className=className,
    )


@app.callback(
    Output("top-album-chart", "figure"),
    Input("top-albums", "data"),
    Input("top-albums-scale", "data"),
    Input("top-album-chart", "className"),
    Input("use-playtime", "checked"),
)
@set_theme
def _top_album(df, scale, className, playtime):
    df = pd.read_json(df, orient="split")

    if playtime:
        title = "Top albums (Playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top albums (plays)"
        xaxis_title = f"Total Plays"

    return _get_graph(
        df=df,
        x="Time",
        y="Album",
        title=title,
        xaxis_title=xaxis_title,
        className=className,
    )
