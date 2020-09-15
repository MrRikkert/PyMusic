from pony.orm import db_session

import musicbeeipc
from app import settings
from app.db.base import db
from app.logic import song as song_logic
from app.models.songs import SongIn
from app.models.tags import TagIn

mbipc = musicbeeipc.MusicBeeIPC()
tag_types = {
    "genre": musicbeeipc.MBMD_Genre,
    "vocals?": musicbeeipc.MBMD_Custom1,
    "subseries": musicbeeipc.MBMD_Custom2,
    "series": musicbeeipc.MBMD_Custom3,
    "op_ed": musicbeeipc.MBMD_Custom4,
    "season": musicbeeipc.MBMD_Custom5,
    "alternate": musicbeeipc.MBMD_Custom6,
    "type": musicbeeipc.MBMD_Custom7,
    "sort_artist": musicbeeipc.MBMD_Custom8,
}


def get_paths():
    return mbipc.library_search(query="")


def mb_duration_to_seconds(duration: str) -> int:
    return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(duration.split(":"))))


def get_tags(path):
    tags = []
    for tag_type in tag_types:
        tags_str = mbipc.library_get_file_tag(path, tag_types[tag_type])
        for tag in tags_str.split(";"):
            if tag:
                tags.append(TagIn(tag_type=tag_type, value=tag))
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


if __name__ == "__main__":
    db.bind(**settings.DB_PARAMS)
    db.generate_mapping(create_tables=True)

    paths = get_paths()
    total = len(paths)

    with db_session:
        for idx, path in enumerate(paths):
            song = get_song(path)
            try:
                song_logic.add(song, return_existing=True, update_existing=True)
            except:
                print(song)
            print(f"{idx + 1}/{total}")
