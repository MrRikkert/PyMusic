from app.db.models import SongDb, TagDb, AlbumDb, ArtistDb
from app.models.songs import SongIn
from app.logic import artist as artist_logic


def add_song(song: SongIn) -> SongDb:
    return SongDb(
        title=song.title,
        length=song.length,
        tags=[TagDb(tag_type=tag.tag_type, value=tag.value) for tag in song.tags],
        albums=AlbumDb(name=song.album, album_artist=ArtistDb(name=song.album_artist)),
        artists=[
            artist_logic.add_artist(artist, return_existing=True)
            for artist in artist_logic.split_artist(song.artist)
        ],
    )
