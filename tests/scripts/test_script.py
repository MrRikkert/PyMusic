import sys

import pytest
from pony import orm
from pony.orm import db_session

from app.db.base import db
from app.db.models import AlbumDb, ArtistDb, SongDb
from app.models.songs import SongIn
from tests.logic.test_song import song_logic
from tests.utils import reset_db


if not sys.platform.startswith("win"):
    pytest.skip("skipping windows-only tests", allow_module_level=True)
else:
    import musicbeeipc


mbipc = musicbeeipc.MusicBeeIPC()  # type: ignore


def setup_function():
    reset_db()


@db_session
# @pytest.mark.mb
def test():
    paths = mbipc.library_search(query="")[:50]
    for path in paths:
        album_artist = mbipc.library_get_file_tag(path, musicbeeipc.MBMD_AlbumArtistRaw)
        song_logic.add(
            SongIn(
                title=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_TrackTitle),
                length=0,
                album=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_Album),
                album_artist=None if not album_artist else album_artist,
                artist=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_Artist),
            )
        )
        db.flush()

    db.commit()
    assert orm.count(s for s in SongDb) > 0
    assert orm.count(s for s in SongDb) <= 50
    assert orm.count(a for a in ArtistDb) > 0
    assert orm.count(a for a in ArtistDb) <= 50
    assert orm.count(a for a in AlbumDb) > 0
    assert orm.count(a for a in AlbumDb) <= 50
