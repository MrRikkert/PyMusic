import dash_bootstrap_components as dbc
from dash import html

from app import stores
from app.components import navbar, stats, titlebar, top_image
from app.components.charts import play_over_time, top_chart, vocals


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
                    dbc.Row(
                        [
                            dbc.Col(
                                top_image.get_layout("mixed"),
                                xs={"size": 12, "order": "first"},
                                lg={"size": 3, "order": "last"},
                            ),
                            dbc.Col(
                                top_chart.get_layout("mixed"),
                                xs={"size": 12, "order": "last"},
                                lg={"size": 9, "order": "first"},
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                top_image.get_layout("artist"),
                                xs={"size": 12, "order": "first"},
                                lg={"size": 3, "order": "first"},
                            ),
                            dbc.Col(
                                top_chart.get_layout("artist", reverse=False),
                                xs={"size": 12, "order": "last"},
                                lg={"size": 9, "order": "first"},
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                top_image.get_layout("album"),
                                xs={"size": 12, "order": "first"},
                                lg={"size": 3, "order": "last"},
                            ),
                            dbc.Col(
                                top_chart.get_layout("album"),
                                xs={"size": 12, "order": "last"},
                                lg={"size": 9, "order": "first"},
                            ),
                        ]
                    ),
                    dbc.Row([dbc.Col(vocals.get_layout(), xs=12)]),
                ],
                fluid=False,
                id="main-content",
            ),
            stores.get_layout(),
        ]
    )
