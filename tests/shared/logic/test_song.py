import pytest
from pony import orm
from pony.orm import db_session

from shared.db.base import db
from shared.db.models import AlbumDb, ArtistDb, FileDb, SongDb, TagDb
from shared.exceptions import IntegrityError
from shared.logic import song as song_logic
from shared.models.songs import SongIn
from shared.models.tags import TagIn
from tests.utils import mixer, reset_db


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
def test_add_song_cased_alt_title():
    song = song_logic.add(
        SongIn(
            title="Title",
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
    assert song.title == "title"
    assert song.title_alt == "Title"


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
    artist = mixer.blend(ArtistDb)
    album = mixer.blend(AlbumDb, album_artists=artist, album_artist=artist.name)
    song_logic.add(
        SongIn(
            title="title",
            length=1,
            album=album.name,
            album_artist=album.album_artist,
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
def test_add_song_existing_with_return_existing_cleaned_artist():
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
            artist="artist (cv. hallo)",
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
def test_add_song_existing_add_length():
    db_song = mixer.blend(
        SongDb, length=None, title="title", artists=mixer.blend(ArtistDb, name="artist")
    )
    song = song_logic.add(
        SongIn(
            title="title",
            artist="artist",
            length=250,
            album="album2",
            album_artist="artist",
        ),
        return_existing=True,
        update_existing=True,
    )
    db.flush()

    assert db_song.id == song.id
    assert orm.count(s for s in SongDb) == 1
    assert db_song.length == song.length


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
def test_update_song():
    db_song = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    song = song_logic.update(
        db_song,
        SongIn(
            title="title",
            length=1,
            album="album2",
            album_artist="artist2",
            artist="artist",
            tags=[TagIn(tag_type="type2", value="value2")],
        ),
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
def test_update_song_add_length():
    db_song = mixer.blend(
        SongDb, length=None, title="title", artists=mixer.blend(ArtistDb, name="artist")
    )
    song = song_logic.update(
        db_song,
        SongIn(
            title="title",
            artist="artist",
            length=250,
            album="album2",
            album_artist="artist",
        ),
    )
    db.flush()

    assert db_song.id == song.id
    assert orm.count(s for s in SongDb) == 1
    assert db_song.length == song.length


@db_session
def test_update_song_with_replace_exisiting_tags():
    db_song = mixer.blend(
        SongDb,
        title="title",
        albums=mixer.blend(AlbumDb, name="album"),
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=mixer.blend(TagDb, tag_type="type", value="value"),
    )
    song = song_logic.update(
        db_song,
        SongIn(
            title="title",
            length=1,
            album="album2",
            album_artist="artist2",
            artist="artist",
            tags=[TagIn(tag_type="type2", value="value2")],
        ),
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
def test_get_song_multiple_artists_case_difference():
    db_song = song_logic.add(
        SongIn(
            title="Title",
            album="Album",
            length=180,
            artist="Artist1, Artist2",
            album_artist="Artist1, Artist2",
        )
    )
    artists = [a.name.lower() for a in db_song.artists]
    song = song_logic.get(title="title", artists=artists)
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


@db_session
def test_add_songs_same_title_different_artist():
    db_song_1 = song_logic.add(
        SongIn(
            title="Close Your Eyes",
            album="Super Eurobeat Vol. 75",
            album_artist="Various Artists",
            length=180,
            artist="Sonya",
            tags=[TagIn(tag_type="type", value="Eurobeat")],
        ),
        return_existing=True,
        update_existing=True,
    )
    db_song_2 = song_logic.add(
        SongIn(
            title="close your eyes",
            album="Guilty Crown Original Soundtrack",
            album_artist="Various",
            length=180,
            artist="Honda Michiyo",
            tags=[TagIn(tag_type="type", value="Anime")],
        ),
        return_existing=True,
        update_existing=True,
    )
    db_song_3 = song_logic.add(
        SongIn(
            title="Close Your Eyes",
            album="Super Eurobeat Vol. 75",
            album_artist="Various Artists",
            length=180,
            artist="Sonya",
            tags=[TagIn(tag_type="type", value="Eurobeat")],
        ),
        return_existing=True,
        update_existing=True,
    )
    assert db_song_1 == db_song_3
    assert not db_song_1 == db_song_2


@db_session
def test_update_from_files():
    song_db = mixer.blend(
        SongDb,
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=[
            mixer.blend(TagDb, tag_type="season", value="season 0"),
            mixer.blend(TagDb, tag_type="series", value="series 1"),
        ],
    )
    db.flush()
    mixer.blend(FileDb, song=song_db, season="season 1")
    mixer.blend(FileDb, song=song_db, season="season 2")
    song_logic.update_from_files(song_db)

    assert orm.count(t for t in TagDb) == 4
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(f for f in FileDb) == 2
    assert len(song_db.tags) == 2


@db_session
def test_update_from_files_no_files():
    song_db = mixer.blend(
        SongDb,
        artists=mixer.blend(ArtistDb, name="artist"),
        tags=[
            mixer.blend(TagDb, tag_type="season", value="season 0"),
            mixer.blend(TagDb, tag_type="series", value="series 1"),
        ],
    )
    db.flush()
    song_logic.update_from_files(song_db)

    assert orm.count(t for t in TagDb) == 2
    assert orm.count(s for s in SongDb) == 1
    assert orm.count(f for f in FileDb) == 0
    assert len(song_db.tags) == 2
