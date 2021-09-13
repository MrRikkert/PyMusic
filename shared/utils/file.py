import os

from shared.settings import MUSIC_PATH


def get_normalized_path(path, rel_path=None):
    if not rel_path:
        rel_path = MUSIC_PATH
    return os.path.relpath(path, rel_path)
