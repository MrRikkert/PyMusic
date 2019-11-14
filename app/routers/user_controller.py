from fastapi import APIRouter

from app.models.users import Register
from app.logic import user_logic

router = APIRouter()


@router.post("/register")
async def register(register: Register):
    return user_logic.register_user(register)
