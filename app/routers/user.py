from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.db.base import db
from app.db.models import UserDb
from app.exceptions import IntegrityError
from app.logic import user as user_logic
from app.models.songs import ScrobbleIn
from app.models.users import LoginOut, RegisterIn, RegisterOut, UserTokenData
from app.oath2 import get_current_user
from app.utils.security import create_access_token

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=RegisterOut
)
async def register(register: RegisterIn):
    try:
        user = user_logic.register(register)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e),
        )
    db.flush()
    return RegisterOut.from_orm(user)


@router.post("/login", response_model=LoginOut)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_logic.authenticate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(UserTokenData(sub=user.username))
    return LoginOut(
        access_token=access_token, token_type="bearer", username=user.username
    )


@router.post("/scrobble")
def scrobble(scrobble: ScrobbleIn, user: UserDb = Depends(get_current_user)):
    pass
