import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.db.base import db
from app.db.models import UserDb
from app.exceptions import IntegrityError
from app.logic import user as user_logic
from app.models.users import RegisterIn
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_register_user():
    user = RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    db_user = user_logic.register_user(user)
    db.flush()
    assert orm.count(u for u in UserDb) == 1
    assert db_user.username == user.username
    assert db_user.password != user.password
    assert db_user.email == user.email
    assert db_user.id is not None


@db_session
def test_register_user_username_exists():
    user1 = mixer.blend(UserDb)
    user2 = RegisterIn(
        username=user1.username, email="email@email.com", password="Abc@123!"
    )
    with pytest.raises(IntegrityError, match="Username"):
        user_logic.register_user(user2)


@db_session
def test_username_exists_non_existing():
    exists = user_logic.username_exists("test")
    assert not exists


@db_session
def test_username_exists_existing():
    user = mixer.blend(UserDb)
    exists = user_logic.username_exists(user.username)
    assert exists


@db_session
def test_get_user_by_name_non_existing():
    user = user_logic.get_user_by_name("test")
    assert user is None


@db_session
def test_get_user_by_name_existing():
    user_db = mixer.blend(UserDb)
    user = user_logic.get_user_by_name(user_db.username)
    assert user is not None


@db_session
def test_authenticate_user_correct():
    user = user_logic.register_user(
        RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    )
    user_auth = user_logic.authenticate_user("username", "Abc@123!")
    assert user_auth is not None
    assert user.username == user_auth.username
    assert user.email == user_auth.email


@db_session
def test_authenticate_user_wrong_password():
    user_logic.register_user(
        RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    )
    user_auth = user_logic.authenticate_user("username", "Abc@123")
    assert user_auth is None


@db_session
def test_authenticate_user_wrong_username():
    user_logic.register_user(
        RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    )
    user_auth = user_logic.authenticate_user("usernames", "Abc@123!")
    assert user_auth is None
