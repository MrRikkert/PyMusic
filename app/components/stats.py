import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from pony.orm import db_session

from app.app import app
from app.utils import (
    add_date_clause,
    convert_dates,
    min_date_to_last_range,
    seconds_to_text,
)
from shared.db.base import db


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
                className="general-stats",
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
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@convert_dates
@db_session
def __get_total_scrobbles(min_date, date_range, max_date):
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
    Output("stats-scrobbles-per-day-old", "children"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@convert_dates
@db_session
def __get_average_scrobbles(min_date, date_range, max_date):
    days = (max_date - min_date).days
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
        return (
            round(df.iloc[0].plays / days),
            f"vs. {round(df.iloc[1].plays / days)} (last {date_range})",
        )
    return round(df.iloc[0].plays / days), None


@app.callback(
    Output("stats-total-playtime", "children"),
    Output("stats-total-playtime-old", "children"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@convert_dates
@db_session
def __get_playtime(min_date, date_range, max_date):
    min_date = min_date_to_last_range(min_date, date_range)

    sql = f"""
    SELECT SUM(s.length) AS length
    FROM scrobble sc
    INNER JOIN song s
        ON s.id = sc.song
    :date:
    GROUP BY EXTRACT({date_range} FROM sc.date)
    ORDER BY EXTRACT({date_range} FROM sc.date) DESC
    """

    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    if len(df) > 1:
        return (
            seconds_to_text(df.iloc[0].length),
            f"vs. {seconds_to_text(df.iloc[1].length)} (last {date_range})",
        )
    return seconds_to_text(df.iloc[0].length), None


@app.callback(
    Output("stats-daily-playtime", "children"),
    Output("stats-daily-playtime-old", "children"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@convert_dates
@db_session
def __get_average_playtime(min_date, date_range, max_date):
    days = (max_date - min_date).days
    min_date = min_date_to_last_range(min_date, date_range)

    sql = f"""
    SELECT SUM(s.length) AS playtime
    FROM scrobble sc
    INNER JOIN song s
        ON sc.song = s.id
    :date:
    GROUP BY EXTRACT({date_range} FROM sc.date)
    ORDER BY EXTRACT({date_range} FROM sc.date) DESC
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )

    if len(df) > 1:
        return (
            seconds_to_text(df.iloc[0].playtime / days),
            f"vs. {seconds_to_text(df.iloc[1].playtime / days)} (last {date_range})",
        )
    return seconds_to_text(df.iloc[0].playtime / days), None
