import platform

import pytest
from pony.orm import db_session

from shared.db.models import FileDb, SongDb
from shared.models.songs import File
from shared.settings import TAG_LIST
from shared.utils.file import get_normalized_path, get_tags
from tests.utils import mixer, reset_db


def setup_function():
    reset_db()


@pytest.mark.skipif(
    platform.system() != "Windows", reason="Linux/MacOs fail with windows-like paths"
)
def test_get_normalized_path_windows():
    rel_path = "C:\\music"
    path = "C:\\music\\artist\\album\\1-1 song.flac"
    path = get_normalized_path(path, rel_path)
    assert path != "artist/album/1-1 song.flac"
    assert path == "music/artist/album/1-1 song.flac"


@pytest.mark.skipif(
    platform.system() != "Windows", reason="Linux/MacOs fail with windows-like paths"
)
def test_get_normalized_path_windows_trailing_slash():
    rel_path = "C:\\music\\"
    path = "C:\\music\\artist\\album\\1-1 song.flac"
    path = get_normalized_path(path, rel_path)
    assert path != "artist\\album\\1-1 song.flac"
    assert path == "artist/album/1-1 song.flac"


def test_get_normalized_path_linux():
    rel_path = "/usr/music"
    path = "/usr/music/artist/album/1-1 song.flac"
    path = get_normalized_path(path, rel_path)
    assert path != "artist/album/1-1 song.flac"
    assert path == "music/artist/album/1-1 song.flac"


def test_get_normalized_path_linux_trailing_slash():
    rel_path = "/usr/music/"
    path = "/usr/music/artist/album/1-1 song.flac"
    path = get_normalized_path(path, rel_path)
    assert path != "artist\\album\\1-1 song.flac"
    assert path == "artist/album/1-1 song.flac"


def test_get_tags_File_object():
    file = File(path="", artist="", album="", title="")
    for tag in TAG_LIST:
        file[tag] = f"{tag} 1"

    tags = get_tags(file)
    assert len(tags) == len(TAG_LIST)


@db_session
def test_get_tags_FileDb_object():
    file = mixer.blend(FileDb, song=mixer.blend(SongDb))
    for tag in TAG_LIST:
        file[tag] = f"{tag} 1"

    tags = get_tags(file)
    assert len(tags) == len(TAG_LIST)
