from typing import Dict, List

from pony import orm

from app.db.models import ScrobbleDb, SongDb, UserDb
from app.exceptions import IntegrityError
from app.models.songs import ScrobbleIn, SongIn
from app.models.users import RegisterIn
from app.utils.security import hash_password, verify_password


def register(register: RegisterIn) -> UserDb:
    """Register a user by adding him/her to the database.
    Also hashes the password.

    ## Arguments:
    - `register`: `RegisterIn`:
        - De user you want to register

    ## Raises:
    - `IntegrityError`:
        - Raised when the username and/or email already exists

    ## Returns:
    - `UserDb`:
        - The created user
    """
    register = register.copy(deep=True)
    register.password = hash_password(register.password)
    if exists(register.username):
        raise IntegrityError("Username already exists")
    return UserDb(**register.dict())


def exists(username: str) -> bool:
    """Check if the user already exists in the database

    ## Arguments:
    - `username`: `str`:
        - Name of the user

    ## Returns:
    - `bool`:
        - `True` when user exists, `False` when it doesn't
    """
    user = get(username)
    if user is None:
        return False
    return True


def get(username: str) -> UserDb:
    """Get user from database

    ## Arguments:
    - `username`: `str`:
        - Name of the user

    ## Returns:
    - `UserDb`:
        - The found user. Returns `None` when no user is found
    """
    return UserDb.get(username=username)


def authenticate(username: str, password: str) -> UserDb:
    """Validat user credentials

    ## Arguments:
    - `username`: `str`:
        - Name of the user
    - `password`: `str`:
        - Password of the user (non hashed)

    ## Returns:
    - `UserDb`:
        - Return the user if the credentials are correct.
        Returns `None` if the credentials are wrong.
    """
    user = get(username)
    if user is not None:
        if not verify_password(password, user.password):
            return None
    return user


def scrobble(user: UserDb, scrobble: ScrobbleIn) -> ScrobbleDb:
    """Scrobble music to the given user.
    uses the logic/song.add() method to add songs with
    `return_existing=True` and `update_existing=True`

    ## Arguments:
    - `user`: `UserDb`:
        - User that is scrobbled the song
    - `scrobble`: `ScrobbleIn`:
        - The scrobble

    ## Returns:
    - `ScrobbleDb`:
        - The created scrobble
    """
    from app.logic import song as song_logic

    return ScrobbleDb(
        user=user,
        song=song_logic.add(
            SongIn(**scrobble.dict()), return_existing=True, update_existing=True
        ),
        title=scrobble.title,
        artist=scrobble.artist,
        album=scrobble.album,
        album_artist=scrobble.album_artist,
        date=scrobble.date,
    )


def recent_plays(user: UserDb, page: int = 0, page_size: int = 10) -> List[ScrobbleDb]:
    """Get recent plays from the given user

    ## Arguments:
    - `user`: `UserDb`:
        - User you want the recent plays from
    - `page`: `int`, optional:
        - Page of plays you want. Defaults to `0`.
    - `page_size`: `int`, optional:
        - The size of pages you want to select. Defaults to `10`.

    ## Returns:
    - `List[ScrobbleDb]`:
        - List of scrobbles ordered be descending date
    """
    query = orm.select(s for s in ScrobbleDb)
    query = query.filter(lambda scrobble: scrobble.user == user)
    query = query.order_by(orm.desc(ScrobbleDb.date))
    return list(query.page(page, page_size))


def top_plays_song(
    user: UserDb, page: int = 0, page_size: int = 10
) -> List[Dict[str, SongDb]]:
    query = orm.select(
        (scrobble.song, orm.count(scrobble.song.scrobbles)) for scrobble in ScrobbleDb
    )
    query = query.order_by(lambda song, count: orm.desc(orm.count(song.scrobbles)))
    query = query.where(lambda scrobble: scrobble.user == user)
    songs = list(query.page(page, page_size))
    return [{"song": song, "plays": plays} for song, plays in songs]
