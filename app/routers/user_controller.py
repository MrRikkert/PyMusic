from fastapi import APIRouter

from app.db.models import User

router = APIRouter()


@router.get("/")
async def read_items():
    User(name="hallo")
    return [{"name": "Item Foo"}, {"name": "item Bar"}]
