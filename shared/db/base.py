from pony import orm

from shared import settings

db = orm.Database()


def init_db():
    db.bind(**settings.DB_PARAMS)
    db.generate_mapping(create_tables=True)
