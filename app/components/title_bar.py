import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from app.app import app
from shared.db.base import db
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from pony.orm import db_session
from app.utils import (
    add_date_clause,
    convert_dates,
    min_date_to_last_range,
    seconds_to_text,
)


def get_layout():
    return (
        dbc.Card(
            dbc.CardBody(
                [
                    html.H1("Loading...", className="card-title", id="title-bar-title"),
                    # html.Div(
                    #     "Some quick example text to build on the card title and make "
                    #     "up the bulk of the card's content.",
                    #     className="card-text",
                    # ),
                ],
                className="d-flex align-items-center justify-content-center",
            ),
            color="light",
            outline=True,
            className="title-bar",
        ),
    )


@app.callback(
    Output("title-bar-title", "children"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@convert_dates
def __get_total_scrobbles(min_date, date_range, max_date):
    if date_range == "week":
        frmt = "Week %W, %Y"
    if date_range == "month":
        frmt = "%B %Y"
    if date_range == "year":
        frmt = "Year %Y"
    return f"Listening report - {min_date.strftime(frmt)}"
