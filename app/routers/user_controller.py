from fastapi import APIRouter
from starlette import status

from app.logic import user_logic
from app.models.users import RegisterIn, RegisterOut

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=RegisterOut
)
async def register(register: RegisterIn):
    user_logic.register_user(register)
    return RegisterOut(**register.dict())
