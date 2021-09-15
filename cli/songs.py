import time
from datetime import datetime

import click
from loguru import logger
from pony import orm

from shared.db.models import SongDb
from shared.logic import song as song_logic


def reset_all_tags():
    start = time.time()
    print(datetime.now().time())
    with click.progressbar(list(orm.select(s for s in SongDb))) as songs:
        for song in songs:
            try:
                song_logic.update_from_files(song)
            except Exception as ex:
                logger.bind(song=song.dict()).exception(
                    f"Something went wrong during the reset"
                )
    print(time.time() - start)
