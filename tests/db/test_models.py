from pony.orm import db_session
from app.db.base import db
from app.db.models import UserDb
from pony import orm


def setup_function():
    db.bind(provider="sqlite", filename=":memory:")
    db.generate_mapping(create_tables=True)


@db_session
def test_test():
    UserDb(username="test", email="test", password="test")
    assert orm.count(u for u in UserDb) == 1
