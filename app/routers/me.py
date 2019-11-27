from fastapi import APIRouter, Depends

from app.db.models import UserDb
from app.models.songs import ScrobbleIn
from app.oath2 import get_current_user

router = APIRouter()


@router.post("/scrobble")
def scrobble(scrobble: ScrobbleIn, user: UserDb = Depends(get_current_user)):
    pass
