import dash_bootstrap_components as dbc
import dash_core_components as dcc
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


def _build_query(date_range, min_date, max_date, filter_date=True):
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
    return sql


@app.callback(
    Output("plays-line-chart", "figure"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
)
@set_theme
@convert_dates
@db_session
def _plays_bar_chart(date_range, min_date, max_date):
    sql = _build_query(date_range, min_date, max_date)

    if date_range == "week":
        min_date = min_date - relativedelta(days=7)
    elif date_range == "year":
        min_date = min_date - relativedelta(years=1)

    df = pd.read_sql_query(
        sql,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date},
        parse_dates=["Date"],
    )
    df = df.sort_values("Date")

    if date_range == "week":
        df["Date"] = df["Date"].dt.strftime("%a")
        color = "Week"
    elif date_range == "month":
        df["Date"] = df["Date"].dt.strftime("%d")
        color = None
    elif date_range == "year":
        df["Date"] = df["Date"].dt.strftime("%b")
        color = "Year"

    df, scale = set_length_scale(df, "Time")

    fig = px.bar(
        df,
        x="Date",
        y="Time",
        title=f"Playtime over time ({scale})",
        text="Time",
        color=color,
        barmode="group",
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
