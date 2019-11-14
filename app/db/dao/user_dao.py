from app.models.users import RegisterIn
from app.db.models import User


def register_user(user: RegisterIn) -> User:
    return User(**user.dict())
