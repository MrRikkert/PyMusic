from pony import orm

from shared.db.models import FileDb


def get(path: str) -> FileDb:
    query = orm.select(f for f in FileDb if f.path == path)
    return query.first()


def exists(path: str) -> bool:
    file = get(path)
    return True if file is not None else False
