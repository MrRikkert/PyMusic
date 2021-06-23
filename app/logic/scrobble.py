from datetime import datetime
from typing import Dict, List

import pytz
from app.db.models import ScrobbleDb
from app.models.songs import ScrobbleIn, SongIn
from app.utils import lastfm
from loguru import logger
from pony import orm


def scrobble(scrobble: ScrobbleIn) -> ScrobbleDb:
    """Add scrobbles to the database.
    uses the logic/song.add() method to add songs with
    `return_existing=True` and `update_existing=True`

    ## Arguments:
    - `scrobble`: `ScrobbleIn`:
        - The scrobble

    ## Returns:
    - `ScrobbleDb`:
        - The created scrobble
    """
    from app.logic import song as song_logic

    query = orm.select(s for s in ScrobbleDb)
    query = query.filter(lambda s: s.title == scrobble.title.lower())
    query = query.filter(lambda s: s.artist == scrobble.artist.lower())
    query = query.filter(lambda s: s.album == scrobble.album.lower())
    db_song = query.first()

    if db_song is None:
        song = song_logic.add(
            SongIn(**scrobble.dict()), return_existing=True, update_existing=True
        )
    else:
        song = db_song.song

    return ScrobbleDb(
        song=song,
        title=scrobble.title,
        artist=scrobble.artist,
        album=scrobble.album,
        date=scrobble.date,
    )


def get_last_scrobble() -> ScrobbleDb:
    query = orm.select(s for s in ScrobbleDb)
    query = query.order_by(orm.desc(ScrobbleDb.date))
    return query.first()


def sync_lastfm_scrobbles(username: str):
    """Sync the user's LastFm scrobbles with the database.
    It will get all scrobbles if the user has never synced before.
    If the user has synced before, it will sync everything since the last sync.

    ## Arguments:
    - `username`: `str`:
        - The user's LastFm username

    ## Returns:
    - `int`:
        - The amount of scrobbles synced
    """
    last_scrobble = get_last_scrobble()
    last_date = 0
    if last_scrobble:
        # Make timestamp timezone aware. All timestamps are stored as UTC,
        # but python interprets all datetimes without timezones as local.
        # So when making a timestamp it first converts the datetime to UTC,
        # even though it was alreadu UTC.
        last_date = pytz.utc.localize(last_scrobble.date)
        last_date = int(last_date.timestamp())
    scrobbles = lastfm.get_scrobbles(
        username=username,
        limit=None,
        # +60 seconds to exclude the last scrobble from lastfm
        time_from=last_date + 60 if last_date is not None else None,
    )
    for _scrobble in scrobbles:
        timestamp = _scrobble.timestamp  # + timedelta(hours=1)
        try:
            scrobble(
                scrobble=ScrobbleIn(
                    date=timestamp,
                    artist=_scrobble.track.artist.name.lower(),
                    album=_scrobble.album.lower(),
                    title=_scrobble.track.title.lower(),
                )
            )
        except Exception as e:
            logger.exception(
                f"Something went wrong while adding a scrobble with data: {_scrobble.dict()}"
            )
            pass
    return len(scrobbles)


def recent_plays(
    min_date: datetime = None, max_date: datetime = None
) -> List[ScrobbleDb]:
    """Get recent plays from the given user in a given timeframe

    ## Arguments:
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
    if min_date is not None:
        query = query.filter(lambda scrobble: scrobble.date >= min_date)
    if max_date is not None:
        query = query.filter(lambda scrobble: scrobble.date <= max_date)
    query = query.order_by(orm.desc(ScrobbleDb.date))
    return query


def most_played_songs(
    page: int = 0,
    page_size: int = 10,
    min_date: datetime = None,
    max_date: datetime = None,
) -> List[Dict]:
    """Get the most played songs of a user in a given time frame

    ## Arguments:
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
    if min_date is not None:
        query = query.where(lambda scrobble: scrobble.date >= min_date)
    if max_date is not None:
        query = query.where(lambda scrobble: scrobble.date <= max_date)
    songs = list(query.page(page, page_size))
    return [{"song": song, "plays": plays} for song, plays in songs]
