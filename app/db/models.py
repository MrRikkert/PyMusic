from pony.orm import PrimaryKey, Required
from app.db.base import db


class User(db.Entity):
    id: int = PrimaryKey(int, auto=True)
    name: str = Required(str, unique=True)