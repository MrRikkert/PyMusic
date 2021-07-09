import math
from datetime import timedelta

import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates, min_date_to_last_range
from app.db.base import db
from dash.dependencies import Input, Output
from dateutil.relativedelta import relativedelta
from pony.orm import db_session


def get_layout(_type):
    def get_card(title, id):
        return (
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1(title, className="card-title"),
                        html.Span("Loading...", id=id, className="main-stat"),
                        html.Span(
                            "Loading...", id=f"{id}-old", className="main-stat-old"
                        ),
                    ],
                    className="d-flex align-items-center justify-content-center",
                ),
                color="light",
                outline=True,
                className="general-stats halve",
            ),
        )

    if _type == "total_scrobbles":
        return get_card("Scrobbles", "stats-total-scrobbles")
    elif _type == "daily_scrobbles":
        return get_card("Scrobbles per day", "stats-scrobbles-per-day")
    elif _type == "total_playtime":
        return get_card("Total playtime", "stats-total-playtime")
    elif _type == "daily_playtime":
        return get_card("Playtime per day", "stats-daily-playtime")


@app.callback(
    Output("stats-total-scrobbles", "children"),
    Output("stats-total-scrobbles-old", "children"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
)
@convert_dates
@db_session
def __get_total_scrobbles(date_range, min_date, max_date):
    min_date = min_date_to_last_range(min_date, date_range)

    sql = f"""
    SELECT COUNT(*) as plays
    FROM scrobble sc
    :date:
    GROUP BY EXTRACT({date_range} FROM sc.date)
    ORDER BY EXTRACT({date_range} FROM sc.date) DESC
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    if len(df) > 1:
        return df.iloc[0].plays, f"vs. {df.iloc[1].plays} (last {date_range})"
    return df.iloc[0].plays, None


@app.callback(
    Output("stats-scrobbles-per-day", "children"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
)
@convert_dates
@db_session
def __get_average_scrobbles(date_range, min_date, max_date):
    min_date = min_date_to_last_range(min_date, date_range)

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
    Input("date-range-select", "value"),
    Input("date-select", "value"),
)
@convert_dates
@db_session
def __get_playtime(date_range, min_date, max_date):
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


@app.callback(
    Output("stats-daily-playtime", "children"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
)
@convert_dates
@db_session
def __get_average_playtime(date_range, min_date, max_date):
    sql = """
    SELECT SUM(s.length) AS playtime
    FROM scrobble sc
    INNER JOIN song s
	    ON sc.song = s.id
    :date:
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    total_seconds = df.iloc[0].playtime
    total_seconds = total_seconds / (max_date - min_date).days

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
