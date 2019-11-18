from pydantic import BaseModel, Schema
from typing import List


class BaseSong(BaseModel):
    title: str = Schema(...)
    lenght: int = Schema(...)


class SongIn(BaseSong):
    from app.models.tags import TagIn

    artist: str = Schema(...)
    album: str = Schema(...)
    album_artist: str = Schema(...)
    tags: List[TagIn] = Schema(None)
