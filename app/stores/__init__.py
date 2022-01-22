from dash import dcc, html
from app.stores import top_stores


def get_layout():
    return html.Div(
        [
            dcc.Store("top-tags"),
            dcc.Store("top-tags-scale"),
            dcc.Store("top-artists"),
            dcc.Store("top-artists-scale"),
        ]
    )
