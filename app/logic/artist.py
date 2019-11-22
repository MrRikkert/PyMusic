import re
from typing import List

from app.db.models import ArtistDb
from app.exceptions import IntegrityError


def get(name: str) -> ArtistDb:
    """Get artist from database

    ## Arguments:
    - `name`: `str`:
        - Name of the artist

    ## Returns:
    - `ArtistDb`:
        - The found artist. Returns `None` when no artist is found
    """
    return ArtistDb.get(name=name)


def exists(name: str) -> bool:
    """Check if the artist already exists in the database

    ## Arguments:
    - `name`: `str`:
        - Name of the artist

    ## Returns:
    - `bool`:
        - `True` when artist exists, `False` when it doesn't
    """
    artist = get(name)
    return True if artist is not None else False


def add(name: str, return_existing: bool = False) -> ArtistDb:
    """Add artist to the database

    ## Arguments:
    - `name`: `str`:
        - Name of the artist
    - `return_existing`: `bool`, optional:
        - Return existing database object when found or not. Defaults to `False`.

    ## Raises:
    - `IntegrityError`:
        - If the artist already exists and `return_existing` is `False`

    ## Returns:
    - `ArtistDb`:
        - The created artist, or existing artist when `return_existing` is `True`
        and it already exists
    """
    existing = get(name)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("artist already exists")
        return existing
    return ArtistDb(name=name)


def split(name: str) -> List[str]:
    """Split artist name to multiple artists

    Delimeters used: ';', ',', "feat.", '×', "vs" and '&'

    ## Arguments:
    - `name`: `str`:
        - Artist name

    ## Returns:
    - `List[str]`:
        - List of artist names
    """
    artists = re.split(";|,|feat.|×|vs|&", name)
    artists = map(lambda x: x.strip(), artists)
    return list(artists)
