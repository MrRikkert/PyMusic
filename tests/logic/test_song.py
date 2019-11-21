from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.logic import song as song_logic
from app.db.models import AlbumDb, ArtistDb, SongDb, TagDb
from app.models.songs import SongIn
from app.models.tags import TagIn
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_add_song_correct():
    song_logic.add(
        SongIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1",
            tags=[TagIn(tag_type="type", value="tag")],
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 1
    assert orm.count(a for a in ArtistDb) == 2
    assert orm.count(a for a in AlbumDb) == 1


@db_session
def test_add_song_multiple_artists():
    song_logic.add(
        SongIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1, artist2",
            tags=[TagIn(tag_type="type", value="tag")],
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 1
    assert orm.count(a for a in ArtistDb) == 3
    assert orm.count(a for a in AlbumDb) == 1


@db_session
def test_add_song_existing_album():
    album = mixer.blend(AlbumDb, album_artist=mixer.blend(ArtistDb))
    song_logic.add(
        SongIn(
            title="title",
            length=1,
            album=album.name,
            album_artist=album.album_artist.name,
            artist="artist1",
            tags=[TagIn(tag_type="type", value="tag")],
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 1
    assert orm.count(a for a in ArtistDb) == 2
    assert orm.count(a for a in AlbumDb) == 1


@db_session
def test_add_song_existing_tag():
    tag = mixer.blend(TagDb)
    song_logic.add(
        SongIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist1",
            tags=[TagIn(tag_type=tag.tag_type, value=tag.value)],
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 1
    assert orm.count(a for a in ArtistDb) == 2
    assert orm.count(a for a in AlbumDb) == 1


@db_session
def test_get_song_single_artist():
    db_song = mixer.blend(SongDb, artists=mixer.blend(ArtistDb, name="artist"))
    song = song_logic.get(title=db_song.title, artists=["artist"])
    assert song is not None
    assert song.title == db_song.title


@db_session
def test_get_song_multiple_artists():
    db_song = mixer.blend(SongDb, artists=mixer.cycle(2).blend(ArtistDb))
    artists = [a.name for a in db_song.artists]
    song = song_logic.get(title=db_song.title, artists=artists)
    assert song is not None
    assert song.title == db_song.title
    assert len(song.artists) == 2


@db_session
def test_get_song_multiple_artists_get_with_one():
    db_song = mixer.blend(SongDb, artists=mixer.cycle(2).blend(ArtistDb))
    artists = [a.name for a in db_song.artists]
    song = song_logic.get(title=db_song.title, artists=[artists[0]])
    assert song is None


@db_session
def test_get_song_none_existing():
    song = song_logic.get(title="title", artists=["artist1", "artist2"])
    assert song is None


@db_session
def test_song_exists_existing():
    db_song = mixer.blend(SongDb, artists=mixer.cycle(2).blend(ArtistDb))
    artists = [a.name for a in db_song.artists]
    exists = song_logic.exists(title=db_song.title, artists=artists)
    assert exists


@db_session
def test_song_exists_non_existing():
    exists = song_logic.exists(title="title", artists=["artist"])
    assert not exists
