import os
import time
from datetime import datetime
from pathlib import Path

import click
from loguru import logger
from PIL import Image, UnidentifiedImageError

from shared.db.base import db
from shared.logic import file as file_logic
from shared.logic.album import get_album_art_hash
from shared.logic.file import get_library_files
from shared.settings import ALBUM_ART_PATH, MUSIC_PATH
from shared.utils.clean import clean_album


def __get_art_path(path) -> Path:
    base_path = Path(os.path.dirname(path))
    art_path = base_path / "Cover.jpg"
    if not os.path.exists(art_path):
        art_path = base_path / "cover.jpg"
    return Path(art_path)


def __get_new_art_path(album_hash, size) -> Path:
    # Strip extension
    album_hash = os.path.splitext(album_hash)[0]
    return Path(ALBUM_ART_PATH) / f"{album_hash}x{size}.png"


def __save_thumbnail(im, album_hash, size):
    im.thumbnail((size, size), Image.ANTIALIAS)
    new_art_path = __get_new_art_path(album_hash, size)
    new_art_path.parent.mkdir(parents=True, exist_ok=True)

    if new_art_path.exists():
        return
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(new_art_path, optimize=True, quality=85)


def get_albums():
    logger.info("Getting albums from musicbee")
    files = get_library_files()
    paths, albums = zip(
        *[(os.path.join(MUSIC_PATH, file.path), file.album) for file in files]
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
            album_hash = get_album_art_hash(album)
            art_path = __get_art_path(path)

            try:
                im = Image.open(art_path)
                for size in [512, 256, 128, 64]:
                    __save_thumbnail(im, album_hash, size)
            except FileNotFoundError:
                logger.bind(file=art_path).info("Cover not found")
            except UnidentifiedImageError:
                logger.bind(file=art_path).info("File can't be read")


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
