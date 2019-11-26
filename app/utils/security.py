import jwt
from passlib.context import CryptContext

from app.models.users import UserTokenData
from app.settings import ALGORITHM, HASH_ALGORITHMS, SECRET_KEY

pwd_context = CryptContext(schemes=HASH_ALGORITHMS, deprecated="auto")


def hash_password(password: str) -> str:
    """Returns a hashed password

    ## Arguments:
    - `password`: `str`:
        - The password to hash

    ## Returns:
    - `str`:
        - Hashed password
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies if a correct password is entered

    ## Arguments:
    - `password`: `str`:
        - Password to verify
    - `hashed_password`: `str`:
        - Actual hashed password

    ## Returns:
    - `bool`:
        - `True` when valid, `False` when invalid
    """
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: UserTokenData) -> str:
    """Creates JWT token based on `UserTokenData`

    ## Arguments:
    - `data`: `UserTokenData`:
        - Data needed for the JWT

    ## Returns:
    - `str`:
        - JWT token
    """
    """Creates jwt token based on UserTokenData"""
    data = data.dict()
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """Decode JWT tokens

    ## Arguments:
    - `token`: `str`:
        - The JWT you want to decode

    ## Returns:
    - `Dict`:
        - JWT payload
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
