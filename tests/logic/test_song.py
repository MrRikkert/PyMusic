import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.db.base import db
from app.db.models import AlbumDb, ArtistDb, SongDb, TagDb
from app.exceptions import IntegrityError
from app.logic import song as song_logic
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
def test_add_song_existing():
    mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    with pytest.raises(IntegrityError):
        song_logic.add(
            SongIn(
                title="title",
                length=1,
                album="album",
                album_artist="artist",
                artist="artist",
                tags=[TagIn(tag_type="type", value="value")],
            )
        )


@db_session
def test_add_song_existing_with_return_existing():
    db_song = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    song = song_logic.add(
        SongIn(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artist="artist",
            tags=[TagIn(tag_type="type", value="value")],
        ),
        return_existing=True,
    )
    assert db_song.id == song.id


@db_session
def test_add_song_existing_with_update():
    db_song = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    song = song_logic.add(
        SongIn(
            title="title",
            length=1,
            album="album2",
            album_artist="artist2",
            artist="artist",
            tags=[TagIn(tag_type="type2", value="value2")],
        ),
        return_existing=True,
        update_existing=True,
    )
    db.flush()
    assert db_song.id == song.id
    assert len(song.albums) == 2
    assert len(song.tags) == 2

    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 2
    assert orm.count(a for a in ArtistDb) == 2
    assert orm.count(a for a in AlbumDb) == 2


@db_session
def test_add_song_existing_with_replace_exisiting_tags():
    db_song = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    song = song_logic.add(
        SongIn(
            title="title",
            length=1,
            album="album2",
            album_artist="artist2",
            artist="artist",
            tags=[TagIn(tag_type="type2", value="value2")],
        ),
        return_existing=True,
        update_existing=True,
        replace_existing_tags=True,
    )
    db.flush()
    assert db_song.id == song.id
    assert len(song.albums) == 2
    assert len(song.tags) == 1

    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 2
    assert orm.count(a for a in ArtistDb) == 2
    assert orm.count(a for a in AlbumDb) == 2


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
