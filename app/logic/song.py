from app.db.models import SongDb
from app.logic import album as album_logic
from app.logic import artist as artist_logic
from app.logic import tag as tag_logic
from app.models.songs import SongIn


def add_song(song: SongIn) -> SongDb:
    return SongDb(
        title=song.title,
        length=song.length,
        tags=[
            tag_logic.add_tag(tag.tag_type, tag.value, return_existing=True)
            for tag in song.tags
        ],
        albums=album_logic.add_album(
            name=song.album, artist=song.album_artist, return_existing=True
        ),
        artists=[
            artist_logic.add_artist(artist, return_existing=True)
            for artist in artist_logic.split_artist(song.artist)
        ],
    )
