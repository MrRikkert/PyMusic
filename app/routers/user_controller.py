from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from app.db.base import db
from app.logic import user as user_logic
from app.models.users import RegisterIn, RegisterOut, UserToken, UserTokenData
from app.utils.security import create_access_token

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=RegisterOut
)
async def register(register: RegisterIn):
    user = user_logic.register(register)
    db.flush()
    return RegisterOut.from_orm(user)


@router.post("/login", response_model=UserToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_logic.authenticate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(UserTokenData(sub=user.username))
    return UserToken(access_token=access_token, token_type="bearer")
