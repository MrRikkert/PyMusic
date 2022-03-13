import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

# Import settings before anything else
import shared.settings  # noqa isort:skip
from app.app import app, server  # noqa
from app.pages.listening_report import get_layout  # noqa: E402
from shared.db.base import init_db  # noqa: E402

app.layout = get_layout()

if __name__ == "__main__":
    init_db()
    app.run_server(debug=True)
