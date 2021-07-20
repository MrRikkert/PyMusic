import base64
import os
import pickle
import time
from datetime import datetime
from hashlib import md5
from pathlib import Path

import click
from loguru import logger
from shared.db.base import db
from shared.logic import song as song_logic
from shared.models.songs import SongIn
from shared.models.tags import TagIn
from shared.settings import ALBUM_ART_PATH

from cli import musicbeeipc

mbipc = musicbeeipc.MusicBeeIPC()
tag_types = {
    "genre": musicbeeipc.MBMD_Genre,
    "vocals?": musicbeeipc.MBMD_Custom1,
    "series": musicbeeipc.MBMD_Custom2,
    "franchise": musicbeeipc.MBMD_Custom3,
    "op_ed": musicbeeipc.MBMD_Custom4,
    "season": musicbeeipc.MBMD_Custom5,
    "alternate": musicbeeipc.MBMD_Custom6,
    "type": musicbeeipc.MBMD_Custom7,
    "sort_artist": musicbeeipc.MBMD_Custom8,
}


def get_paths(query: str = "", fields=["ArtistPeople", "Title", "Album"]):
    return mbipc.library_search(query=query, fields=fields)


def mb_duration_to_seconds(duration: str) -> int:
    return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(duration.split(":"))))


def get_tags(path):
    tags = []
    for tag_type in tag_types:
        tags_str = mbipc.library_get_file_tag(path, tag_types[tag_type])
        for tag in tags_str.split(";"):
            if tag:
                tags.append(TagIn(tag_type=tag_type.strip(), value=tag.strip()))
    return tags


def get_song(path: str) -> SongIn:
    album_artist = mbipc.library_get_file_tag(path, musicbeeipc.MBMD_AlbumArtistRaw)

    return SongIn(
        title=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_TrackTitle),
        length=mb_duration_to_seconds(
            mbipc.library_get_file_property(path, musicbeeipc.MBFP_Duration)
        ),
        album=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_Album),
        album_artist=None if not album_artist else album_artist,
        artist=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_Artist),
        tags=get_tags(path),
    )


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
        if not album in _albums:
            _albums.append(album)
            _paths.append(path)

    with click.progressbar(zip(_paths, _albums), length=len(_albums)) as click_iter:
        for path, album in click_iter:
            save_album_art(album, path)


def save_album_art(album: str, path: str):
    album_hash = md5(album.lower().encode("utf-8")).hexdigest()
    art_path = os.path.join(ALBUM_ART_PATH, album_hash[0:2], album_hash + ".png")
    art = mbipc.library_get_artwork(path, 0)

    if not os.path.exists(art_path):
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
    paths = get_paths(query=query, fields=fields)

    with click.progressbar(paths) as click_paths:
        for idx, path in enumerate(click_paths):
            song = get_song(path)
            try:
                song_logic.add(
                    song,
                    return_existing=True,
                    update_existing=True,
                    replace_existing_tags=replace_existing,
                )
            except Exception as ex:
                logger.bind(song=song.dict()).exception(
                    f"Something went wrong while adding a song"
                )
            if idx % 500 == 0:
                db.commit()
    print(time.time() - start)


def export_data(
    export_path, query: str = "", fields=["ArtistPeople", "Title", "Album"]
):
    Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
    paths = get_paths(query=query, fields=fields)
    songs = []
    with click.progressbar(paths) as click_paths:
        for idx, path in enumerate(click_paths):
            songs.append(get_song(path))

    with open(export_path, "wb") as file:
        pickle.dump(songs, file)


def import_data(replace_existing, export_path):
    with open(export_path, "rb") as file:
        songs = pickle.load(file)
    with click.progressbar(songs) as click_songs:
        for idx, song in enumerate(click_songs):
            try:
                song_logic.add(
                    song,
                    return_existing=True,
                    update_existing=True,
                    replace_existing_tags=replace_existing,
                )
            except Exception as ex:
                logger.bind(song=song.dict()).exception(
                    f"Something went wrong while adding a song"
                )
            if idx % 500 == 0:
                db.commit()
