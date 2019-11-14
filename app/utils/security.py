from passlib.context import CryptContext

from app.settings import HASH_ALGORITHMS

pwd_context = CryptContext(schemes=HASH_ALGORITHMS, deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)
