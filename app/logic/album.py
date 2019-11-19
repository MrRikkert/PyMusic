import re
from typing import List
from app.db.base import db
from pony import orm

from app.db.models import AlbumDb
from app.exceptions import IntegrityError


def get_album(name: str, artist: str = None) -> AlbumDb:
    album = orm.select(a for a in AlbumDb if a.name == name)
    if artist is not None:
        return album.filter(lambda a: a.album_artist.name == artist).first()
    return album.first()


def album_exists(name: str, artist: str = None):
    album = get_album(name, artist)
    return True if album is not None else False
