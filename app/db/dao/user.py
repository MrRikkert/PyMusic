from app.models.users import RegisterIn
from app.db.models import UserDb


def register_user(user: RegisterIn) -> UserDb:
    """Adds user to the database"""
    return UserDb(**user.dict())


def get_user_by_name(username: str) -> UserDb:
    """Returns UserDb if user exists, else returns None"""
    return UserDb.get(username=username)
