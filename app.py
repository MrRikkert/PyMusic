import dash_html_components as html

import shared.settings  # Import settings before anything else
from app import data_callbacks
from app.app import app
from app.components import navbar
from app.pages import listening_report
from shared.db.base import init_db

app.layout = html.Div(
    [navbar.get_layout(), listening_report.get_layout(), data_callbacks.get_layout()]
)

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)
