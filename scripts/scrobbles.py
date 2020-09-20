from app.logic import artist
from app.models.songs import ScrobbleIn
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


def import_scrobbles(path: str):
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        # skip header
        next(reader)
        for row in reader:
            scrobble.scrobble(
                ScrobbleIn(title=row[0], artist=row[1], album=row[2], date=row[3])
            )
