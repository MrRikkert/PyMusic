from shared.utils.file import get_normalized_path
from tests.utils import reset_db


def setup_function():
    reset_db()


def test_get_normalized_path_windows():
    rel_path = "C:\\music"
    path = "C:\\music\\artist\\album\\1-1 song.flac"
    path = get_normalized_path(path, rel_path)
    assert path != "artist\\album\\1-1 song.flac"
    assert path == "artist/album/1-1 song.flac"


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
    assert path != "artist\\album\\1-1 song.flac"
    assert path == "artist/album/1-1 song.flac"


def test_get_normalized_path_linux_trailing_slash():
    rel_path = "/usr/music/"
    path = "/usr/music/artist/album/1-1 song.flac"
    path = get_normalized_path(path, rel_path)
    assert path != "artist\\album\\1-1 song.flac"
    assert path == "artist/album/1-1 song.flac"
