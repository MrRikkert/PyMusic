import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="altair")
# filter out pandas SQLAlchemy UserWarning
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r".*pandas.*SQLAlchemy.*",
)

# Import settings before anything else
import shared.settings  # noqa isort:skip
from app.app import app, server  # noqa
from app.pages.listening_report import get_layout  # noqa: E402
from shared.db.base import init_db  # noqa: E402


def init():
    app.layout = get_layout()
    init_db()


def run_server():
    init()
    return server


if __name__ == "__main__":
    init()
    app.run_server(debug=True)
