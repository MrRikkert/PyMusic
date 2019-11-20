import re
from typing import List

from app.db.models import ArtistDb
from app.exceptions import IntegrityError


def get(name: str) -> ArtistDb:
    return ArtistDb.get(name=name)


def exists(name: str) -> bool:
    artist = get(name)
    return True if artist is not None else False


def add(name: str, return_existing: bool = False) -> ArtistDb:
    existing = get(name)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("artist already exists")
        return existing
    return ArtistDb(name=name)


def split(name: str) -> List[str]:
    artists = re.split(";|,|feat.|×|vs|&", name)
    artists = map(lambda x: x.strip(), artists)
    return list(artists)
