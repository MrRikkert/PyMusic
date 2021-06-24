from datetime import datetime

from pony.orm import Optional, PrimaryKey, Required, Set, composite_key, composite_index

from app.db.base import db


class ScrobbleDb(db.Entity):
    def __init__(self):
        self.super().__init__()

    _table_ = "scrobble"
    id = PrimaryKey(int, auto=True)
    song = Required("SongDb")
    album = Required("AlbumDb")
    title = Required(str)
    artist = Required(str)
    album_name = Required(str)
    date = Required(datetime, volatile=True)
    composite_index(title, artist, album_name)

    def __str__(self):
        return f"ScrobbleDb[{self.id}]: {self.date} - {self.song}"


class SongDb(db.Entity):
    def __init__(self):
        self.super().__init__()

    _table_ = "song"
    id = PrimaryKey(int, auto=True)
    title = Required(str, index=True)
    title_alt = Required(str)
    length = Optional(int)
    scrobbles = Set(ScrobbleDb)
    albums = Set("AlbumDb")
    artists = Set("ArtistDb")
    tags = Set("TagDb")

    def __str__(self):
        return f"SongDb[{self.id}]: {self.title} - {', '.join([str(artist) for artist in self.artists])}"


class AlbumDb(db.Entity):
    def __init__(self):
        self.super().__init__()

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


class ArtistDb(db.Entity):
    def __init__(self):
        self.super().__init__()

    _table_ = "artist"
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    name_alt = Required(str)
    albums = Set(AlbumDb)
    songs = Set(SongDb)

    def __str__(self):
        return f"ArtistDb[{self.id}]: {self.name}"


class TagDb(db.Entity):
    def __init__(self):
        self.super().__init__()

    _table_ = "tag"
    id = PrimaryKey(int, auto=True)
    tag_type = Required(str)
    value = Required(str)
    songs = Set(SongDb)
    composite_key(tag_type, value)

    def __str__(self):
        return f"TagDb[{self.id}]: {self.tag_type}:{self.value}"
