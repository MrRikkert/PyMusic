import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pony import orm

from shared import settings

db = orm.Database()


def database_exists() -> bool:
    params = settings.DB_PARAMS
    try:
        connection = psycopg2.connect(
            f"""
            user='{params['user']}'
            port='{params['port']}'
            host='{params['host']}'
            password='{params['password']}'
            """
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{params['database']}'"
            )
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {params['database']}")
    finally:
        if connection:
            connection.close()


def create_database():
    pass


def init_db():
    if not database_exists():
        create_database()
    db.bind(**settings.DB_PARAMS)
    db.generate_mapping(create_tables=True)
