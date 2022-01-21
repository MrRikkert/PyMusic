import dash_bootstrap_components as dbc
from app.components import navbar
from dash import html


def get_layout():
    return html.Div(
        [
            navbar.get_layout(),
            dbc.Container(
                [
                    dbc.Card(
                        dbc.CardBody("This is some text within a card body"),
                        className="xs-3 mx-auto",
                    ),
                    dbc.Row(dbc.Col("HALLO", xs=12)),
                ],
                fluid=False,
                id="main-content",
            ),
        ]
    )
