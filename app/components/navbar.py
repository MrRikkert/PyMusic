import json

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, html
from dateutil.relativedelta import relativedelta
from pony.orm import db_session

from app.app import app
from shared.db.base import db


def get_layout():
    collapse = [
        dbc.Nav(id="navbar-options"),
        html.Div([], className="ml-auto flex-nowrap mt-3 mt-md-0"),
        dbc.Checklist(
            options=[{"label": "Use playtime?", "value": 1}],
            value=[1],
            id="use-playtime",
            inline=True,
        ),
        dbc.Select(
            "date-range-select",
            options=[
                {"label": "Week", "value": "week"},
                {"label": "Month", "value": "month"},
                {"label": "Year", "value": "year"},
            ],
            value="week",
            style={"width": "7rem"},
        ),
        dbc.Select(
            "date-select",
            options=[{"label": f"option_{idx}", "value": idx} for idx in range(100)],
            style={"width": "15rem"},
        ),
    ]

    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(src="/assets/img/logo.png", height="30px")
                            ),
                            dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://plotly.com",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    collapse, id="navbar-collapse", is_open=False, navbar=True
                ),
            ]
        ),
        color="dark",
        dark=True,
        id="navbar",
    )


@app.callback(
    Output("date-select", "options"),
    Output("date-select", "value"),
    Input("date-range-select", "value"),
)
@db_session
def fill_options(value):
    sql = """
    SELECT
        MAX(sc.date) max_date,
        MIN(sc.date) min_date
    FROM scrobble sc
    """
    df = pd.read_sql_query(sql, db.get_connection())
    min_date = pd.to_datetime(df.min_date[0])
    max_date = pd.to_datetime(df.max_date[0])

    if value == "week":
        freq = "W-MON"
        frmt = r"Week %W, %Y"
        timedelta = relativedelta(days=7)
    elif value == "month":
        freq = "MS"
        frmt = r"%b %Y"
        timedelta = relativedelta(months=1)
        min_date = min_date + pd.offsets.MonthBegin(-1)
    elif value == "year":
        freq = "YS"
        frmt = "%Y"
        timedelta = relativedelta(years=1)
        min_date = min_date + pd.offsets.YearBegin(-1)

    dates = pd.date_range(start=min_date, end=max_date, freq=freq, normalize=True)
    dates = dates.sort_values(ascending=False)[1:]
    options = [
        {
            "label": date.strftime(frmt),
            "value": json.dumps(
                {
                    "min_date": date.strftime(r"%Y-%m-%d"),
                    "max_date": (date + timedelta).strftime(r"%Y-%m-%d"),
                }
            ),
        }
        for date in dates
    ]
    return options, options[0]["value"]


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
