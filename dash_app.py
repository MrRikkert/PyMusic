import dash_bootstrap_components as dbc
import dash_html_components as html

from app.dash.app import app
from app.dash.components.navbar import navbar

app.layout = html.Div([navbar, dbc.Container([], fluid=True)])

if __name__ == "__main__":
    app.run_server(debug=True)

