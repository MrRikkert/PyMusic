# Import settings before anything else
import shared.settings  # noqa isort:skip
from app.app import app, server  # noqa
from app.pages.listening_report import get_layout
from shared.db.base import init_db

app.layout = get_layout()

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)
