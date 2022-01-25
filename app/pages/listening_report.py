import dash_bootstrap_components as dbc
from dash import html

from app import stores
from app.components import navbar, stats, titlebar, top_image_chart
from app.components.charts import listening_clock, play_over_time, tag_timeline, vocals


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
                    dbc.Row(
                        [
                            dbc.Col(top_image_chart.get_layout("mixed"), xs=12, lg=4),
                            dbc.Col(top_image_chart.get_layout("artist"), xs=12, lg=4),
                            dbc.Col(top_image_chart.get_layout("album"), xs=12, lg=4),
                        ]
                    ),
                    dbc.Row(dbc.Col(play_over_time.get_layout())),
                    dbc.Row([dbc.Col(vocals.get_layout(), xs=12)]),
                    dbc.Row(
                        [
                            dbc.Col(listening_clock.get_layout(), xs=12, lg=4),
                            dbc.Col(tag_timeline.get_layout(), xs=12, lg=8),
                        ]
                    ),
                ],
                fluid=False,
                id="main-content",
            ),
            stores.get_layout(),
        ]
    )
