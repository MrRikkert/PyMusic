import click
from loguru import logger
from pony.orm import db_session

from shared import settings  # Import settings before anything else
from shared.db.base import db, init_db
from cli import mb, scrobbles
from pony import orm
from shared.db.models import ScrobbleDb


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
    logger.bind(params=locals()).info(f"Syncing musicbee library")
    mb.sync_data(replace_existing=replace, query=query, fields=field)


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
    default="scrobbles.csv",
    help="sync scrobbles from a local csv file",
    show_default=True,
)
def export(path):
    """Export scrobbles to a csv file"""
    logger.info(f"Exporting scrobbles to: {path}")
    scrobbles.export_scrobbles(path)


@cli.command("import")
@click.option(
    "--path",
    "-p",
    default="scrobbles.csv",
    help="sync scrobbles from a local csv file",
    show_default=True,
)
def import_csv(path):
    """Import scrobbles from a csv file"""
    logger.bind(path=path).info("Importing scrobbles")
    scrobbles.import_scrobbles(path)


# TODO Fix with new db_session method (wrapped for all functions)
# @cli.command()
# def renew():
#     """Re-creates the database.
#     1. Backup scrobbles
#     2. Delete all tables
#     3. Create tables
#     4. Restore scrobbles
#     5. Import music from musicbee
#     """
#     logger.info("Re creating database")
#     click.confirm("Are you sure you want to delete everything?")
#     init_db()
#     with db_session:
#         click.echo("Start backing-up scrobbles")
#         scrobbles.export_scrobbles("backup.csv")

#     click.echo("Dropping all tables")
#     db.drop_all_tables(with_all_data=True)

#     click.echo("Creating tables")
#     db.create_tables()

#     with db_session:
#         click.echo("Importing scrobbles")
#         scrobbles.import_scrobbles("backup.csv")

#         click.echo("Retrieving MusicBee data")
#         mb.sync_data()


@cli.command()
def save_art():
    mb.get_albums()


if __name__ == "__main__":
    wrap_cli()
