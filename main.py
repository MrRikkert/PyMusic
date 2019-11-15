import uvicorn

from app import settings
from app.db.base import db
from app.server import app

db.bind(**settings.DB_PARAMS)
db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
