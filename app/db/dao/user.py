from app.db.base import db
from app.db.models import UserDb
from app.models.users import RegisterIn


def register_user(user: RegisterIn) -> UserDb:
    """Adds user to the database"""
    user_db = UserDb(**user.dict())
    db.flush()
    return user_db


def get_user_by_name(username: str) -> UserDb:
    """Returns UserDb if user exists, else returns None"""
    return UserDb.get(username=username)
