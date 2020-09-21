import csv
import logging
import time

import click
import pytz

from app.db.base import db
from app.logic import scrobble
from app.models.songs import ScrobbleIn


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
    start = time.time()
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        rows = sum(1 for row in reader)

    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        # skip header
        print(rows)
        next(reader)
        with click.progressbar(reader, length=rows) as click_paths:
            for idx, row in enumerate(click_paths):
                try:
                    scrobble.scrobble(
                        ScrobbleIn(
                            title=row[0], artist=row[1], album=row[2], date=row[3]
                        )
                    )
                except:
                    logging.error(f"IMPORT: {row[1]} - {row[0]}")
                if idx % 500 == 0:
                    db.commit()
    print(time.time() - start)
