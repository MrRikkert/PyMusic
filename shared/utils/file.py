import os

from shared.settings import MUSIC_PATH


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
    return os.path.relpath(path, rel_path)
