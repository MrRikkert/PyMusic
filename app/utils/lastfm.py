from typing import List

import pylast
from app.exceptions import LastFmError
from app.models.songs import ScrobbleLastFm
from app.settings import LASTFMKEY, LASTFMSECRET
from loguru import logger

lastfm = pylast.LastFMNetwork(api_key=LASTFMKEY, api_secret=LASTFMSECRET)


def get_scrobbles(
    username: str, limit: int = None, time_from: str = None, time_to: str = None
) -> List[ScrobbleLastFm]:
    """Get all scrobbles from the given LastFM user within the search criteria

    ## Arguments:
    - `username`: `str`:
        - Name of the LastFM user
    - `limit`: `int`, optional:
        - Limit the max amount of scrobbles to get.
        When `None` gets every scrobble within criteria.Defaults to `None`.
    - `time_from`: `str`, optional:
        - Get scrobbles from now up until this date.
        Includes scrobble on the exact date. Defaults to `None`.
    - `time_to`: `str`, optional:
        - Get scrobbles from the given date and below.
        Does not include scrobble on the exact date. Defaults to `None`.

    ## Raises:
    - `ValueError`:
        - Raised when the given user is not a valid username
    - `LastFmError`:
        - Raised when the given user does not exist

    ## Returns:
    - `ScrobbleLastFm`:
        - A Scrobble model with all the information LastFM returns
    """
    if not username:
        raise ValueError("Username is required")

    try:
        user: pylast.User = lastfm.get_user(username)
    except pylast.PyLastError:
        logger.exception("User not found")
        raise LastFmError("User not found")
    scrobbles = user.get_recent_tracks(
        limit=limit, time_from=time_from, time_to=time_to
    )
    return [ScrobbleLastFm.from_orm(scrobble) for scrobble in scrobbles]
