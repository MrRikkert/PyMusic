import dash_bootstrap_components as dbc
from dash import Input, Output, html

from app.app import app
from app.utils import get_min_max_date


def get_layout():
    return dbc.Card(
        dbc.CardBody(
            html.H1(
                "Listening report - ...",
                id="titlebar-title",
                style={"font-size": "2rem", "margin-bottom": "0px"},
            )
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
