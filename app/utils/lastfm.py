import pylast

from app.exceptions import LastFmError
from app.settings import LASTFMKEY, LASTFMSECRET

lastfm = pylast.LastFMNetwork(api_key=LASTFMKEY, api_secret=LASTFMSECRET)


def get_scrobbles(
    username: str, limit: int = None, time_from: str = None, time_to: str = None
):
    if not username:
        raise ValueError("Username is required")

    try:
        user: pylast.User = lastfm.get_user(username)
    except pylast.WSError:
        raise LastFmError("User not found")
    return user.get_recent_tracks(limit=limit, time_from=time_from, time_to=time_to)
