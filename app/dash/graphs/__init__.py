from datetime import datetime
from inspect import getfullargspec

import dash_core_components as dcc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates, set_theme
from app.db.base import db
from dash.dependencies import Input, Output
from pony.orm import db_session


def get_default_graph(id: str):
    fig = px.bar()
    set_theme(fig)
    return dcc.Graph(figure=fig, id=id)


@app.callback(
    Output("top-albums", "figure"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def top_albums(min_date, max_date):
    sql = """
    SELECT a.name_alt, SUM(s.length) AS length, a.art
    FROM scrobble sc
    INNER JOIN album a
        ON sc.album = a.id
    INNER JOIN song s
        ON s.id = sc.song
    WHERE length IS NOT NULL :date:
    GROUP BY a.name_alt, sc.album, a.art
    ORDER BY length DESC
    LIMIT 10
    """
    sql = add_date_clause(sql, min_date, max_date)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    df = df.rename(columns={df.columns[0]: "Album", df.columns[1]: "Hours"})
    df = df.sort_values("Hours", ascending=True)
    if df.iloc[-1].Hours > 172_800:
        df.Hours = df.Hours / (24 * 60 * 60)
        scale = "days"
    elif df.iloc[-1].Hours > 7200:
        df.Hours = df.Hours / (60 * 60)
        scale = "hours"
    elif df.iloc[-1].Hours > 120:
        df.Hours = df.Hours / 60
        scale = "minutes"
    else:
        scale = "seconds"

    fig = px.bar(
        df,
        x="Hours",
        y="Album",
        orientation="h",
        title="Top Albums",
        hover_data=["Hours"],
        text="Album",
    )
    fig.update_layout(
        xaxis_title=f"Total Playtime ({scale})",
        uniformtext_minsize=13,
        uniformtext_mode="show",
    )
    set_theme(fig)
    fig.update_traces(textposition="inside", insidetextanchor="start")
    fig.update_yaxes(showticklabels=False)

    return fig
