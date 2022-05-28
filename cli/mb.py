import os
import time
from datetime import datetime
from hashlib import md5
from shutil import copy

import click
from loguru import logger

from shared.db.base import db
from shared.logic import file as file_logic
from shared.logic.file import get_library_files
from shared.settings import ALBUM_ART_PATH, MUSIC_PATH
from shared.utils.clean import clean_album


def get_albums():
    logger.info("Getting albums from musicbee")
    files = get_library_files()
    paths, albums = zip(
        *[
            (os.path.join(os.path.split(MUSIC_PATH)[0], file.path), file.album)
            for file in files
        ]
    )
    _albums = []
    _paths = []

    logger.info("Filtering albums")
    for path, album in zip(paths, albums):
        album = clean_album(album)
        if album not in _albums:
            _albums.append(album)
            _paths.append(path)

    return _albums, _paths


def save_album_art():
    albums, paths = get_albums()
    with click.progressbar(length=len(albums)) as bar:
        for album, path in zip(albums, paths):
            bar.update(1)
            album_hash = md5(album.lower().encode("utf-8")).hexdigest()
            art_path = os.path.join(os.path.dirname(path), "Cover.jpg")
            new_art_path = os.path.join(
                ALBUM_ART_PATH, album_hash[0:2], album_hash + ".png"
            )

            if not os.path.exists(art_path) or os.path.exists(new_art_path):
                continue

            copy(art_path, new_art_path)


def sync_data():
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
