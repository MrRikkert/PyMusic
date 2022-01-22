import dash_bootstrap_components as dbc
from app.components import navbar, titlebar, stats
from dash import html


def get_layout():
    return html.Div(
        [
            navbar.get_layout(),
            dbc.Container(
                [
                    dbc.Row(dbc.Col(titlebar.get_layout())),
                    dbc.Row(
                        [
                            dbc.Col(stats.get_layout("total_scrobbles"), xs=12, lg=3),
                            dbc.Col(stats.get_layout("daily_scrobbles"), xs=12, lg=3),
                            dbc.Col(stats.get_layout("total_playtime"), xs=12, lg=3),
                            dbc.Col(stats.get_layout("daily_playtime"), xs=12, lg=3),
                        ]
                    ),
                ],
                fluid=False,
                id="main-content",
            ),
        ]
    )
