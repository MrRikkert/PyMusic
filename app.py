import shared.settings  # Import settings before anything else
from app.app import app
from shared.db.base import init_db
from app import pages

app.layout = pages.get_layout()

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)
