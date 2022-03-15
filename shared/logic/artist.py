from typing import List

from shared.db.models import ArtistDb
from shared.exceptions import IntegrityError
from shared.utils.clean import (
    clean_artist,
    get_character_voice,
    reverse_artist,
    split_artists,
)


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


def add(name: str, return_existing: bool = False, update_existing=True) -> ArtistDb:
    """Add artist to the database

    ## Arguments:
    - `name`: `str`:
        - Name of the artist
    - `return_existing`: `bool`, optional:
        - Return existing database object when found or not. Defaults to `False`.
    - `update_existing`: `bool`, optional:
        - Update the existing artist when found or not.
        Only updates the `character_voice` property
        `return_existing` also needs to be `True` for this to work.
        Defaults to `False`.

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
        elif update_existing:
            cv = get_character_voice(name)
            if cv:
                existing.character_voice = ArtistDb(name=cv.lower(), name_alt=cv)
        return existing
    name, cv = clean_artist(name, return_character_voice=True)
    if cv:
        cv = add(cv, return_existing=True)
    return ArtistDb(name=name.lower(), name_alt=name, character_voice=cv)


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
