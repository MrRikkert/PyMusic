from app.db.models import UserDb
from app.exceptions import IntegrityError
from app.models.users import RegisterIn
from app.utils.security import hash_password, verify_password


def register(register: RegisterIn) -> UserDb:
    """Register a user by adding him/her to the database.
    Also hashes the password.

    ## Arguments:
    - `register`: `RegisterIn`:
        - De user you want to register

    ## Raises:
    - `IntegrityError`:
        - Raised when the username and/or email already exists

    ## Returns:
    - `UserDb`:
        - The created user
    """
    register = register.copy(deep=True)
    register.password = hash_password(register.password)
    if exists(register.username):
        raise IntegrityError("Username already exists")
    return UserDb(**register.dict())


def exists(username: str) -> bool:
    """Check if the user already exists in the database

    ## Arguments:
    - `username`: `str`:
        - Name of the user

    ## Returns:
    - `bool`:
        - `True` when user exists, `False` when it doesn't
    """
    user = get(username)
    if user is None:
        return False
    return True


def get(username: str) -> UserDb:
    """Get user from database

    ## Arguments:
    - `username`: `str`:
        - Name of the user

    ## Returns:
    - `UserDb`:
        - The found user. Returns `None` when no user is found
    """
    return UserDb.get(username=username)


def authenticate(username: str, password: str) -> UserDb:
    """Validat user credentials

    ## Arguments:
    - `username`: `str`:
        - Name of the user
    - `password`: `str`:
        - Password of the user (non hashed)

    ## Returns:
    - `UserDb`:
        - Return the user if the credentials are correct.
        Returns `None` if the credentials are wrong.
    """
    user = get(username)
    if user is not None:
        if not verify_password(password, user.password):
            return None
    return user
