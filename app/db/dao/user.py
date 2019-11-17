from app.db.base import db
from app.db.models import UserDb
from app.models.users import RegisterIn, User


def register_user(user: RegisterIn) -> User:
    """Adds user to the database"""
    user_db = UserDb(**user.dict())
    db.flush()
    return User.from_orm(user_db)


def get_user_by_name(username: str) -> User:
    """Returns UserDb if user exists, else returns None"""
    user_db = UserDb.get(username=username)
    return User.from_orm(user_db) if user_db is not None else None
