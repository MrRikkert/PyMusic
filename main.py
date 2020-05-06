import dotenv
import uvicorn

from app import settings
from app.db.base import db
from app.server import app

db.bind(**settings.DB_PARAMS)
db.generate_mapping(create_tables=True)

# Used for the docker container
app = app
dotenv.load_dotenv()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
