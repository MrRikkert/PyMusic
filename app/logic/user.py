from app.db.models import UserDb
from app.exceptions import IntegrityError
from app.models.users import RegisterIn
from app.utils.security import hash_password, verify_password


def register(register: RegisterIn) -> UserDb:
    """Hashes the password and adds the user to the database"""
    register = register.copy(deep=True)
    register.password = hash_password(register.password)
    if exists(register.username):
        raise IntegrityError("Username already exists")
    return UserDb(**register.dict())


def exists(username: str) -> bool:
    user = get(username)
    if user is None:
        return False
    return True


def get(username: str) -> UserDb:
    """Returns User if user exists, else returns None"""
    return UserDb.get(username=username)


def authenticate(username: str, password: str) -> UserDb:
    """Returns User if authenticated, else returns None"""
    user = get(username)
    if user is not None:
        if not verify_password(password, user.password):
            return None
    return user
