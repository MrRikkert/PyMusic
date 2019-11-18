from datetime import datetime

from pony.orm import Optional, PrimaryKey, Required, Set

from app.db.base import db


class UserDb(db.Entity):
    _table_ = "user"
    id = PrimaryKey(int, auto=True)
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    password = Required(str)
    scrobbles = Set("ScrobbleDb")


class ScrobbleDb(db.Entity):
    _table_ = "scrobble"
    id = PrimaryKey(int, auto=True)
    user = Required(UserDb)
    song = Required("SongDb")
    title = Required(str)
    artist = Required(str)
    album = Required(str)
    date = Required(datetime)


class SongDb(db.Entity):
    _table_ = "song"
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    length = Optional(int)
    scrobbles = Set(ScrobbleDb)
    tags = Set("TagDb")
    albums = Set("AlbumDb")
    artists = Set("ArtistDb")


class AlbumDb(db.Entity):
    _table_ = "album"
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    songs = Set(SongDb)
    album_artist = Optional("ArtistDb")


class ArtistDb(db.Entity):
    _table_ = "artist"
    id = PrimaryKey(int, auto=True)
    Name = Required(str, unique=True)
    albums = Set(AlbumDb)
    songs = Set(SongDb)


class TagDb(db.Entity):
    _table_ = "tag"
    song = Required(SongDb)
    tag_type = Required(str)
    value = Required(str)
    PrimaryKey(song, tag_type, value)
