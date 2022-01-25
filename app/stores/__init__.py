from dash import dcc, html

from app.stores import top_stores  # noqa


def get_layout():
    return html.Div(
        [
            dcc.Store("top-tags"),
            dcc.Store("top-tags-scale"),
            dcc.Store("top-artists"),
            dcc.Store("top-artists-scale"),
            dcc.Store("top-albums"),
            dcc.Store("top-albums-scale"),
        ]
    )
