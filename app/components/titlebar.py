import dash_bootstrap_components as dbc
from dash import Input, Output, html

from app.app import app
from app.utils import get_min_max_date


def get_layout():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H1(
                    "Listening report - ...",
                    id="titlebar-title",
                    style={"font-size": "2rem", "margin-bottom": "0px"},
                ),
                html.H2(
                    "...-...",
                    id="titlebar-dates",
                    style={"font-size": "1.2rem", "margin-bottom": "0px"},
                    className="text-light",
                ),
            ]
        ),
        color="light",
        outline=True,
        className="mx-auto text-center font-weight-bold",
    )


@app.callback(Output("titlebar-title", "children"), Input("date-select", "value"))
def __get_total_scrobbles(min_date):
    min_date, _, date_range = get_min_max_date(min_date)

    if date_range == "week":
        frmt = "Week %W, %Y"
    if date_range == "month":
        frmt = "%B %Y"
    if date_range == "year":
        frmt = "Year %Y"
    return f"Listening report - {min_date.strftime(frmt)}"


@app.callback(Output("titlebar-dates", "children"), Input("date-select", "value"))
def __get_dates(min_date):
    min_date, max_date, date_range = get_min_max_date(min_date)
    if date_range == "week":
        frmt = "%d %b, %Y"
        return f"{min_date.strftime(frmt)} - {max_date.strftime(frmt)}"
    return ""
