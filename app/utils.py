import json
from datetime import datetime, timedelta
from math import floor

import pandas as pd
import plotly.express as px
from dash import dcc
from dateutil.relativedelta import relativedelta

from shared.db.base import db
from shared.settings import IMG_URL


def get_min_max_date(dates):
    dates = json.loads(dates)
    min_date = datetime.strptime(dates["min_date"], "%Y-%m-%d").date()
    max_date = datetime.strptime(dates["max_date"], "%Y-%m-%d").date()
    return min_date, max_date, dates["date_range"]


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


def get_df_from_sql(sql, min_date, max_date, where=True, parse_dates=[]):
    sql = add_date_clause(sql, min_date, max_date, where=where)
    return pd.read_sql_query(
        sql,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date},
        parse_dates=parse_dates,
    )


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
    except Exception:
        return None


def get_default_graph(id: str, className=""):
    fig = px.bar()
    return dcc.Graph(figure=fig, id=id, className=className, style={"height": "100%"})


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


def get_art_url(hash_, size=512):
    if size not in [512, 256, 128, 64]:
        raise ValueError("unsupported image size")
    idx = hash_.rfind(".")
    return IMG_URL + hash_[:idx] + f"x{size}" + hash_[idx:]
