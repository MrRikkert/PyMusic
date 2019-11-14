from app.models.users import Register
from app.utils.security import hash_password
from app.db.dao import user_dao


def register_user(register: Register):
    register.password = hash_password(register.password)
    user_dao.register_user(register)
    return register
