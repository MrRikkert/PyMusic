from pony import orm
from pony.orm import db_session

from app.db.models import UserDb
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_test():
    UserDb(username="test", email="test", password="test")
    assert orm.count(u for u in UserDb) == 1


@db_session
def test_test2():
    UserDb(username="test", email="test", password="test")
    assert UserDb[1] is not None
