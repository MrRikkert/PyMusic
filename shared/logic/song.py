from typing import List

from pony import orm

from shared.db.models import FileDb, SongDb
from shared.exceptions import IntegrityError
from shared.logic import album as album_logic
from shared.logic import artist as artist_logic
from shared.logic import tag as tag_logic
from shared.models.songs import SongIn
from shared.utils.clean import clean_artist, reverse_artist
from shared.utils.file import get_tags


def add(
    song: SongIn,
    return_existing: bool = False,
    update_existing: bool = False,
    replace_existing_tags: bool = False,
) -> SongDb:
    """Add song to the database

    ## Arguments:
    - `song`: `SongIn`:
        - The song you want to add
    - `return_existing`: `bool`, optional:
        - Return existing database object when found or not. Defaults to `False`.
    - `update_existing`: `bool`, optional:
        - Update the existing song when found or not.
        Only updates the `albums` and `tags` properties
        `return_existing` also needs to be `True` for this to work.
        Defaults to `False`.
    - `replace_existing_tags`: `bool`, optional:
        - Remove all `tag` relationships from the song and the new ones.
        `update_existing` also need to be `True` for this to work.
        Defaults to `False`.

    ## Raises:
    - `IntegrityError`:
        - If the song already exists and `return_existing` is `False`

    ## Returns:
    - `SongDb`:
        - The created song, or existing song when `return_existing` is `true`
    """
    artists = artist_logic.split(song.artist)
    existing = get(title=song.title, artists=artists)

    if existing is not None:
        if not return_existing:
            raise IntegrityError("Song already exists")
        elif update_existing:
            existing = update(existing, song, replace_existing_tags)
        return existing
    return SongDb(
        title=song.title.lower(),
        title_alt=song.title,
        length=song.length,
        tags=[
            tag_logic.add(tag.tag_type, tag.value, return_existing=True)
            for tag in song.tags
        ],
        albums=album_logic.add(
            name=song.album, artist=song.album_artist, return_existing=True
        ),
        artists=[artist_logic.add(artist, return_existing=True) for artist in artists],
    )


def update(
    existing_song: SongDb, new_song: SongIn, replace_existing_tags: bool = False
) -> SongDb:
    """Update song in the database with new data.
    Only updates the `albums` and `tags` properties. Also updates
    the length property of it was still empty.

    ## Arguments:
    - `existing_song`: `SongDb`:
        - The existing song
    - `new_song`: `SongIn`:
        - The song with the new data
    - `replace_existing_tags`: `bool`, optional:
        - Remove all `tag` relationships from the song and replace the ones from `new_song`.
        Defaults to `False`.

    ## Returns:
    - `SongDb`:
        - _description_
    """
    existing_song.albums.add(
        album_logic.add(
            name=new_song.album,
            artist=new_song.album_artist,
            return_existing=True,
        )
    )

    if not existing_song.length and new_song.length:
        existing_song.length = new_song.length

    if replace_existing_tags:
        existing_song.tags.clear()
    for tag in new_song.tags:
        existing_song.tags.add(
            tag_logic.add(tag_type=tag.tag_type, value=tag.value, return_existing=True)
        )
    return existing_song


def update_from_files(song: SongDb) -> SongDb:
    """Updated the tags of the given songs using the tags
    of the connected files. This will also clear all
    current tags of the song.

    Nothing will happen if no files are found

    ## Arguments:
    - `song`: `SongDb`:
        - The song that needs to be updated

    ## Returns:
    - `SongDb`:
        - Given song with updated tags
    """
    files = orm.select(f for f in FileDb if f.song == song)

    if not files:
        return song

    song.tags.clear()
    for file in files:
        tags = get_tags(file)
        for tag in tags:
            song.tags.add(
                tag_logic.add(
                    tag_type=tag.tag_type, value=tag.value, return_existing=True
                )
            )
    return song


def get(title: str, artists: List[str]) -> SongDb:
    """Get song from database. Case insensitive

    ## Arguments:
    - `title`: `str`:
        - Title of the song
    - `artists`: `List[str]`:
        - Artists of the song

    ## Returns:
    - `SongDb`:
        - The song, Returns `None` when no album is found
    """
    query = orm.select(s for s in SongDb if s.title == title.lower())
    for artist in artists:
        _artist = clean_artist(artist).lower()
        query = query.filter(
            lambda s: _artist in s.artists.name
            or reverse_artist(_artist) in s.artists.name
        )
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
