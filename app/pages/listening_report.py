import dash_bootstrap_components as dbc
import dash_html_components as html

from app.components import (
    listening_clock_chart,
    plays_over_time_chart,
    stats,
    tag_timeline_chart,
    title_bar,
    top_chart,
    top_image,
    vocal_chart,
)


def get_layout():
    return dbc.Container(
        [
            dbc.Row(dbc.Col(title_bar.get_layout(), xs=12)),
            dbc.Row(
                [
                    dbc.Col(stats.get_layout("total_scrobbles"), xs=12, lg=3),
                    dbc.Col(stats.get_layout("daily_scrobbles"), xs=12, lg=3),
                    dbc.Col(stats.get_layout("daily_playtime"), xs=12, lg=3),
                    dbc.Col(stats.get_layout("total_playtime"), xs=12, lg=3),
                ]
            ),
            dbc.Row([dbc.Col(plays_over_time_chart.get_layout(), xs=12)]),
            dbc.Row(
                [
                    dbc.Col(
                        top_image.get_layout("series"),
                        xs={"size": 12, "order": "first"},
                        lg={"size": 3, "order": "last"},
                    ),
                    dbc.Col(
                        top_chart.get_layout("mixed", reverse=True),
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
                        top_chart.get_layout("album", reverse=True),
                        xs={"size": 12, "order": "last"},
                        lg={"size": 9, "order": "first"},
                    ),
                ]
            ),
            dbc.Row([dbc.Col(vocal_chart.get_layout(), xs=12)]),
            dbc.Row(
                [
                    dbc.Col(listening_clock_chart.get_layout(), xs=12, lg=4),
                    dbc.Col(tag_timeline_chart.get_layout(), xs=12, lg=8),
                ]
            ),
        ],
        fluid=False,
        id="main-content",
    )
