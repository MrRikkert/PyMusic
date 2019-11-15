from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from app.logic.user import UserLogic
from app.models.users import RegisterIn, RegisterOut, UserToken, UserTokenData
from app.utils.security import create_access_token

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=RegisterOut
)
async def register(register: RegisterIn):
    UserLogic.register_user(register)
    return RegisterOut(**register.dict())


@router.post("/login", response_model=UserToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserLogic.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(UserTokenData(sub=user.username))
    return UserToken(access_token=access_token, token_type="bearer")
