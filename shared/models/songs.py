from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from shared.models.artists import ArtistLastFm


class CustomBaseModel(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k in args:
            setattr(self, k, args[k])

    def __getitem__(self, item):
        return getattr(self, item)


class BaseSong(CustomBaseModel):
    title: str = Field(...)
    length: int = Field(None)


class File(BaseSong):
    path: str = Field(...)
    artist: str = Field(...)
    album: str = Field(...)
    album_artist: str = Field(None)
    genre: str = Field(None)
    vocals: str = Field(None)
    series: str = Field(None)
    franchise: str = Field(None)
    op_ed: str = Field(None)
    season: str = Field(None)
    alternate: str = Field(None)
    type: str = Field(None)
    sort_artist: str = Field(None)
    language: str = Field(None)


class SongIn(BaseSong):
    from shared.models.tags import TagIn

    artist: str = Field(...)
    album: str = Field(...)
    album_artist: str = Field(None)
    tags: Optional[List[TagIn]] = Field([])


class ScrobbleIn(SongIn):
    date: datetime = Field(datetime.now())


class Song(BaseSong):
    from shared.models.tags import TagIn

    artists: List[str] = Field(..., min_items=1)
    album: str = Field(...)
    album_artist: str = Field(...)
    tags: List[TagIn] = Field(None)


class SongLastFm(CustomBaseModel):
    title: str = Field(...)
    artist: ArtistLastFm = Field(...)

    class Config:
        orm_mode = True


class ScrobbleLastFm(CustomBaseModel):
    album: str = Field(None)
    timestamp: datetime = Field(...)
    track: SongLastFm = Field(...)

    class Config:
        orm_mode = True
