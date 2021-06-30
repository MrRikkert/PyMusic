import math
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates
from app.db.base import db
from dash.dependencies import Input, Output
from pony.orm import db_session


def get_layout():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H1("Scrobbles", className="card-title"),
                html.Span("Loading...", id="stats-total-scrobbles"),
                html.H1("Scrobbles per day", className="card-title"),
                html.Span("Loading...", id="stats-scrobbles-per-day"),
                html.H1("Total playtime", className="card-title"),
                html.Span("Loading...", id="stats-total-playtime"),
            ]
        ),
        color="light",
        outline=True,
        className="general-stats",
    )


@app.callback(
    Output("stats-total-scrobbles", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def __get_total_scrobbles(min_date, max_date):
    sql = """
    SELECT COUNT(*) as plays
    FROM scrobble sc
    :date:
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    return df.iloc[0].plays


@app.callback(
    Output("stats-scrobbles-per-day", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def __get_average_scrobbles(min_date, max_date):
    sql = """
    SELECT COUNT(*) as plays
    FROM scrobble sc
    :date:
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    count = df.iloc[0].plays
    return round(count / (max_date - min_date).days)


@app.callback(
    Output("stats-total-playtime", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def __get_playtime(min_date, max_date):
    sql = """
    SELECT SUM(s.length) AS length
    FROM scrobble sc
    INNER JOIN song s
        ON s.id = sc.song
    :date:
    """

    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    total_seconds = df.iloc[0].length

    time = ""
    weeks = math.floor(total_seconds / 604_800)
    days = math.floor(total_seconds % 604_800 / 86400)
    hours = math.floor(total_seconds % 604_800 % 86400 / 3600)
    minutes = math.floor(total_seconds % 604_800 % 86400 % 3600 / 60)

    if weeks > 0:
        time = f"{time}{weeks} weeks, "
    if days > 0:
        time = f"{time}{days} days, "
    if hours > 0:
        time = f"{time}{hours} hours, "
    if minutes > 0:
        time = f"{time}{minutes} minutes"

    return time
