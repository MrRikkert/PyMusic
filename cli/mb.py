import base64
import os
import time
from datetime import datetime
from hashlib import md5

import click
from loguru import logger

from shared.db.base import db
from shared.logic import file as file_logic
from shared.logic.file import get_library_files
from shared.settings import ALBUM_ART_PATH

# Can only be used on windows
try:
    from cli import musicbeeipc

    mbipc = musicbeeipc.MusicBeeIPC()
except ImportError:
    from cli.musicbeeipc_mock import Mock

    # Mock class that raises an exception on usage
    mbipc = Mock()

tag_types = {
    "genre": musicbeeipc.MBMD_Genre,
    "vocals": musicbeeipc.MBMD_Custom1,
    "series": musicbeeipc.MBMD_Custom2,
    "franchise": musicbeeipc.MBMD_Custom3,
    "op_ed": musicbeeipc.MBMD_Custom4,
    "season": musicbeeipc.MBMD_Custom5,
    "alternate": musicbeeipc.MBMD_Custom6,
    "type": musicbeeipc.MBMD_Custom7,
    "sort_artist": musicbeeipc.MBMD_Custom8,
    "language": musicbeeipc.MBMD_Custom9,
}


def get_paths(query: str = "", fields=["ArtistPeople", "Title", "Album"]):
    return mbipc.library_search(query=query, fields=fields)


def get_albums():
    logger.info("Getting albums from musicbee")
    paths = get_paths()
    albums = [
        mbipc.library_get_file_tag(path, musicbeeipc.MBMD_Album).lower()
        for path in paths
    ]
    _albums = []
    _paths = []

    logger.info("Filtering albums")
    for path, album in zip(paths, albums):
        if album not in _albums:
            _albums.append(album)
            _paths.append(path)

    with click.progressbar(zip(_paths, _albums), length=len(_albums)) as click_iter:
        for path, album in click_iter:
            save_album_art(album, path)


def save_album_art(album: str, path: str):
    album_hash = md5(album.lower().encode("utf-8")).hexdigest()
    art_path = os.path.join(ALBUM_ART_PATH, album_hash[0:2], album_hash + ".png")

    if not os.path.exists(art_path):
        art = mbipc.library_get_artwork(path, 0)
        os.makedirs(os.path.dirname(art_path), exist_ok=True)
        with open(art_path, "wb") as fh:
            fh.write(base64.decodebytes(str.encode(art)))


def sync_data(
    replace_existing: bool = False,
    query: str = "",
    fields=["ArtistPeople", "Title", "Album"],
):
    start = time.time()
    print(datetime.now().time())
    files = get_library_files()

    with click.progressbar(files) as click_files:
        for idx, file in enumerate(click_files):
            try:
                file_logic.add(file)
            except Exception:
                logger.bind(song=file.dict()).exception(
                    "Something went wrong while adding a song"
                )
            if idx % 500 == 0:
                db.commit()
    print(time.time() - start)
