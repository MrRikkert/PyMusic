import click
import musicbeeipc
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
        artist=mbipc.library_get_file_tag(path, musicbeeipc.MBMD_Artists),
        tags=get_tags(path),
    )


def sync_data(
    print_progress: bool = False,
    replace_existing: bool = False,
    query: str = "",
    fields=["ArtistPeople", "Title", "Album"],
):
    paths = get_paths(query=query, fields=fields)

    with click.progressbar(paths) as click_paths:
        for path in click_paths:
            song = get_song(path)
            try:
                song_logic.add(
                    song,
                    return_existing=True,
                    update_existing=True,
                    replace_existing_tags=replace_existing,
                )
            except Exception as ex:
                print(ex)
                print(f"{song.title} - {song.artist}")
