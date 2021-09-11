from datetime import datetime, timedelta
from inspect import getfullargspec
from math import floor

import dash_core_components as dcc
import plotly.express as px
from dateutil.relativedelta import relativedelta


def convert_dates(func):
    argspec = getfullargspec(func)

    def wrap(*args, **kwargs):
        date_range_idx = argspec.args.index("date_range")
        min_date_idx = argspec.args.index("min_date")

        args = list(args)

        min_date = datetime.strptime(args[min_date_idx], "%Y-%m-%d")
        date_range = args[date_range_idx]

        if date_range == "week":
            max_date = min_date + timedelta(days=7)
        elif date_range == "month":
            max_date = min_date + relativedelta(months=1)
        elif date_range == "year":
            max_date = min_date + relativedelta(years=1)

        args[min_date_idx] = min_date
        return func(*args, **kwargs, max_date=max_date)

    return wrap


def add_date_clause(
    sql: str, min_date: datetime, max_date: datetime, where=True
) -> str:
    if min_date and max_date:
        condition = "sc.date >= %(min_date)s AND sc.date < %(max_date)s"
        if where:
            condition = "WHERE " + condition
        else:
            condition = "AND " + condition
        return sql.replace(":date:", condition)
    return sql.replace(":date:", "")


def set_length_scale(df, column, playtime):
    if playtime:
        if df.iloc[-1][column] > 172_800:
            df[column] = df[column] / (24 * 60 * 60)
            scale = "days"
        elif df.iloc[-1][column] > 7200:
            df[column] = df[column] / (60 * 60)
            scale = "hours"
        elif df.iloc[-1][column] > 120:
            df[column] = df[column] / 60
            scale = "minutes"
        else:
            scale = "seconds"
    else:
        scale = "Plays"
    return (df, scale)


def get_default_graph(id: str, className=""):
    fig = px.bar()
    fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=40),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        template="plotly_dark",
    )
    return dcc.Graph(figure=fig, id=id, className=className, style={"height": "100%"})


def get_agg(playtime):
    if playtime:
        return "SUM"
    return "COUNT"


def min_date_to_last_range(min_date, date_range):
    if date_range == "week":
        min_date = min_date - timedelta(days=7)
    elif date_range == "month":
        min_date = min_date - relativedelta(months=1)
    elif date_range == "year":
        min_date = min_date - relativedelta(years=1)
    return min_date


def seconds_to_text(total_seconds):
    weeks = total_seconds / 604_800
    days = total_seconds % 604_800 / 86400
    hours = total_seconds % 604_800 % 86400 / 3600
    minutes = total_seconds % 604_800 % 86400 % 3600 / 60

    try:
        if total_seconds < 60 * 60:
            return f"{floor(minutes)} minutes"
        elif total_seconds < 60 * 60 * 24:
            return f"{floor(hours)} hours, {round(minutes)} minutes"
        elif total_seconds < 60 * 60 * 24 * 7:
            return f"{floor(days)} days, {round(hours)} hours"
        else:
            return f"{floor(weeks)} weeks, {round(days)} days"
    except:
        return None