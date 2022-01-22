import dash_bootstrap_components as dbc
from dash import html

from app.components import navbar, stats, titlebar
from app.components.charts import play_over_time, top_chart


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
                    dbc.Row(dbc.Col(play_over_time.get_layout())),
                    dbc.Row(dbc.Col(top_chart.get_layout("mixed"), xs=12, lg=9)),
                ],
                fluid=False,
                id="main-content",
            ),
        ]
    )
