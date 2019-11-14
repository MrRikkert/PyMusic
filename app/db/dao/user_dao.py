from app.models.users import Register
from app.db.models import User


def register_user(user: Register):
    User(**user.dict())
