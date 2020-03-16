from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.models.artists import ArtistLastFm


class BaseSong(BaseModel):
    title: str = Field(...)
    length: int = Field(...)


class SongIn(BaseSong):
    from app.models.tags import TagIn

    artist: str = Field(...)
    album: str = Field(...)
    album_artist: str = Field(...)
    tags: List[TagIn] = Field(None)


class ScrobbleIn(SongIn):
    date: datetime = Field(datetime.now())


class Song(BaseSong):
    from app.models.tags import TagIn

    artists: List[str] = Field(..., min_items=1)
    album: str = Field(...)
    album_artist: str = Field(...)
    tags: List[TagIn] = Field(None)


class SongLastFm(BaseModel):
    title: str = Field(...)
    artist: ArtistLastFm = Field(...)

    class Config:
        orm_mode = True


class ScrobbleLastFm(BaseModel):
    album: str = Field(None)
    timestamp: datetime = Field(...)
    track: SongLastFm = Field(...)

    class Config:
        orm_mode = True
