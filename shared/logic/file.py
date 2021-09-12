from typing import List, Union

from pony import orm
from shared.db.models import FileDb
from shared.logic import song as song_logic
from shared.logic import tag as tag_logic
from shared.models.songs import File, SongIn
from shared.models.tags import TagIn
from shared.settings import TAG_LIST


def add(file: File) -> FileDb:
    """Add the given file. Also tries to add the
    associated song to the database. If the file
    already exists it will update the given file.

    ## Arguments:
    - `file`: `File`:
        - The file you want to add

    ## Returns:
    - `FileDb`:
        - The created file object.
    """
    existing = get(file.path)

    if existing:
        return update(file, existing)

    file_db = FileDb(
        song=song_logic.add(
            SongIn(
                title=file.title,
                length=file.length,
                artist=file.artist,
                album=file.album,
                album_artist=file.album_artist,
                tags=get_tags(file),
            ),
            return_existing=True,
            update_existing=True,
        ),
        path=file.path,
        title=file.title,
        length=file.length,
        artist=file.artist,
        album=file.album,
        album_artist=file.album_artist,
    )
    for tag in TAG_LIST:
        file_db[tag] = file[tag]

    return file_db


def update(file: File, existing: FileDb) -> FileDb:
    """Updates an existing file object using the given new file object.
    Also updates the associated song.

    ## Arguments:
    - `file`: `File`:
        - The new file data
    - `existing`: `FileDb`:
        - The existing file object

    ## Returns:
    - `FileDb`:
        - Updated file object
    """
    file_tags = get_tags(file)
    existing_tags = get_tags(existing)

    new_tags = [tag for tag in file_tags if tag not in existing_tags]
    for tag in new_tags:
        existing[tag.tag_type] = tag.value

    if new_tags:
        existing.song = song_logic.add(
            SongIn(
                title=file.title,
                length=file.length,
                artist=file.artist,
                album=file.album,
                album_artist=file.album_artist,
                tags=get_tags(file),
            ),
            return_existing=True,
            update_existing=True,
        )

    return existing


def get_tags(file: Union[File, FileDb]) -> List[TagIn]:
    """Gets all tags from a `File` or `FileDb` object
    as `TagIn` objects

    ## Arguments:
    - `file`: `Union[File, FileDb]`:
        - The file of which you want the tags

    ## Returns:
    - `List[TagIn]`:
        - All the tags from the files as `TagIn` objects
    """
    tags = []

    for tag_type in TAG_LIST:
        tag_str = file[tag_type]
        if tag_str is not None:
            for tag in tag_str.split(";"):
                if tag:
                    tags.append(TagIn(tag_type=tag_type.strip(), value=tag.strip()))
    return tags


def get(path: str) -> FileDb:
    """Get file from the database based on the given path.

    ## Arguments:
    - `path`: `str`:
        - The path of the file

    ## Returns:
    - `FileDb`:
        - The file, returns `None` when no file is found
    """
    query = orm.select(f for f in FileDb if f.path == path)
    return query.first()


def exists(path: str) -> bool:
    """Checks if a file exists in the database

    ## Arguments:
    - `path`: `str`:
        - Path of the file

    ## Returns:
    - `bool`:
        - `True` if the file exists and `False` if it doesn't
    """
    file = get(path)
    return True if file is not None else False
