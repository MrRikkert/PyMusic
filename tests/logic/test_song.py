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
    song_logic.add_song(
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
    song_logic.add_song(
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
    song_logic.add_song(
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
    song_logic.add_song(
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
