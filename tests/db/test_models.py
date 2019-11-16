import pytest
from pony import orm
from pony.orm import db_session

from app.db.models import UserDb
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_create_user():
    UserDb(username="test", email="test", password="test")
    assert orm.count(u for u in UserDb) == 1


@db_session
def test_create_user_no_username():
    with pytest.raises(ValueError):
        UserDb(email="test", password="test")


@db_session
def test_create_user_no_email():
    with pytest.raises(ValueError):
        UserDb(username="test", password="test")


@db_session
def test_create_user_password():
    with pytest.raises(ValueError):
        UserDb(username="test", email="test")


@db_session
def test_create_user_duplicate_username():
    UserDb(username="test", email="test", password="test")
    with pytest.raises(orm.core.CacheIndexError, match="key username"):
        UserDb(username="test", email="test2", password="test")


@db_session
def test_create_user_duplicate_email():
    UserDb(username="test", email="test", password="test")
    with pytest.raises(orm.core.CacheIndexError, match="key email"):
        UserDb(username="test2", email="test", password="test")
