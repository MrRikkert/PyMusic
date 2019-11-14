from pony.orm import PrimaryKey, Required
from app.db.base import db


class User(db.Entity):
    id: int = PrimaryKey(int, auto=True)
    username: str = Required(str, unique=True)
    email: str = Required(str, unique=True)
    password: str = Required(str)
