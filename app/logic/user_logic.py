from app.models.users import RegisterIn
from app.utils.security import hash_password
from app.db.dao import user_dao
from app.db.models import UserDb
from app.utils.security import verify_password


def register_user(register: RegisterIn) -> UserDb:
    """Hashes the password and adds the user to the database"""
    register.password = hash_password(register.password)
    return user_dao.register_user(register)


def get_user_by_name(username: str) -> UserDb:
    """Returns UserDb if user exists, else returns None"""
    return user_dao.get_user_by_name(username)


def authenticate_user(username: str, password: str) -> UserDb:
    """Returns UserDb if authenticated, else returns None"""
    user = get_user_by_name(username)
    if user is not None:
        if not verify_password(password, user.password):
            return None
    return user
