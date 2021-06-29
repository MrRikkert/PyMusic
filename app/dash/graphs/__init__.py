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
    Output("top-albums", "figure"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@set_theme
@convert_dates
@db_session
def top_albums(min_date, max_date):
    sql = """
    SELECT a.name_alt, SUM(s.length) AS length
    FROM scrobble sc
    INNER JOIN album a
        ON sc.album = a.id
    INNER JOIN song s
        ON s.id = sc.song
    WHERE length IS NOT NULL :date:
    GROUP BY a.name_alt, sc.album
    ORDER BY length DESC
    LIMIT 5
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    df = df.rename(columns={df.columns[0]: "Album", df.columns[1]: "Hours"})
    df = df.sort_values("Hours", ascending=True)
    df, scale = set_length_scale(df, "Hours")

    fig = px.bar(
        df,
        x="Hours",
        y="Album",
        orientation="h",
        title="Top Albums",
        hover_data=["Hours"],
        text="Album",
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
