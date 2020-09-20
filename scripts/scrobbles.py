import csv

import pytz

from app.logic import scrobble


def sync_lastfm_scrobbles(username: str):
    scrobble.sync_lastfm_scrobbles(username)


def export_scrobbles(path: str):
    scrobbles = scrobble.recent_plays()
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, delimiter=",", fieldnames=["title", "artist", "album", "date"]
        )
        writer.writeheader()
        for _scrobble in scrobbles:
            date = int(pytz.utc.localize(_scrobble.date).timestamp())
            flat_scrobble = {
                "title": _scrobble.title,
                "artist": _scrobble.artist,
                "album": _scrobble.album,
                "date": date,
            }
            writer.writerow(flat_scrobble)
