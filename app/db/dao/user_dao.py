from app.models.users import RegisterIn
from app.db.models import UserDb


def register_user(user: RegisterIn) -> UserDb:
    return UserDb(**user.dict())


def get_user_by_name(username: str) -> UserDb:
    return UserDb.get(username=username)
