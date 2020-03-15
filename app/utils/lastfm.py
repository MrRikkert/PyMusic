import pylast
from app.settings import LASTFMKEY, LASTFMSECRET

lastfm = pylast.LastFMNetwork(api_key=LASTFMKEY, api_secret=LASTFMSECRET)


def get_scrobbles(username: str):
    user: pylast.User = lastfm.get_user(username)
    return user.get_recent_tracks(limit=1)
