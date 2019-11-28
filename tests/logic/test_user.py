from datetime import datetime

import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.db.base import db
from app.db.models import AlbumDb, ArtistDb, ScrobbleDb, SongDb, TagDb, UserDb
from app.exceptions import IntegrityError
from app.logic import user as user_logic
from app.models.songs import ScrobbleIn
from app.models.tags import TagIn
from app.models.users import RegisterIn
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_register_user():
    user = RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    db_user = user_logic.register(user)
    db.flush()
    assert orm.count(u for u in UserDb) == 1
    assert db_user.username == user.username
    assert db_user.password != user.password
    assert db_user.email == user.email
    assert db_user.id is not None


@db_session
def test_register_user_username_exists():
    user1 = mixer.blend(UserDb)
    user2 = RegisterIn(
        username=user1.username, email="email@email.com", password="Abc@123!"
    )
    with pytest.raises(IntegrityError, match="Username"):
        user_logic.register(user2)


@db_session
def test_username_exists_non_existing():
    exists = user_logic.exists("test")
    assert not exists


@db_session
def test_username_exists_existing():
    user = mixer.blend(UserDb)
    exists = user_logic.exists(user.username)
    assert exists


@db_session
def test_get_user_by_name_non_existing():
    user = user_logic.get("test")
    assert user is None


@db_session
def test_get_user_by_name_existing():
    user_db = mixer.blend(UserDb)
    user = user_logic.get(user_db.username)
    assert user is not None


@db_session
def test_authenticate_user_correct():
    user = user_logic.register(
        RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    )
    user_auth = user_logic.authenticate("username", "Abc@123!")
    assert user_auth is not None
    assert user.username == user_auth.username
    assert user.email == user_auth.email


@db_session
def test_authenticate_user_wrong_password():
    user_logic.register(
        RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    )
    user_auth = user_logic.authenticate("username", "Abc@123")
    assert user_auth is None


@db_session
def test_authenticate_user_wrong_username():
    user_logic.register(
        RegisterIn(username="username", email="email@email.com", password="Abc@123!")
    )
    user_auth = user_logic.authenticate("usernames", "Abc@123!")
    assert user_auth is None


@db_session
def test_scrobble_without_date():
    user = mixer.blend(UserDb)
    scrobble = user_logic.scrobble(
        user,
        ScrobbleIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1",
            tags=[TagIn(tag_type="type", value="tag")],
        ),
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(s for s in ScrobbleDb) == 1
    assert scrobble.date is not None
    assert len(user.scrobbles) == 1


@db_session
def test_scrobble_with_date():
    date = datetime.now()
    user = mixer.blend(UserDb)
    scrobble = user_logic.scrobble(
        user,
        ScrobbleIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1",
            tags=[TagIn(tag_type="type", value="tag")],
            date=date,
        ),
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(s for s in ScrobbleDb) == 1
    assert scrobble.date == date
    assert len(user.scrobbles) == 1


@db_session
def test_scrobble_existing_song():
    date = datetime.now()
    user = mixer.blend(UserDb)
    mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    scrobble = user_logic.scrobble(
        user,
        ScrobbleIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist",
            tags=[TagIn(tag_type="type", value="value")],
            date=date,
        ),
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(s for s in ScrobbleDb) == 1
    assert scrobble.date == date
    assert len(user.scrobbles) == 1


@db_session
def test_recent_plays():
    user = mixer.blend(UserDb, scrobbles=mixer.cycle(30).blend(ScrobbleDb))
    orm.flush()
    scrobbles = user_logic.recent_plays(user)
    assert len(scrobbles) == 10
    for idx, scrobble in enumerate(scrobbles):
        if idx > 0:
            assert scrobbles[idx].date < scrobbles[idx - 1].date


@db_session
def test_recent_plays_multiple_users():
    user = mixer.blend(UserDb, scrobbles=mixer.cycle(15).blend(ScrobbleDb))
    mixer.cycle(15).blend(ScrobbleDb, user=mixer.blend(UserDb))
    orm.flush()
    scrobbles = user_logic.recent_plays(user)
    assert len(scrobbles) == 10
    for idx, scrobble in enumerate(scrobbles):
        assert scrobble.user == user
        if idx > 0:
            assert scrobbles[idx].date < scrobbles[idx - 1].date


@db_session
def test_recent_plays_no_scrobbles():
    user = mixer.blend(UserDb)
    orm.flush()
    scrobbles = user_logic.recent_plays(user)
    assert len(scrobbles) == 0


@db_session
def test_recent_plays_different_page_size():
    user = mixer.blend(UserDb, scrobbles=mixer.cycle(25).blend(ScrobbleDb))
    orm.flush()
    scrobbles = user_logic.recent_plays(user, page_size=20)
    assert len(scrobbles) == 20
    for idx, scrobble in enumerate(scrobbles):
        assert scrobble.user == user
        if idx > 0:
            assert scrobbles[idx].date < scrobbles[idx - 1].date


@db_session
def test_top_plays():
    user = mixer.blend(UserDb)
    song1 = mixer.blend(SongDb)
    song2 = mixer.blend(SongDb)
    mixer.cycle(5).blend(ScrobbleDb, song=song1, user=user)
    mixer.cycle(3).blend(ScrobbleDb, song=song2, user=user)
    orm.flush()
    songs = user_logic.top_plays_song(user)
    assert len(songs) == 2
    assert songs[0]["song"] == song1
    assert songs[0]["plays"] == 5
    assert songs[1]["song"] == song2
    assert songs[1]["plays"] == 3


@db_session
def test_top_plays_multiple_users():
    user = mixer.blend(UserDb)
    mixer.blend(UserDb, scrobbles=mixer.cycle(10).blend(ScrobbleDb))
    song1 = mixer.blend(SongDb)
    song2 = mixer.blend(SongDb)
    mixer.cycle(5).blend(ScrobbleDb, song=song1, user=user)
    mixer.cycle(3).blend(ScrobbleDb, song=song2, user=user)
    orm.flush()
    songs = user_logic.top_plays_song(user)
    assert len(songs) == 2
    assert songs[0]["song"] == song1
    assert songs[0]["plays"] == 5
    assert songs[1]["song"] == song2
    assert songs[1]["plays"] == 3


@db_session
def test_top_plays_no_plays():
    user = mixer.blend(UserDb)
    orm.flush()
    songs = user_logic.top_plays_song(user)
    assert len(songs) == 0
