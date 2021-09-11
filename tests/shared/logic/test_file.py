import pytest
from pony import orm
from pony.orm import db_session

from shared.db.base import db
from shared.db.models import AlbumDb, ArtistDb, FileDb, SongDb, TagDb
from shared.exceptions import IntegrityError
from shared.logic import file as file_logic
from shared.models.songs import SongIn
from shared.models.tags import TagIn
from tests.utils import reset_db, mixer


def setup_function():
    reset_db()


@db_session
def test_get_file_existing():
    path = "/music/album/1 - 1 song.flac"
    db_file = mixer.blend(FileDb, path=path)
    file = file_logic.get(path)
    assert file is not None
    assert file.path == db_file.path


@db_session
def test_get_file_non_existing():
    path = "/music/album/1 - 1 song.flac"
    file = file_logic.get(path)
    assert file is None


@db_session
def test_file_existst_existing():
    path = "/music/album/1 - 1 song.flac"
    mixer.blend(FileDb, path=path)
    exists = file_logic.exists(path)
    assert exists


@db_session
def test_file_existst_non_existing():
    path = "/music/album/1 - 1 song.flac"
    exists = file_logic.exists(path)
    assert not exists
