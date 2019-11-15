from app.models.users import RegisterIn
from app.utils.security import hash_password
from app.db.dao.user import UserDao
from app.db.models import UserDb
from app.utils.security import verify_password


class UserLogic:
    def register_user(self, register: RegisterIn) -> UserDb:
        """Hashes the password and adds the user to the database"""
        register.password = hash_password(register.password)
        return UserDao.register_user(register)

    def get_user_by_name(self, username: str) -> UserDb:
        """Returns UserDb if user exists, else returns None"""
        return UserDao.get_user_by_name(username)

    def authenticate_user(self, username: str, password: str) -> UserDb:
        """Returns UserDb if authenticated, else returns None"""
        user = self.get_user_by_name(username)
        if user is not None:
            if not verify_password(password, user.password):
                return None
        return user
