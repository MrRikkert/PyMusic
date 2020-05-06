import os

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
        DB_PARAMS = {
            "provider": "postgres",
            "user": os.getenv("DB_POSTGRES_USER"),
            "password": os.getenv("DB_POSTGRES_PASSWORD"),
            "host": os.getenv("DB_POSTGRES_HOST"),
            "database": os.getenv("DB_POSTGRES_DATABASE"),
        }
