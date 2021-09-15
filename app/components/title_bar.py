import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app.app import app
from app.utils import convert_dates


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
