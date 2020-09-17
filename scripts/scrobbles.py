from app.logic import scrobble


def sync_lastfm_scrobbles(username: str):
    scrobble.sync_lastfm_scrobbles(username)
