from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import dash_html_components as html
from app.dash.app import app
from dash.dependencies import Input, Output, State


def get_layout():
    LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    max_date = datetime.now().strftime("%Y-%m-%d")
    min_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    min_date = dbc.Row(
        [
            dbc.Col("Min date:", className="navbar-text"),
            dbc.Col(dbc.Input(type="date", id="min-date", value=min_date)),
        ],
        no_gutters=True,
        className="ml-auto flex-nowrap mt-3 mt-md-0 date-input",
        align="center",
    )

    max_date = dbc.Row(
        [
            dbc.Col("Max date:", className="navbar-text"),
            dbc.Col(dbc.Input(type="date", id="max-date", value=max_date)),
        ],
        no_gutters=True,
        className="flex-nowrap mt-3 mt-md-0 date-input",
        align="center",
    )

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
            dbc.Collapse(
                [
                    dbc.Nav(dbc.NavItem(dbc.NavLink("Page 1", href="#")), navbar=True),
                    dbc.Nav(dbc.NavItem(dbc.NavLink("Page 2", href="#")), navbar=True),
                    min_date,
                    max_date,
                ],
                id="navbar-collapse",
                navbar=True,
                is_open=False,
            ),
        ],
        color="dark",
        dark=True,
        fixed="top",
    )
    return navbar


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
