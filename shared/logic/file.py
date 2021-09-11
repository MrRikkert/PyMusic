from shared.models.tags import TagIn
from pony import orm

from shared.db.models import FileDb
from shared.models.songs import File, SongIn
from shared.logic import song as song_logic


def add(file: File) -> FileDb:
    existing = get(file.path)

    if existing:
        return update(file)

    return FileDb(
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
        genre=file.genre,
        vocals=file.vocals,
        series=file.series,
        franchise=file.franchise,
        op_ed=file.op_ed,
        season=file.season,
        alternate=file.alternate,
        type=file.type,
        sort_artist=file.sort_artist,
        language=file.language,
    )


def update(file) -> FileDb:
    raise NotImplementedError


def get_tags(file: File):
    tag_list = [
        "genre",
        "vocals",
        "series",
        "franchise",
        "op_ed",
        "season",
        "alternate",
        "type",
        "sort_artist",
        "language",
    ]
    tags = []

    for tag_type in tag_list:
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
