import re
from typing import List

from app.db.models import ArtistDb
from app.exceptions import IntegrityError


def get_artist(name: str) -> ArtistDb:
    return ArtistDb.get(name=name)


def artist_exists(name: str) -> bool:
    artist = get_artist(name)
    return True if artist is not None else False


def add_artist(name: str, return_existing: bool = False) -> ArtistDb:
    existing = get_artist(name)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("artist already exists")
        return existing
    return ArtistDb(name=name)


def split_artist(name: str) -> List[str]:
    artists = re.split(";|,|feat.|×|vs|&", name)
    artists = map(lambda x: x.strip(), artists)
    return list(artists)
