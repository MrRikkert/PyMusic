import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import (
    add_date_clause,
    convert_dates,
    get_default_graph,
    set_length_scale,
    set_theme,
)
from app.db.base import db
from dash.dependencies import Input, Output
from pony.orm import db_session
import dash_core_components as dcc


def get_layout():
    def get_card():
        return (
            dbc.Card(
                dbc.CardBody(get_default_graph(id="plays-line-chart")),
                color="light",
                outline=True,
            ),
        )

    return get_card()


def _build_query(min_date, max_date, filter_date=True):
    days = (max_date - min_date).days
    if days <= 14:
        _type = "days"
        select = """
            EXTRACT(year from DATE) AS "Year",
            EXTRACT(month from DATE) AS "Month",
            EXTRACT(day from DATE) AS "Day",
        """
        group_columns = ['"Year"', '"Month"', '"Day"']
    elif days <= 7 * 14:
        _type = "weeks"
        select = """
            EXTRACT(year from DATE) AS "Year",
            EXTRACT(week from DATE) AS "Week",
        """
        group_columns = ['"Year"', '"Week"']
    elif days <= 14 * 30:
        _type = "months"
        select = """
            EXTRACT(year from DATE) AS "Year",
            EXTRACT(month from DATE) AS "Month",
        """
        group_columns = ['"Year"', '"Month"']
    else:
        _type = "years"
        select = """
            EXTRACT(year from DATE) AS "Year",
        """
        group_columns = ['"Year"']

    sql = f"""
    SELECT
        {select}
        MIN(DATE::DATE) AS "Date",
        SUM(s.length) as "Time"
    FROM scrobble sc
    INNER JOIN song s
	    ON sc.song = s.id
    :date:
    GROUP BY {', '.join(group_columns)}
    ORDER BY {' DESC, '.join(group_columns)} DESC
    """

    if filter_date:
        sql = add_date_clause(sql, min_date, max_date, where=True)
    else:
        sql = sql.replace(":date:", "")
    return (sql, _type)


def _get_data(min_date, max_date, filter_date=True):
    sql, _type = _build_query(min_date, max_date, filter_date)

    df = pd.read_sql_query(
        sql,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date},
        parse_dates=["Date"],
    )
    df = df.sort_values("Date")

    if _type == "days":
        df["Date"] = df["Date"].dt.strftime("%a, %b %d")
    elif _type == "weeks":
        df["Date"] = df["Date"] - pd.to_timedelta(df["Date"].dt.dayofweek, unit="d")
        df["Date"] = df["Date"].dt.strftime("Week %W, %Y")
    elif _type == "months":
        df["Date"] = df["Date"].dt.strftime("%b %Y")
    elif _type == "years":
        df["Date"] = df["Date"].dt.strftime("%Y")

    df, scale = set_length_scale(df, "Time")
    return (df, scale)


@app.callback(
    Output("plays-line-chart", "figure"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@set_theme
@convert_dates
@db_session
def _plays_bar_chart(min_date, max_date):
    df, scale = _get_data(min_date, max_date)

    fig = px.bar(
        df, x="Date", y="Time", title=f"Playtime over time ({scale})", text="Time"
    )
    fig.update_layout(
        yaxis_title=f"Total Playtime ({scale})",
        uniformtext_minsize=11,
        uniformtext_mode="show",
    )
    fig.update_traces(texttemplate="%{value:.0f}")

    # df, scale = _get_data(min_date, max_date, filter_date=False)
    # fig_2 = px.line(df, x="Date", y="Time", text="Time")
    # fig_2.update_traces(text=None, line_color="white")

    # fig.add_trace(fig_2.data[0])

    return fig
