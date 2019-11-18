import pytest
from mixer.backend.pony import mixer
from pony import orm
from pony.orm import db_session

from app.db.dao import song as song_dao
from app.db.models import AlbumDb, ArtistDb, SongDb, TagDb
from app.models.songs import Song
from app.models.tags import TagIn
from tests.utils import reset_db


def setup_function():
    reset_db()


@db_session
def test_add_song_correct():
    song_dao.add_song(
        Song(
            title="title",
            length=1,
            album="album",
            album_artist="artist",
            artists=["artist1", "artist2"],
            tags=[TagIn(tag_type="type", value="tag")],
        )
    )
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(t for t in TagDb) == 1
    assert orm.count(a for a in ArtistDb) == 3
    assert orm.count(a for a in AlbumDb) == 1
