from app.models.users import RegisterIn
from app.db.models import UserDb


class UserDao:
    def register_user(self, user: RegisterIn) -> UserDb:
        """Adds user to the database"""
        return UserDb(**user.dict())

    def get_user_by_name(self, username: str) -> UserDb:
        """Returns UserDb if user exists, else returns None"""
        return UserDb.get(username=username)
