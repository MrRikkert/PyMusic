import pytest


from pony import orm
from pony.orm import db_session

from app.logic import artist as artist_logic
from app.db.models import ArtistDb
from tests.utils import reset_db, mixer
from app.exceptions import IntegrityError


def setup_function():
    reset_db()


@db_session
def test_get_artist_by_name_existing():
    db_artist = mixer.blend(ArtistDb)
    artist = artist_logic.get_by_name(name=db_artist.name)
    assert artist is not None
    assert db_artist.name == artist.name


@db_session
def test_get_artist_by_name_cleaned_name():
    db_artist = mixer.blend(ArtistDb, name="test")
    artist = artist_logic.get_by_name(name="test (cv. test1)")
    assert artist is not None
    assert db_artist.name == artist.name


@db_session
def test_get_artist_by_name_case_difference():
    db_artist = artist_logic.add("Artist")
    artist = artist_logic.get_by_name(name="artist")
    assert artist is not None
    assert db_artist.name == artist.name


@db_session
def test_get_artist_by_name_non_existing():
    artist = artist_logic.get_by_name(name="hallo")
    assert artist is None


@db_session
def test_get_artist_by_name_existing_reversed():
    db_artist = mixer.blend(ArtistDb, name="first second")
    artist = artist_logic.get_by_name(name="second first")
    assert artist is not None
    assert db_artist.name == artist.name


@db_session
def test_get_artist_by_id_non_existing():
    artist = artist_logic.get_by_id(id=1)
    assert artist is None


@db_session
def test_get_artist_by_id_existing():
    db_artist = mixer.blend(ArtistDb)
    orm.flush()
    artist = artist_logic.get_by_id(id=db_artist.id)
    assert artist is not None
    assert db_artist.name == artist.name


@db_session
def test_artist_exists_existing():
    db_artist = mixer.blend(ArtistDb)
    exists = artist_logic.exists(db_artist.name)
    assert exists


@db_session
def test_artist_exists_non_existing():
    exists = artist_logic.exists("hallo")
    assert not exists


@db_session
def test_add_artist():
    artist_logic.add("hallo")
    assert orm.count(a for a in ArtistDb) == 1


@db_session
def test_add_artist_cleaned_name():
    artist = artist_logic.add("hallo (cv. test)")
    assert orm.count(a for a in ArtistDb) == 1
    assert artist.name == "hallo"


@db_session
def test_add_artist_existing():
    db_artist = mixer.blend(ArtistDb)
    with pytest.raises(IntegrityError):
        artist_logic.add(db_artist.name)


@db_session
def test_add_artist_existing_with_return_existing():
    db_artist = mixer.blend(ArtistDb)
    artist = artist_logic.add(db_artist.name, return_existing=True)
    assert orm.count(a for a in ArtistDb) == 1
    assert artist is not None
    assert db_artist.id == artist.id


@db_session
def test_split_artist():
    artist = "artist1, artist2 & artist3 ; artist4 vs artist5 & artist6 feat. artist7"
    artists = artist_logic.split(artist)
    assert len(artists) == 7


@db_session
def test_split_artist_same_name():
    artist = "artist, artist & artist ; artist vs artist & artist feat. artist"
    artists = artist_logic.split(artist)
    assert len(artists) == 1
