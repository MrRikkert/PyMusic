# Import settings before anything else
import shared.settings  # noqa isort:skip
from app import pages
from app.app import app, server  # noqa
from shared.db.base import init_db

app.layout = pages.get_layout()

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)
