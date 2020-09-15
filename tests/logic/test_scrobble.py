from datetime import datetime, timedelta

import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.db.base import db
from app.db.models import AlbumDb, ArtistDb, ScrobbleDb, SongDb, TagDb
from app.exceptions import IntegrityError
from app.logic import scrobble as scrobble_logic
from app.models.songs import ScrobbleIn
from app.models.tags import TagIn
from app.models.users import RegisterIn
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_scrobble_without_date():
    scrobble = scrobble_logic.scrobble(
        ScrobbleIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1",
            tags=[TagIn(tag_type="type", value="tag")],
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(s for s in ScrobbleDb) == 1
    assert scrobble.date is not None


@db_session
def test_scrobble_with_date():
    date = datetime.now()
    scrobble = scrobble_logic.scrobble(
        ScrobbleIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1",
            tags=[TagIn(tag_type="type", value="tag")],
            date=date,
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(s for s in ScrobbleDb) == 1
    assert scrobble.date == date


@db_session
def test_scrobble_existing_song():
    date = datetime.now()
    mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    scrobble = scrobble_logic.scrobble(
        ScrobbleIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist",
            tags=[TagIn(tag_type="type", value="value")],
            date=date,
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(s for s in ScrobbleDb) == 1
    assert scrobble.date == date


@db_session
def test_recent_plays():
    mixer.cycle(30).blend(ScrobbleDb)
    orm.flush()
    scrobbles = scrobble_logic.recent_plays()
    assert len(scrobbles) == 10
    for idx, scrobble in enumerate(scrobbles):
        if idx > 0:
            assert scrobbles[idx].date < scrobbles[idx - 1].date


@db_session
def test_recent_plays_no_scrobbles():
    orm.flush()
    scrobbles = scrobble_logic.recent_plays()
    assert len(scrobbles) == 0


@db_session
def test_recent_plays_different_page_size():

    mixer.cycle(30).blend(ScrobbleDb)
    orm.flush()
    scrobbles = scrobble_logic.recent_plays(page_size=20)
    assert len(scrobbles) == 20
    for idx, scrobble in enumerate(scrobbles):
        if idx > 0:
            assert scrobbles[idx].date < scrobbles[idx - 1].date


@db_session
def test_recent_plays_min_max_date():
    song = mixer.blend(SongDb)
    mixer.cycle(5).blend(ScrobbleDb, date=datetime.now(), song=song)
    mixer.cycle(5).blend(ScrobbleDb, date=datetime.now() - timedelta(days=6), song=song)
    orm.flush()
    scrobbles = scrobble_logic.recent_plays(min_date=datetime.now() - timedelta(days=4))
    assert len(scrobbles) == 5


@db_session
def test_top_plays():
    song1 = mixer.blend(SongDb)
    song2 = mixer.blend(SongDb)
    mixer.cycle(5).blend(ScrobbleDb, song=song1)
    mixer.cycle(3).blend(ScrobbleDb, song=song2)
    orm.flush()
    songs = scrobble_logic.most_played_songs()
    assert len(songs) == 2
    assert songs[0]["song"] == song1
    assert songs[0]["plays"] == 5
    assert songs[1]["song"] == song2
    assert songs[1]["plays"] == 3


@db_session
def test_top_plays_multiple_users():
    song1 = mixer.blend(SongDb)
    song2 = mixer.blend(SongDb)
    mixer.cycle(5).blend(ScrobbleDb, song=song1)
    mixer.cycle(3).blend(ScrobbleDb, song=song2)
    orm.flush()
    songs = scrobble_logic.most_played_songs()
    assert songs[0]["song"] == song1
    assert songs[0]["plays"] == 5
    assert songs[1]["song"] == song2
    assert songs[1]["plays"] == 3


@db_session
def test_top_plays_no_plays():
    songs = scrobble_logic.most_played_songs()
    assert len(songs) == 0


@db_session
def test_top_plays_min_max_date():
    song = mixer.blend(SongDb)
    mixer.cycle(5).blend(ScrobbleDb, date=datetime.now(), song=song)
    songs = mixer.cycle(5).blend(
        ScrobbleDb, date=datetime.now() - timedelta(days=6), song=song
    )
    orm.flush()
    songs = scrobble_logic.most_played_songs()
    assert len(songs) == 1
    assert songs[0]["plays"] == 10

    songs = scrobble_logic.most_played_songs(
        min_date=datetime.now() - timedelta(days=1)
    )
    orm.commit()
    assert len(songs) == 1
    assert songs[0]["plays"] == 5


@db_session
@pytest.mark.lastfm
def test_sync_lastfm_scrobbles():
    user = mixer.blend(UserDb)
    scrobble_logic.sync_lastfm_scrobbles(user, "Arararararagi")
    assert orm.count(s for s in ScrobbleDb) == 40
    assert orm.count(s for s in SongDb) > 0
    assert orm.count(a for a in ArtistDb) > 0
    assert orm.count(a for a in AlbumDb) > 0
    assert user.last_lastfm_sync is not None
    assert user.last_lastfm_sync.timestamp() == 1584545334


@db_session
@pytest.mark.lastfm
def test_sync_lastfm_scrobbles_since_last_sync():
    user = mixer.blend(UserDb, last_lastfm_sync=datetime.fromtimestamp(1584543600))
    scrobble_logic.sync_lastfm_scrobbles(user, "Arararararagi")
    assert orm.count(s for s in ScrobbleDb) == 5
    assert orm.count(s for s in SongDb) > 0
    assert orm.count(a for a in ArtistDb) > 0
    assert orm.count(a for a in AlbumDb) > 0


@db_session
@pytest.mark.lastfm
def test_sync_lastfm_scrobbles_since_last_sync_exact_date_time():
    user = mixer.blend(UserDb, last_lastfm_sync=datetime.fromtimestamp(1584543120))
    scrobble_logic.sync_lastfm_scrobbles(user, "Arararararagi")
    assert orm.count(s for s in ScrobbleDb) == 7
    assert orm.count(s for s in SongDb) > 0
    assert orm.count(a for a in ArtistDb) > 0
    assert orm.count(a for a in AlbumDb) > 0
