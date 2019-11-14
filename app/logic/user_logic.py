from app.models.users import RegisterIn
from app.utils.security import hash_password
from app.db.dao import user_dao
from app.db.models import User


def register_user(register: RegisterIn) -> User:
    register.password = hash_password(register.password)
    return user_dao.register_user(register)
