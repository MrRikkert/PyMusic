from pony import orm

from app.db.models import AlbumDb
from app.exceptions import IntegrityError
from app.logic import artist as artist_logic


def get(name: str, artist: str = None) -> AlbumDb:
    album = orm.select(a for a in AlbumDb if a.name == name)
    if artist is not None:
        return album.filter(lambda a: a.album_artist.name == artist).first()
    return album.first()


def exists(name: str, artist: str = None):
    album = get(name, artist)
    return True if album is not None else False


def add(name: str, artist: str = None, return_existing: bool = False) -> AlbumDb:
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
