import dash_bootstrap_components as dbc
from dash import Input, Output, State, html

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
        className="xs-3 mx-auto text-center font-weight-bold",
    )


@app.callback(
    Output("titlebar-title", "children"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
def __get_total_scrobbles(min_date, date_range):
    min_date, max_date = get_min_max_date(min_date, date_range)

    if date_range == "week":
        frmt = "Week %W, %Y"
    if date_range == "month":
        frmt = "%B %Y"
    if date_range == "year":
        frmt = "Year %Y"
    return f"Listening report - {min_date.strftime(frmt)}"
