from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from pony.orm import db_session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


@db_session
def get_current_user(token: str = Depends(oauth2_scheme)):
    from app.logic import user as user_logic

    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = user_logic.get(username)
    if user is None:
        raise credentials_exception
    return user
