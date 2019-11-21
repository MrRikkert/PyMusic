from pony import orm

from app.db.models import AlbumDb
from app.exceptions import IntegrityError
from app.logic import artist as artist_logic


def get(name: str, artist: str = None) -> AlbumDb:
    """Get album from database

    ## Arguments:
    - `name`: `str`:
        - Name of the album
    - `artist`: `str`, optional:
        - Album artist. Defaults to `None`.

    ## Returns:
    - `AlbumDb`:
        - The album. Returns `None` when no album is found
    """
    album = orm.select(a for a in AlbumDb if a.name == name)
    if artist is not None:
        return album.filter(lambda a: a.album_artist.name == artist).first()
    return album.first()


def exists(name: str, artist: str = None) -> bool:
    """Checks if an album exists in the database

    ## Arguments:
    - `name`: `str`:
        - Name of the album
    - `artist`: `str`, optional:
        - Album artist. Defaults to `None`.

    ## Returns:
    - `bool`:
        - `True` if the album exists and `false` if it doesn't exists
    """
    album = get(name, artist)
    return True if album is not None else False


def add(name: str, artist: str = None, return_existing: bool = False) -> AlbumDb:
    """Add album to the database

    ## Arguments:
    - `name`: `str`:
        - Name of the album
    - `artist`: `str`, optional:
        - Album artist, will add artist to the database if it doesn't exist and use the existing artist if it does.
        Defaults to `None`.
    - `return_existing`: `bool`, optional:
        - Return existing database object when found or not. Defaults to `False`.

    ## Raises:
    - `IntegrityError`:
        - If the album already exists and `return_existing` is `False`

    ## Returns:
    - `AlbumDb`:
        - The created album, or existing album when `return_existing` is `True` and it already exists
    """
    existing = get(name=name, artist=artist)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("album already exists")
        return existing
    return AlbumDb(
        name=name,
        album_artist=artist_logic.add(artist, return_existing=True)
        if artist is not None
        else None,
    )
