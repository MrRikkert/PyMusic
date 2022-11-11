import os
from hashlib import md5

from pony import orm

from shared.db.models import AlbumDb
from shared.exceptions import IntegrityError
from shared.logic import artist as artist_logic
from shared.utils.clean import clean_album


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


def get_album_art_hash(name):
    hash_ = md5(name.lower().encode("utf-8")).hexdigest()
    return os.path.join(hash_[0:2], hash_ + ".png")


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
        return existing
    name = clean_album(name)
    album_hash = get_album_art_hash(name)

    artists = artist_logic.split(artist)
    return AlbumDb(
        name=name.lower(),
        name_alt=name,
        album_artist=artist,
        album_artists=[
            artist_logic.add(artist, return_existing=True) for artist in artists
        ],
        art=album_hash,
    )
