import os

import pytest
from pony import orm
from pony.orm import db_session

from shared.db.models import AlbumDb, ArtistDb
from shared.exceptions import IntegrityError
from shared.logic import album as album_logic
from tests.utils import mixer, reset_db


def setup_function():
    reset_db()


@db_session
def test_get_album_by_name():
    db_album = mixer.blend(AlbumDb)
    album = album_logic.get_by_name(name=db_album.name)
    assert album is not None


@db_session
def test_get_album_by_name_case_difference():
    album_logic.add(name="album", artist="artist")
    album = album_logic.get_by_name(name="album")
    assert album is not None


@db_session
def test_get_album_by_name_no_album_artist():
    db_album = mixer.blend(AlbumDb)
    album = album_logic.get_by_name(name=db_album.name)
    assert album is not None


@db_session
def test_get_album_by_name_no_non_existing():
    album = album_logic.get_by_name(name="hallo")
    assert album is None


@db_session
def test_get_album_by_id_non_existing():
    album = album_logic.get_by_id(id=1)
    assert album is None


@db_session
def test_get_album_by_id_existing():
    album_db = mixer.blend(AlbumDb)
    orm.flush()
    album = album_logic.get_by_id(id=album_db.id)
    assert album is not None


@db_session
def test_album_exists_existing():
    db_album = mixer.blend(AlbumDb)
    exists = album_logic.exists(name=db_album.name)
    assert exists


@db_session
def test_album_exists_non_existing():
    exists = album_logic.exists(name="hallo")
    assert not exists


@db_session
def test_add_album_without_artist():
    with pytest.raises(Exception):
        album_logic.add(name="album")


@db_session
def test_add_album_correct_alt_name():
    album = album_logic.add(name="album disc 1", artist="artist")
    assert orm.count(a for a in AlbumDb) == 1
    assert album.name_alt == "album"


@db_session
def test_add_album_correct_cased_alt_name():
    album = album_logic.add(name="Album disc 1", artist="artist")
    assert orm.count(a for a in AlbumDb) == 1
    assert album.name_alt == "Album"
    assert album.name == "album"


@db_session
def test_add_album_with_artist():
    album_logic.add(name="album", artist="artist")
    assert orm.count(a for a in AlbumDb) == 1
    assert orm.count(a for a in ArtistDb) == 1


@db_session
def test_add_album_with_multiple_artists():
    album_logic.add(name="album", artist="artist, artist2")
    assert orm.count(a for a in AlbumDb) == 1
    assert orm.count(a for a in ArtistDb) == 2


@db_session
def test_add_album_existing_artist():
    artist = mixer.blend(ArtistDb)
    album_logic.add(name="album", artist=artist.name)
    assert orm.count(a for a in AlbumDb) == 1
    assert orm.count(a for a in ArtistDb) == 1


@db_session
def test_add_album_existing_album():
    album = mixer.blend(AlbumDb)
    with pytest.raises(IntegrityError):
        album_logic.add(name=album.name)


@db_session
def test_add_album_existing_album_with_return_existing():
    db_album = mixer.blend(AlbumDb)
    album = album_logic.add(name=db_album.name, return_existing=True)
    assert orm.count(a for a in AlbumDb) == 1
    assert album is not None
    assert db_album.id == album.id


@db_session
def test_add_album_correct_hash():
    album = album_logic.add(name="album disc 1", artist="artist")
    assert album.art == os.path.join("a4", "a4b2d20f456833bcdac42e73edad64c0.png")

    album = album_logic.add(name="Album2", artist="artist")
    assert album.art == os.path.join("f8", "f8d7bd28b526864cf358256ca7b041c6.png")

    album = album_logic.add(name="Test Album (Disc 1)", artist="artist")
    assert album.art == os.path.join("68", "68798d8741b8c53335aadcc9eb291ad1.png")
