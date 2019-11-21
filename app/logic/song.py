from typing import List

from pony import orm

from app.db.models import SongDb
from app.logic import album as album_logic
from app.logic import artist as artist_logic
from app.logic import tag as tag_logic
from app.models.songs import SongIn


def add(song: SongIn) -> SongDb:
    return SongDb(
        title=song.title,
        length=song.length,
        tags=[
            tag_logic.add(tag.tag_type, tag.value, return_existing=True)
            for tag in song.tags
        ],
        albums=album_logic.add(
            name=song.album, artist=song.album_artist, return_existing=True
        ),
        artists=[
            artist_logic.add(artist, return_existing=True)
            for artist in artist_logic.split(song.artist)
        ],
    )


def get(title: str, artists: List[str]) -> SongDb:
    """Get song from database

    ## Arguments:
    - `title`: `str`:
        - Title of the song
    - `artists`: `List[str]`:
        - Artists of the song

    ## Returns:
    - `SongDb`:
        - The song, Returns `None` when no album is found
    """
    query = orm.select(s for s in SongDb if s.title == title)
    for artist in artists:
        query = query.filter(lambda s: artist in s.artists.name)
    query = query.filter(lambda s: orm.count(s.artists) == len(artists))
    return query.first()


def exists(title: str, artists: List[str]) -> bool:
    """Checks if a song exists in the database

    ## Arguments:
    - `title`: `str`:
        - Title of the song
    - `artists`: `List[str]`:
        - Artists of the song

    ## Returns:
    - `bool`:
        - `True` if song exists and `False` if it doesn't
    """
    song = get(title, artists)
    return True if song is not None else False
