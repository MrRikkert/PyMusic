import csv
import os
import time
from datetime import datetime
from pathlib import Path

import click
import pytz
from loguru import logger

from shared.db.base import db
from shared.logic import scrobble
from shared.models.songs import ScrobbleIn


def sync_lastfm_scrobbles(username: str):
    scrobble.sync_lastfm_scrobbles(username)


def export_scrobbles(path: str):
    scrobbles = scrobble.recent_plays()
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, delimiter=",", fieldnames=["title", "artist", "album", "date"]
        )
        writer.writeheader()
        for _scrobble in scrobbles:
            date = int(pytz.utc.localize(_scrobble.date).timestamp())
            flat_scrobble = {
                "title": _scrobble.title_alt,
                "artist": _scrobble.artist_alt,
                "album": _scrobble.album_name_alt,
                "date": date,
            }
            writer.writerow(flat_scrobble)


def import_scrobbles(path: str):
    start = time.time()
    print(datetime.now().time())
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
                except Exception:
                    logger.bind(
                        scrobble=f"title={row[0]}, artist={row[1]}, album={row[2]}, date={row[3]}"
                    ).exception("Something went wrong while adding a scrobble")
                if idx % 500 == 0:
                    db.commit()
    print(time.time() - start)
