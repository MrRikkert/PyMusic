import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import app.dash.graphs
import app.dash.components
import app.settings  # Import settings before anything else
from app.dash.app import app
from app.dash.components.navbar import navbar
from app.dash.graphs import get_default_graph
from app.db.base import init_db

app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Div(id="general-stats"), width=3),
                        dbc.Col(html.Div(id="top-series"), width=3),
                        dbc.Col(html.Div(id="top-album"), width=3),
                        dbc.Col(html.Div(id="top-artist"), width=3),
                    ]
                )
            ],
            fluid=False,
        ),
    ]
)

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)

