from datetime import datetime
from typing import Dict, List

from email_validator import EmailNotValidError, validate_email
from pony import orm

from app.db.models import ScrobbleDb, UserDb
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
    if username_exists(register.username):
        raise IntegrityError("Username already exists")
    if email_exists(register.email):
        raise IntegrityError("Email already exists")
    return UserDb(**register.dict())


def username_exists(username: str) -> bool:
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


def email_exists(email: str) -> bool:
    user = get(email)
    if user is None:
        return False
    return True


def get(value: str) -> UserDb:
    """Get user from database

    ## Arguments:
    - `value`: `str`:
        - Name or email of the user, checks for email using the email-validator library

    ## Returns:
    - `UserDb`:
        - The found user. Returns `None` when no user is found
    """
    try:
        # deliverability is already checked by pydantic
        validate_email(value, check_deliverability=False)
        return UserDb.get(email=value)
    except EmailNotValidError:
        return UserDb.get(username=value)


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


def recent_plays(
    user: UserDb,
    page: int = 0,
    page_size: int = 10,
    min_date: datetime = None,
    max_date: datetime = None,
) -> List[ScrobbleDb]:
    """Get recent plays from the given user in a given timeframe

    ## Arguments:
    - `user`: `UserDb`:
        - User you want the recent plays from
    - `page`: `int`, optional:
        - Page of plays you want. Defaults to `0`.
    - `page_size`: `int`, optional:
        - The size of pages you want to select. Defaults to `10`.
    - `min_date`: `datetime`, optional:
        - The minimal date from which scrobbles should be fetched
        `None` gets data from the beginning. Defaults to `None`
    - `max_date`: `datetime`, optional:
        - The maximum date from which scrobbles should be fetched
        `None` gets data until the end. Defaults to `None`

    ## Returns:
    - `List[ScrobbleDb]`:
        - List of scrobbles ordered by descending date
    """
    query = orm.select(s for s in ScrobbleDb)
    query = query.filter(lambda scrobble: scrobble.user == user)
    if min_date is not None:
        query = query.filter(lambda scrobble: scrobble.date >= min_date)
    if max_date is not None:
        query = query.filter(lambda scrobble: scrobble.date <= max_date)
    query = query.order_by(orm.desc(ScrobbleDb.date))
    return list(query.page(page, page_size))


def most_played_songs(
    user: UserDb,
    page: int = 0,
    page_size: int = 10,
    min_date: datetime = None,
    max_date: datetime = None,
) -> List[Dict]:
    """Get the most played songs of a user in a given time frame

    ## Arguments:
    - `user`: `UserDb`:
        - User you want to get the top played songs from
    - `page`: `int`, optional:
        - Defaults to `0`.
    - `page_size`: `int`, optional:
        - The size of the pages you want to select. Defaults to `10`.
    - `min_date`: `datetime`, optional:
        - The start of data to aggregate.
        `None` gets data from the beginning. Defaults to `None`
    - `max_date`: `datetime`, optional:
        - The end of data to aggregate
        `None` gets data until the end. Defaults to `None`

    ## Returns:
    - `List[Dict]`:
        - The list of scrobbles ordered by descending plays.
        The dict has two keys: `song` of type `SongDb` and
        `plays` of type `int`
    """
    query = orm.select((scrobble.song, orm.count(scrobble)) for scrobble in ScrobbleDb)
    query = query.order_by(lambda song, count: orm.desc(count))
    query = query.where(lambda scrobble: scrobble.user == user)
    if min_date is not None:
        query = query.where(lambda scrobble: scrobble.date >= min_date)
    if max_date is not None:
        query = query.where(lambda scrobble: scrobble.date <= max_date)
    songs = list(query.page(page, page_size))
    return [{"song": song, "plays": plays} for song, plays in songs]
