from datetime import datetime
from inspect import getfullargspec

import dash_core_components as dcc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates, set_theme, set_length_scale
from app.db.base import db
from dash.dependencies import Input, Output
from pony.orm import db_session


def get_default_graph(id: str):
    fig = px.bar()
    fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=40),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        template="plotly_dark",
    )
    return dcc.Graph(figure=fig, id=id)


@app.callback(
    Output("top-mixed", "figure"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@set_theme
@convert_dates
@db_session
def top_mixed(min_date, max_date):
    sql = """
    SELECT
        tag_type,
        CASE
            WHEN franchise IS NOT NULL THEN franchise
            WHEN sort_artist IS NOT NULL THEN sort_artist
            WHEN "type" IS NOT NULL THEN "type"
        END AS "name",
        SUM("length") AS plays
    FROM (
        SELECT
            sc.id,
            s.length,
            MAX(CASE WHEN t.tag_type = 'franchise' THEN t.value END) AS "franchise",
            MAX(CASE WHEN t.tag_type = 'sort_artist' THEN t.value END) AS "sort_artist",
            MAX(CASE WHEN t.tag_type = 'type' THEN t.value END) AS "type",
            MIN(
                CASE
                    WHEN t.tag_type = 'franchise' THEN 'Franchise'
                    WHEN t.tag_type = 'sort_artist' THEN 'Artist'
                    WHEN t.tag_type = 'type' THEN 'Type'
                END
            ) AS tag_type
        FROM scrobble sc
        INNER JOIN song s
            ON s.id = sc.song
        INNER JOIN songdb_tagdb st
            ON s.id = st.songdb
        INNER JOIN tag t
            ON t.id = st.tagdb
        :date:
        GROUP BY sc.id, s.length
    ) x
    GROUP BY "name", tag_type
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
    df, scale = set_length_scale(df, "Time")

    fig = px.bar(
        df,
        x="Time",
        y="Name",
        orientation="h",
        title="Top Series/Artist/Type",
        hover_data=["Time"],
        text="Name",
        height=200,
    )
    fig.update_layout(
        xaxis_title=f"Total Playtime ({scale})",
        uniformtext_minsize=8,
        uniformtext_mode="show",
    )
    fig.update_traces(textposition="inside", insidetextanchor="start")
    fig.update_xaxes(autorange="reversed")
    fig.update_yaxes(showticklabels=False)

    return fig
