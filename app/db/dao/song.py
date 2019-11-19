from app.db.dao import artist as artist_dao
from app.db.models import AlbumDb, ArtistDb, SongDb, TagDb
from app.models.songs import Song


def add_song(song: Song) -> SongDb:
    return SongDb(
        title=song.title,
        length=song.length,
        tags=[TagDb(tag_type=tag.tag_type, value=tag.value) for tag in song.tags],
        albums=AlbumDb(name=song.album, album_artist=ArtistDb(name=song.album_artist)),
        artists=[artist_dao.get_or_add_artist(artist) for artist in song.artists],
    )
