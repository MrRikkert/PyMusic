from app.db.models import AlbumDb, ArtistDb, SongDb, TagDb
from app.logic import album as album_logic
from app.logic import artist as artist_logic
from app.models.songs import SongIn


def add_song(song: SongIn) -> SongDb:
    return SongDb(
        title=song.title,
        length=song.length,
        tags=[TagDb(tag_type=tag.tag_type, value=tag.value) for tag in song.tags],
        albums=album_logic.add_album(
            name=song.album, artist=song.album_artist, return_existing=True
        ),
        artists=[
            artist_logic.add_artist(artist, return_existing=True)
            for artist in artist_logic.split_artist(song.artist)
        ],
    )
