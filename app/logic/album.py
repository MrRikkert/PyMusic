from hashlib import md5
import os
from pony import orm

from app.db.models import AlbumDb
from app.exceptions import IntegrityError
from app.logic import artist as artist_logic
from app.utils.clean import clean_album


def get_by_name(name: str) -> AlbumDb:
    """Get album from database. Case insensitive

    ## Arguments:
    - `name`: `str`:
        - Name of the album

    ## Returns:
    - `AlbumDb`:
        - The album. Returns `None` when no album is found
    """
    name = clean_album(name)
    album = orm.select(a for a in AlbumDb if a.name == name.lower())
    return album.first()


def get_by_id(id: int) -> AlbumDb:
    """Get album from the database by id

    ## Arguments:
    - `id`: `int`:
        - Id of the database

    ## Returns:
    - `AlbumDb`:
        - The found album. Returns `None` when no album is found
    """
    return AlbumDb.get(id=id)


def exists(name: str) -> bool:
    """Checks if an album exists in the database

    ## Arguments:
    - `name`: `str`:
        - Name of the album

    ## Returns:
    - `bool`:
        - `True` if the album exists and `false` if it doesn't exists
    """
    album = get_by_name(name)
    return True if album is not None else False


def add(name: str, artist: str = None, return_existing: bool = False) -> AlbumDb:
    """Add album to the database

    ## Arguments:
    - `name`: `str`:
        - Name of the album
    - `artist`: `str`, optional:
        - Album artist, will add artist to the database if it doesn't exist
        and use the existing artist if it does.
        Defaults to `None`.
    - `return_existing`: `bool`, optional:
        - Return existing database object when found or not. Defaults to `False`.

    ## Raises:
    - `IntegrityError`:
        - If the album already exists and `return_existing` is `False`

    ## Returns:
    - `AlbumDb`:
        - The created album, or existing album when `return_existing` is `True`
        and it already exists
    """
    existing = get_by_name(name=name)

    if existing is not None:
        if not return_existing:
            raise IntegrityError("album already exists")
        if not existing.album_artist and artist:
            existing.album_artist = artist_logic.add(artist, return_existing=True)

        return existing
    album_hash = md5(name.lower().encode("utf-8")).hexdigest()
    name = clean_album(name)
    return AlbumDb(
        name=name.lower(),
        name_alt=name,
        album_artist=artist_logic.add(artist, return_existing=True)
        if artist is not None
        else None,
        art=os.path.join(album_hash[0:2], album_hash + ".png"),
    )
