import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.logic import album as album_logic
from app.db.models import AlbumDb, ArtistDb
from tests.utils import reset_db
from app.exceptions import IntegrityError


def setup_function():
    reset_db()


@db_session
def test_get_album():
    db_album = mixer.blend(AlbumDb, album_artist=mixer.blend(ArtistDb))
    album = album_logic.get_album(name=db_album.name, artist=db_album.album_artist.name)
    assert album is not None


@db_session
def test_get_album_no_album_artist():
    db_album = mixer.blend(AlbumDb)
    album = album_logic.get_album(name=db_album.name)
    assert album is not None


@db_session
def test_get_album_no_non_existing():
    album = album_logic.get_album(name="hallo")
    assert album is None


@db_session
def test_album_exists_existing():
    db_album = mixer.blend(AlbumDb)
    exists = album_logic.album_exists(name=db_album.name)
    assert exists


@db_session
def test_album_exists_non_existing():
    exists = album_logic.album_exists(name="hallo")
    assert not exists
