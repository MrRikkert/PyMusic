import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.logic import artist as artist_logic
from app.db.models import ArtistDb
from tests.utils import reset_db
from app.exceptions import IntegrityError


def setup_function():
    reset_db()


@db_session
def test_get_artist_existing():
    db_artist = mixer.blend(ArtistDb)
    artist = artist_logic.get_artist(db_artist.name)
    assert artist is not None
    assert db_artist.name == artist.name


@db_session
def test_get_artist_non_existing():
    artist = artist_logic.get_artist("hallo")
    assert artist is None


@db_session
def test_artist_exists_existing():
    db_artist = mixer.blend(ArtistDb)
    exists = artist_logic.artist_exists(db_artist.name)
    assert exists


@db_session
def test_artist_exists_non_existing():
    exists = artist_logic.artist_exists("hallo")
    assert not exists


@db_session
def test_add_artist():
    artist_logic.add_artist("hallo")
    assert orm.count(a for a in ArtistDb) == 1


@db_session
def test_add_artist_existing():
    db_artist = mixer.blend(ArtistDb)
    with pytest.raises(IntegrityError):
        artist_logic.add_artist(db_artist.name)


@db_session
def test_add_artist_existing_with_return_existing():
    db_artist = mixer.blend(ArtistDb)
    artist = artist_logic.add_artist(db_artist.name, return_existing=True)
    assert orm.count(a for a in ArtistDb) == 1
    assert artist is not None
    assert db_artist.id == artist.id


@db_session
def test_split_artist():
    artist = "artist, artist & artist ; artist vs artist & artist feat. artist"
    artists = artist_logic.split_artist(artist)
    assert len(artists) == 7
