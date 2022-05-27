import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

# Import settings before anything else
import shared.settings  # noqa isort:skip
from app.app import app, server  # noqa
from app.pages.listening_report import get_layout  # noqa: E402
from shared.db.base import init_db  # noqa: E402


def run_server(*arg, **kwarg):
    app.layout = get_layout()
    init_db()
    app.run_server(debug=True)


if __name__ == "__main__":
    run_server()
