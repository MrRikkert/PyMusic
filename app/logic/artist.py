from typing import List

from app.db.models import ArtistDb
from app.exceptions import IntegrityError
from app.utils.clean import clean_artist, reverse_artist, split_artists


def get_by_name(name: str) -> ArtistDb:
    """Get artist from database. Case insensitive. Also checks if the reverse exists
    ("Keiichi Okabe" and "Okabe Keiichi")

    ## Arguments:
    - `name`: `str`:
        - Name of the artist

    ## Returns:
    - `ArtistDb`:
        - The found artist. Returns `None` when no artist is found
    """
    name = clean_artist(name).lower()
    reversed_artist = reverse_artist(name)
    if reversed_artist:
        return ArtistDb.get(lambda a: a.name == name or a.name == reversed_artist)
    return ArtistDb.get(lambda a: a.name == name)


def get_by_id(id: int) -> ArtistDb:
    """Get artist from database

    ## Arguments:
    - `id`: `int`:
        - Id of the artist

    ## Returns:
    - `ArtistDb`:
        - The found artist. Returns `None` when no artist is found
    """
    return ArtistDb.get(id=id)


def exists(name: str) -> bool:
    """Check if the artist already exists in the database

    ## Arguments:
    - `name`: `str`:
        - Name of the artist

    ## Returns:
    - `bool`:
        - `True` when artist exists, `False` when it doesn't
    """
    artist = get_by_name(name=name)
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
    existing = get_by_name(name=name)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("artist already exists")
        return existing
    name = clean_artist(name)
    return ArtistDb(name=name.lower(), name_alt=name)


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
    artists = split_artists(name)
    artists = map(lambda x: x.strip(), artists)
    return set(artists)
