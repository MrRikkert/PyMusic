import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import app.dash.components
import app.settings  # Import settings before anything else
from app.dash.app import app
from app.dash.components import navbar, stats, top_image, top_chart
from app.db.base import init_db

app.layout = html.Div(
    [
        navbar.get_layout(),
        # navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(stats.get_layout(), md=12, lg=3),
                        dbc.Col(top_image.get_layout("series"), md=12, lg=3),
                        dbc.Col(top_image.get_layout("album"), md=12, lg=3),
                        dbc.Col(top_image.get_layout("artist"), md=12, lg=3),
                    ]
                ),
                dbc.Row([dbc.Col(top_chart.get_layout("mixed"), md=12, lg=9)]),
                dbc.Row([dbc.Col(top_chart.get_layout("artist"), md=12, lg=9)]),
            ],
            fluid=False,
        ),
    ]
)

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)
