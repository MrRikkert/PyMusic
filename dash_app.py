import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import app.dash.graphs
import app.settings  # Import settings before anything else
from app.dash.app import app
from app.dash.components.navbar import navbar
from app.db.base import init_db

app.layout = html.Div([navbar, dbc.Container([dcc.Graph(id="top-albums")], fluid=True)])

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)

