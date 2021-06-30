import dash_bootstrap_components as dbc
import dash_html_components as html
from app.dash.app import app
from app.dash.utils import convert_dates
from dash.dependencies import Input, Output
from pony.orm import db_session


def get_layout():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H1("Scrobbles", className="card-title"),
                html.Span(id="stats-total-scrobbles"),
                html.H1("Scrobbles per day", className="card-title"),
                html.Span(id="stats-scrobbles-per-day"),
                html.H1("Total playtime", className="card-title"),
                html.Span(id="stats-total-playtime"),
            ]
        ),
        color="light",
        outline=True,
        className="general-stats",
    )


@app.callback(
    Output("stats-total-scrobbles", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def __get_total_scrobbles(min_date, max_date):
    return 806


@app.callback(
    Output("stats-scrobbles-per-day", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def __get_average_scrobbles(min_date, max_date):
    return 86


@app.callback(
    Output("stats-total-playtime", "children"),
    Input("min-date", "value"),
    Input("max-date", "value"),
)
@convert_dates
@db_session
def __get_playtime(min_date, max_date):
    return "18 hours, 5 minutes"


# @app.callback(
#     Output("general-stats", "children"),
#     Input("min-date", "value"),
#     Input("max-date", "value"),
# )
# @convert_dates
# @db_session
# def get_stats(min_date, max_date):
#     return dbc.Card(
#         dbc.CardBody(
#             [
#                 html.H1("Scrobbles", className="card-title"),
#                 html.Span("806"),
#                 html.H1("Scrobbles per day", className="card-title"),
#                 html.Span("86"),
#                 html.H1("Total playtime", className="card-title"),
#                 html.Span("18 hours, 5 minutes"),
#             ]
#         ),
#         color="light",
#         outline=True,
#     )
