from datetime import datetime
from typing import List

from pydantic import BaseModel, Schema


class BaseSong(BaseModel):
    title: str = Schema(...)
    length: int = Schema(...)


class SongIn(BaseSong):
    from app.models.tags import TagIn

    artist: str = Schema(...)
    album: str = Schema(...)
    album_artist: str = Schema(...)
    tags: List[TagIn] = Schema(None)


class ScrobbleIn(SongIn):
    date: datetime = Schema(datetime.now())


class Song(BaseSong):
    from app.models.tags import TagIn

    artists: List[str] = Schema(..., min_items=1)
    album: str = Schema(...)
    album_artist: str = Schema(...)
    tags: List[TagIn] = Schema(None)
