import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import (
    add_date_clause,
    convert_dates,
    get_agg,
    get_default_graph,
    min_date_to_last_range,
    set_length_scale,
    set_theme,
)
from app.db.base import db
from dash.dependencies import Input, Output
from dateutil.relativedelta import relativedelta
from pony.orm import db_session


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


def _build_query(date_range, min_date, max_date, playtime, filter_date=True):
    if date_range == "week":
        select = """
            EXTRACT(year from DATE) AS "Year",
            EXTRACT(month from DATE) AS "Month",
            EXTRACT(day from DATE) AS "Day",
            EXTRACT(week from DATE)::varchar(255) AS "Week",
        """
        group_columns = ['"Year"', '"Month"', '"Day"', '"Week"']
    elif date_range == "month":
        select = """
            EXTRACT(year from DATE) AS "Year",
            EXTRACT(month from DATE) AS "Month",
            EXTRACT(day from DATE) AS "Day",
        """
        group_columns = ['"Year"', '"Month"', '"Day"']
    elif date_range == "year":
        select = """
            EXTRACT(year from DATE)::varchar(255) AS "Year",
            EXTRACT(month from DATE) AS "Month",
        """
        group_columns = ['"Year"', '"Month"']

    sql = f"""
    SELECT
        {select}
        MIN(DATE::DATE) AS "Date",
        {get_agg(playtime)}(s.length) as "Time"
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
    return sql


@app.callback(
    Output("plays-line-chart", "figure"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("use-playtime", "checked"),
)
@set_theme
@convert_dates
@db_session
def _plays_bar_chart(date_range, min_date, playtime, max_date):
    sql = _build_query(date_range, min_date, max_date, playtime)
    sql_total = _build_query(
        date_range, min_date, max_date, playtime, filter_date=False
    )

    if date_range == "week" or date_range == "year":
        min_date = min_date_to_last_range(min_date, date_range)

    df = pd.read_sql_query(
        sql,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date},
        parse_dates=["Date"],
    )
    df = df.sort_values("Date")

    df_total = pd.read_sql_query(
        sql_total,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date},
        parse_dates=["Date"],
    )
    df_total = df_total.sort_values("Date")

    if date_range == "week":
        frmt = "%a"
        color = "Week"
        x_axis_title = "Day"
        df_total = df_total.groupby(df_total["Date"].dt.weekday, as_index=False).agg(
            {"Time": "mean", "Date": "first"}
        )
    elif date_range == "month":
        frmt = "%d"
        color = None
        x_axis_title = "Day"
        df_total = df_total.groupby("Day", as_index=False).agg(
            {"Time": "mean", "Date": "first"}
        )
    elif date_range == "year":
        frmt = "%b"
        color = "Year"
        x_axis_title = "Month"
        df_total = df_total.groupby("Month", as_index=False).agg(
            {"Time": "mean", "Date": "first"}
        )

    df["X"] = df["Date"].dt.strftime(frmt)
    df_total["X"] = df_total["Date"].dt.strftime(frmt)

    df, scale = set_length_scale(df, "Time", playtime)
    df_total, scale = set_length_scale(df_total, "Time", playtime)

    if playtime:
        title = f"Playtime over time ({scale})"
        y_axis_title = f"Total Playtime ({scale})"
    else:
        title = "Plays over time"
        y_axis_title = "Plays"

    fig = px.bar(
        df, x="X", y="Time", title=title, text="Time", color=color, barmode="group"
    )
    fig.update_layout(
        yaxis_title=y_axis_title,
        xaxis_title=x_axis_title,
        uniformtext_minsize=11,
        uniformtext_mode="show",
        legend_orientation="h",
        legend_yanchor="bottom",
        legend_xanchor="right",
        legend_y=1.15,
        legend_x=1,
    )
    fig.update_traces(texttemplate="%{value:.0f}")

    fig_2 = px.line(df_total, x="X", y="Time")
    fig_2.update_traces(
        name="Mean",
        text=None,
        line_color="white",
        showlegend=True,
        mode="markers+lines",
    )

    fig.add_trace(fig_2.data[0])

    return fig
