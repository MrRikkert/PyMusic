import os

import dotenv
from loguru import logger

dotenv.load_dotenv()


config = {
    "handlers": [
        {
            "sink": "logs/{time:YYYY-MM-DD}.log",
            "rotation": "1 day",
            "retention": "7 days",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {file}:{function}:{line} | {message}",
            "backtrace": True,
            "diagnose": True,
        }
    ]
}
logger.configure(**config)


# DB
DB_PARAMS = {"provider": "sqlite", "filename": "sqlite.db", "create_db": True}

# JWT
SECRET_KEY = ""
ALGORITHM = "HS256"

# password hashing
HASH_ALGORITHMS = ["bcrypt"]

# LastFM
LASTFMKEY = ""
LASTFMSECRET = ""

# --------------------------------------------------------------------------------------

# Override the default value from the envirioment variable if it exists
# This is done this way since docker creates empty variables by default.
if os.getenv("JWT_SECRET_KEY"):
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if os.getenv("JWT_ALGORITHM"):
    ALGORITHM = os.getenv("JWT_ALGORITHM")
if os.getenv("PASS_ALGORITHM"):
    HASH_ALGORITHMS = os.getenv("PASS_ALGORITHM")
if os.getenv("LASTFM_KEY"):
    LASTFMKEY = os.getenv("LASTFM_KEY")
if os.getenv("LASTFM_SECRET"):
    LASTFMSECRET = os.getenv("LASTFM_SECRET")
if os.getenv("DB_PROVIDER"):
    provider = os.getenv("DB_PROVIDER")
    if provider == "sqlite":
        DB_PARAMS = {
            "provider": "sqlite",
            "filename": os.getenv("DB_SQLITE_FILENAME"),
            "create_db": os.getenv("DB_SQLITE_CREATE_DB"),
        }
    elif provider == "postgres":
        if os.getenv("DATABASE_URL"):
            DB_PARAMS = {"provider": "postgres", "dsn": os.getenv("DATABASE_URL")}
        else:
            DB_PARAMS = {
                "provider": "postgres",
                "user": os.getenv("DB_POSTGRES_USER"),
                "password": os.getenv("DB_POSTGRES_PASSWORD"),
                "host": os.getenv("DB_POSTGRES_HOST"),
                "port": os.getenv("DB_POSTGRES_PORT"),
                "database": os.getenv("DB_POSTGRES_DATABASE"),
            }
if os.getenv("ALBUM_ART_PATH"):
    ALBUM_ART_PATH = os.getenv("ALBUM_ART_PATH")
