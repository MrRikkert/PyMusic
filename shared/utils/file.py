import pathlib
from typing import List, Union

from shared.db.models import FileDb
from shared.models.songs import File
from shared.models.tags import TagIn
from shared.settings import MUSIC_PATH, TAG_LIST


def get_normalized_path(path: str, rel_path: str = None) -> str:
    """Normalizes a given path by the given `rel_path`.
    If `rel_path` is not given the env variable will be used.

    example:
    - `path="C:\\users\\johndoe\\music\\Supercell\\My Dearest\\3 - Dai Hinmin.flac"`
    - `rel_path="C:\\users\\johndoe\\music"`

    returns: `"Supercell\\My Dearest\\3 - Dai Hinmin.flac"`

    ## Arguments:
    - `path`: `str`:
        - Path to be normalized
    - `rel_path`: `str`, optional:
        - The relative path where the music is stored.
        when `None` will use the env variables. Defaults to `None`.

    ## Returns:
    - `str`:
        - The normalized path
    """
    if not rel_path:
        rel_path = MUSIC_PATH

    return str(pathlib.PurePosixPath(pathlib.Path(path).relative_to(rel_path)))


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
