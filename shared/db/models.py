from datetime import datetime

from pony.orm import Optional, PrimaryKey, Required, Set, composite_index, composite_key

from shared.db.base import db


class BaseMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k in args:
            setattr(self, k, args[k])

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, attr, value):
        setattr(self, attr, value)


class ScrobbleDb(db.Entity, BaseMixin):
    _table_ = "scrobble"
    id = PrimaryKey(int, auto=True)
    song = Required("SongDb")
    album = Required("AlbumDb")
    title = Required(str)
    title_alt = Required(str)
    artist = Required(str)
    artist_alt = Required(str)
    album_name = Required(str)
    album_name_alt = Required(str)
    date = Required(datetime, volatile=True)
    composite_index(title, artist, album_name)

    def __str__(self):
        return f"ScrobbleDb[{self.id}]: {self.date} - {self.song}"


class SongDb(db.Entity, BaseMixin):
    _table_ = "song"
    id = PrimaryKey(int, auto=True)
    title = Required(str, index=True)
    title_alt = Required(str)
    length = Optional(int)
    scrobbles = Set(ScrobbleDb)
    files = Set("FileDb")
    albums = Set("AlbumDb")
    artists = Set("ArtistDb")
    tags = Set("TagDb")

    def __str__(self):
        return f"SongDb[{self.id}]: {self.title} - {', '.join([str(artist) for artist in self.artists])}"  # noqa


class FileDb(db.Entity, BaseMixin):
    _table_ = "file"
    id = PrimaryKey(int, auto=True)
    path = Required(str, index=True)
    song = Required("SongDb")
    title = Required(str)
    length = Required(int)
    artist = Required(str)
    album = Required(str)
    album_artist = Required(str)
    genre = Optional(str, nullable=True)
    vocals = Optional(str, nullable=True)
    series = Optional(str, nullable=True)
    franchise = Optional(str, nullable=True)
    op_ed = Optional(str, nullable=True)
    season = Optional(str, nullable=True)
    alternate = Optional(str, nullable=True)
    type = Optional(str, nullable=True)
    sort_artist = Optional(str, nullable=True)
    language = Optional(str, nullable=True)


class AlbumDb(db.Entity, BaseMixin):
    _table_ = "album"
    id = PrimaryKey(int, auto=True)
    name = Required(str, index=True)
    name_alt = Required(str)
    art = Optional(str)
    songs = Set(SongDb)
    scrobbles = Set(ScrobbleDb)
    album_artist = Optional("ArtistDb")

    def __str__(self):
        return f"AlbumDb[{self.id}]: {self.name} - {self.album_artist}"


class ArtistDb(db.Entity, BaseMixin):
    _table_ = "artist"
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    name_alt = Required(str)
    albums = Set(AlbumDb)
    songs = Set(SongDb)
    character_voice = Optional("ArtistDb", reverse="characters_voiced")
    characters_voiced = Set("ArtistDb", reverse="character_voice")

    def __str__(self):
        return f"ArtistDb[{self.id}]: {self.name}"


class TagDb(db.Entity, BaseMixin):
    _table_ = "tag"
    id = PrimaryKey(int, auto=True)
    tag_type = Required(str)
    value = Required(str)
    songs = Set(SongDb)
    composite_key(tag_type, value)

    def __str__(self):
        return f"TagDb[{self.id}]: {self.tag_type}:{self.value}"
