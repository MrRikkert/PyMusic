from app.db.models import ArtistDb


def add_artist(name: str) -> ArtistDb:
    return ArtistDb(name=name)


def get_existing_artist(name: str) -> ArtistDb:
    return ArtistDb.get(name=name)


def get_or_add_artist(name: str) -> ArtistDb:
    """Returns existing artist if it exists, else it creates a new artist and returns that"""
    db_artist = get_existing_artist(name)
    return db_artist if db_artist is not None else add_artist(name)
