from typing import Union

from pony import orm
from shared.db.models import FileDb
from shared.logic import song as song_logic
from shared.logic import tag as tag_logic
from shared.models.songs import File, SongIn
from shared.models.tags import TagIn
from shared.settings import TAG_LIST


def add(file: File) -> FileDb:
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


def get_tags(file: Union[File, FileDb]):
    tags = []

    for tag_type in TAG_LIST:
        tag_str = file[tag_type]
        if tag_str is not None:
            for tag in tag_str.split(";"):
                if tag:
                    tags.append(TagIn(tag_type=tag_type.strip(), value=tag.strip()))
    return tags


def get(path: str) -> FileDb:
    query = orm.select(f for f in FileDb if f.path == path)
    return query.first()


def exists(path: str) -> bool:
    file = get(path)
    return True if file is not None else False
