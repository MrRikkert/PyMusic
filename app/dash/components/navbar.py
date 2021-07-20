import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from app.dash.app import app
from shared.db.base import db
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from pony.orm import db_session


def get_layout():
    LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    collapse = [
        dbc.Nav(dbc.NavItem(dbc.NavLink("Page 1", href="#")), navbar=True),
        dbc.Nav(dbc.NavItem(dbc.NavLink("Page 2", href="#")), navbar=True),
        dbc.Nav(id="test"),
        html.Div([], className="ml-auto flex-nowrap mt-3 mt-md-0"),
        dbc.FormGroup(
            [
                dbc.Checklist(
                    options=[{"label": "Use playtime?", "value": 1}],
                    value=[1],
                    id="use-playtime",
                    inline=True,
                )
            ],
            check=True,
        ),
        dbc.Select(
            "date-range-select",
            options=[
                {"label": "Week", "value": "week"},
                {"label": "Month", "value": "month"},
                {"label": "Year", "value": "year"},
            ],
            value="week",
        ),
        dbc.Select(
            "date-select",
            options=[{"label": f"option_{idx}", "value": idx} for idx in range(100)],
            className="right",
        ),
    ]

    navbar = dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("PyMusic", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://plotly.com",
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(collapse, id="navbar-collapse", navbar=True, is_open=False),
        ],
        color="dark",
        dark=True,
        sticky="top",
    )
    return navbar


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
    min_date = df.min_date[0]
    max_date = df.max_date[0]

    if value == "week":
        freq = "W-MON"
        frmt = r"Week %W, %Y"
        max_date = max_date + relativedelta(weeks=1)
    elif value == "month":
        freq = "MS"
        frmt = r"%b %Y"
        min_date = min_date + pd.offsets.MonthBegin(-1)
        max_date = max_date + pd.offsets.MonthBegin(1)
    elif value == "year":
        freq = "YS"
        frmt = "%Y"
        min_date = min_date + pd.offsets.YearBegin(-1)
        max_date = max_date + pd.offsets.YearBegin(1)

    dates = pd.date_range(start=min_date, end=max_date, freq=freq)
    dates = dates.sort_values(ascending=False)[1:]
    options = [
        {"label": date.strftime(frmt), "value": date.strftime(r"%Y-%m-%d")}
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
