import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.models.users import UserTokenData
from app.settings import ALGORITHM, HASH_ALGORITHMS, SECRET_KEY

pwd_context = CryptContext(schemes=HASH_ALGORITHMS, deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    """Returns True when passwords match, else returns False"""
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: UserTokenData):
    """Creates jwt token based on UserTokenData"""
    data = data.dict()
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
