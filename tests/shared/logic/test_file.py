from datetime import datetime

from pony import orm
from pony.orm import db_session

from shared.db.models import AlbumDb, ArtistDb, FileDb, SongDb, TagDb
from shared.logic import file as file_logic
from shared.models.songs import File
from tests.utils import mixer, reset_db


def setup_function():
    reset_db()


@db_session
def test_add_file_non_existing_file_and_song():
    file_logic.add(
        File(
            path="/music/artist/album/1 - 1 song.flac",
            title="title",
            artist="artist",
            album="album",
            album_artist="artist_album",
            length=120,
            date_added=datetime.now(),
            bitrate=320,
            sample_rate=44100,
            file_size=1000,
        )
    )
    assert orm.count(f for f in FileDb) == 1
    assert orm.count(s for s in SongDb) == 1


@db_session
def test_add_file_non_existing_file_and_existing_song():
    artist = mixer.blend(ArtistDb, name="artist")
    mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(
            AlbumDb, name="album", album_artists=artist, album_artist=artist.name
        ),
        artists=artist,
    )

    file_logic.add(
        File(
            path="/music/artist/album/1 - 1 song.flac",
            title="title",
            artist="artist",
            album="album",
            album_artist="artist",
            length=120,
            date_added=datetime.now(),
            bitrate=320,
            sample_rate=44100,
            file_size=1000,
        )
    )
    assert orm.count(f for f in FileDb) == 1
    assert orm.count(s for s in SongDb) == 1


@db_session
def test_add_file_existing_file_song():
    artist = mixer.blend(ArtistDb, name="artist")
    song_db = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(
            AlbumDb, name="album", album_artists=artist, album_artist=artist.name
        ),
        artists=artist,
    )
    mixer.blend(FileDb, path="/music/artist/album/1 - 1 song.flac", song=song_db)

    file_logic.add(
        File(
            path="/music/artist/album/1 - 1 song.flac",
            title="title",
            artist="artist",
            album="album",
            album_artist="artist",
        )
    )
    assert orm.count(f for f in FileDb) == 1
    assert orm.count(s for s in SongDb) == 1


@db_session
def test_add_file_existing_file_song_updated():
    artist = mixer.blend(ArtistDb, name="artist")
    song_db = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(
            AlbumDb, name="album", album_artists=artist, album_artist=artist.name
        ),
        artists=artist,
        tags=mixer.blend(TagDb, tag_type="genre", value="genre 1"),
    )
    mixer.blend(
        FileDb,
        path="/music/artist/album/1 - 1 song.flac",
        song=song_db,
        genre="genre 1",
    )

    file = file_logic.add(
        File(
            path="/music/artist/album/1 - 1 song.flac",
            title="title",
            artist="artist",
            album="album",
            album_artist="artist",
            genre="genre 2",
        )
    )
    assert orm.count(f for f in FileDb) == 1
    assert orm.count(s for s in SongDb) == 1
    assert file.genre == "genre 2"
    assert len(file.song.tags) == 2


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


@db_session
def test_get_library_files():
    files = file_logic.get_library_files("./tests/data/MusicBeeLibrary.mbl")
    assert len(files) == 32785  # Size of test library
