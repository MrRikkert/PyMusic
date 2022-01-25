import dash_bootstrap_components as dbc
from dash import Input, Output, html
from pony.orm import db_session

from app.app import app
from app.utils import (
    get_df_from_sql,
    get_min_max_date,
    min_date_to_last_range,
    seconds_to_text,
)


def get_layout(_type):
    def get_card(title, id):
        return (
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1(
                            title,
                            className="mb-0 text-light",
                            style={"font-size": "1.2rem"},
                        ),
                        html.Span("Loading...", style={"font-size": "1.5rem"}, id=id),
                        html.Span(
                            "Loading...",
                            className="text-light",
                            style={"font-size": "1rem"},
                            id=f"{id}-old",
                        ),
                    ],
                    class_name="d-flex flex-column",
                ),
                color="light",
                outline=True,
                class_name="text-center n3",
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
)
@db_session
def __get_total_scrobbles(min_date):
    min_date, max_date, date_range = get_min_max_date(min_date)
    min_date = min_date_to_last_range(min_date, date_range)

    sql = f"""
    SELECT COUNT(*) as plays
    FROM scrobble sc
    :date:
    GROUP BY EXTRACT({date_range} FROM sc.date)
    ORDER BY EXTRACT({date_range} FROM sc.date) DESC
    """
    df = get_df_from_sql(sql, min_date, max_date)

    if len(df) > 1:
        return df.iloc[0].plays, f"vs. {df.iloc[1].plays} (last {date_range})"
    return df.iloc[0].plays, None


@app.callback(
    Output("stats-scrobbles-per-day", "children"),
    Output("stats-scrobbles-per-day-old", "children"),
    Input("date-select", "value"),
)
@db_session
def __get_average_scrobbles(min_date):
    min_date, max_date, date_range = get_min_max_date(min_date)
    min_date = min_date_to_last_range(min_date, date_range)

    days = (max_date - min_date).days

    sql = f"""
    SELECT ROUND(COUNT(*) / {days}) as plays
    FROM scrobble sc
    :date:
    GROUP BY EXTRACT({date_range} FROM sc.date)
    ORDER BY EXTRACT({date_range} FROM sc.date) DESC
    """
    df = get_df_from_sql(sql, min_date, max_date)

    if len(df) > 1:
        return (df.iloc[0].plays, f"vs. {df.iloc[1].plays:.0f} (last {date_range})")
    return round(df.iloc[0].plays), None


@app.callback(
    Output("stats-total-playtime", "children"),
    Output("stats-total-playtime-old", "children"),
    Input("date-select", "value"),
)
@db_session
def __get_playtime(min_date):
    min_date, max_date, date_range = get_min_max_date(min_date)
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
    df = get_df_from_sql(sql, min_date, max_date)

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
)
@db_session
def __get_average_playtime(min_date):
    min_date, max_date, date_range = get_min_max_date(min_date)
    min_date = min_date_to_last_range(min_date, date_range)

    days = (max_date - min_date).days

    sql = f"""
    SELECT SUM(s.length) / {days} AS playtime
    FROM scrobble sc
    INNER JOIN song s
        ON sc.song = s.id
    :date:
    GROUP BY EXTRACT({date_range} FROM sc.date)
    ORDER BY EXTRACT({date_range} FROM sc.date) DESC
    """
    df = get_df_from_sql(sql, min_date, max_date)

    if len(df) > 1:
        return (
            seconds_to_text(df.iloc[0].playtime),
            f"vs. {seconds_to_text(df.iloc[1].playtime)} (last {date_range})",
        )
    return seconds_to_text(df.iloc[0].playtime), None
