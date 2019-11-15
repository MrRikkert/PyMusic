from pony.orm import PrimaryKey, Required

from app.db.base import db


class UserDb(db.Entity):
    _table_ = "user"
    id: int = PrimaryKey(int, auto=True)
    username: str = Required(str, unique=True)
    email: str = Required(str, unique=True)
    password: str = Required(str)
