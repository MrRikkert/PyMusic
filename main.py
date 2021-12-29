# Import settings before anything else
import shared.settings  # noqa isort:skip
import os
from datetime import datetime

import click
from loguru import logger
from pony.orm import db_session

from cli import mb, scrobbles, songs
from shared.db.base import init_db


@click.group()
def cli():
    pass


@logger.catch()
def wrap_cli():
    try:
        init_db()
        with db_session:
            cli(standalone_mode=False)
    except (KeyboardInterrupt, click.Abort):
        logger.warning("User cancelled operation")
    except Exception:
        logger.exception("An unexpected error occured")


@cli.command()
@click.option(
    "--replace",
    is_flag=True,
    default=False,
    help="Replace all tags stored in the database with the new tags",
)
@click.option(
    "--query", "-q", default="", help="Only sync music that matches the given query"
)
@click.option(
    "--field",
    "-f",
    multiple=True,
    default=["ArtistPeople", "Title", "Album"],
    show_default=True,
    help="""
    Field to use in query.
    Use multiple times to select multiple fields.
    """,
)
def sync_mb(replace, query, field):
    """Sync MusicBee data to the database"""
    logger.bind(params=locals()).info("Syncing musicbee library")
    mb.sync_data(replace_existing=replace, query=query, fields=field)


@cli.command()
@click.option(
    "--path",
    "-p",
    help="Path where the export should be stored",
    default="./.exports/mb.pickle",
    show_default=True,
)
@click.option(
    "--query", "-q", default="", help="Only sync music that matches the given query"
)
@click.option(
    "--field",
    "-f",
    multiple=True,
    default=["ArtistPeople", "Title", "Album"],
    show_default=True,
    help="""
    Field to use in query.
    Use multiple times to select multiple fields.
    """,
)
def export_mb(query, field, path):
    """export musicbee data to a pickle file"""
    if not path:
        path = "./.exports/mb.pickle"
    logger.bind(params=locals()).info("Syncing musicbee library")
    mb.export_data(query=query, fields=field, export_path=path)


@cli.command()
@click.option(
    "--path",
    "-p",
    help="Path where the export is stored",
    default="./.exports/mb.pickle",
    show_default=True,
)
@click.option(
    "--replace",
    is_flag=True,
    default=False,
    show_default=True,
    help="Replace all tags stored in the database with the new tags",
)
def import_mb(replace, path):
    """import musicbee data from an exported file"""
    path = "./.exports/mb.pickle"
    logger.bind(params=locals()).info("Syncing musicbee library")
    mb.import_data(replace_existing=replace, export_path=path)


@cli.command()
@click.option("--name", "-n", "lastfm", help="Your LastFM username", required=True)
def sync_scrobbles(lastfm: str):
    """Syncs all scrobbles from LastFM to the database"""
    logger.info(f"Syncing LastFm scrobbles: {lastfm}")
    if lastfm:
        scrobbles.sync_lastfm_scrobbles(lastfm)


@cli.command()
@click.option(
    "--path",
    "-p",
    default=f"./.exports/scrobbles/{datetime.now():%Y%m%d%H%M}.csv",
    help="sync scrobbles from a local csv file",
)
def export(path):
    """Export scrobbles to a csv file"""
    logger.info(f"Exporting scrobbles to: {path}")
    scrobbles.export_scrobbles(path)


@cli.command("import")
@click.option("--path", "-p", help="sync scrobbles from a local csv file")
def import_csv(path):
    """Import scrobbles from a csv file"""
    if not path:
        path = f"./.exports/scrobbles/{os.listdir('./.exports/scrobbles')[-1]}"
        print(path)
    logger.bind(path=path).info("Importing scrobbles")
    if os.path.exists(path):
        scrobbles.import_scrobbles(path)
    else:
        logger.info("File does not exist")


@cli.command()
def reset_tags():
    """Removes all tags from song in the db
    and replaces them with the tags in the file table.
    use when you update a lot of tags"""
    songs.reset_all_tags()


@cli.command()
def save_art():
    """Save album art to a location"""
    mb.get_albums()


if __name__ == "__main__":
    wrap_cli()
