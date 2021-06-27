import dash_bootstrap_components as dbc
import dash_html_components as html
from app.dash.app import app
from dash.dependencies import Input, Output, State

LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

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
            ],
            id="navbar-collapse",
            navbar=True,
            is_open=False,
        ),
    ],
    color="dark",
    dark=True,
)


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
