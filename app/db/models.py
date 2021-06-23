from datetime import datetime

from pony.orm import Optional, PrimaryKey, Required, Set, composite_key

from app.db.base import db


class ScrobbleDb(db.Entity):
    _table_ = "scrobble"
    id = PrimaryKey(int, auto=True)
    song = Required("SongDb")
    title = Required(str)
    artist = Required(str)
    album = Required(str)
    date = Required(datetime, volatile=True)
    composite_key(title, artist, album)


class SongDb(db.Entity):
    _table_ = "song"
    id = PrimaryKey(int, auto=True)
    title = Required(str, index=True)
    title_alt = Required(str)
    length = Optional(int)
    scrobbles = Set(ScrobbleDb)
    albums = Set("AlbumDb")
    artists = Set("ArtistDb")
    tags = Set("TagDb")


class AlbumDb(db.Entity):
    _table_ = "album"
    id = PrimaryKey(int, auto=True)
    name = Required(str, index=True)
    name_alt = Required(str)
    art = Optional(str)
    songs = Set(SongDb)
    album_artist = Optional("ArtistDb")


class ArtistDb(db.Entity):
    _table_ = "artist"
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    name_alt = Required(str)
    albums = Set(AlbumDb)
    songs = Set(SongDb)


class TagDb(db.Entity):
    _table_ = "tag"
    id = PrimaryKey(int, auto=True)
    tag_type = Required(str)
    value = Required(str)
    songs = Set(SongDb)
    composite_key(tag_type, value)
