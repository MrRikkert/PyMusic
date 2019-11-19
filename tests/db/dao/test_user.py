from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.db.dao import user as user_dao
from app.db.models import UserDb
from app.models.users import RegisterIn
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_register_user():
    user = RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    db_user = user_dao.register_user(user)
    assert orm.count(u for u in UserDb) == 1
    assert db_user.username == user.username
    assert db_user.password == user.password
    assert db_user.email == user.email
    assert db_user.id is not None


@db_session
def test_get_user_by_name_existing():
    user = mixer.blend(UserDb)
    db_user = user_dao.get_user_by_name(user.username)
    assert db_user is not None
    assert db_user.username == user.username


@db_session
def test_get_user_by_name_non_existing():
    db_user = user_dao.get_user_by_name("hallo")
    assert db_user is None
