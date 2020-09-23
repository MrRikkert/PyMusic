import click
from pony.orm import db_session

from app.db.base import init_db, db
from scripts import mb, scrobbles


@click.group()
def cli():
    pass


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
    init_db()
    with db_session:
        mb.sync_data(replace_existing=replace, query=query, fields=field)


@cli.command()
@click.option(
    "--lastfm",
    help="Sync scrobbles from lastfm. will continue from the last recorded scrobble. Enter your username as argument",
)
@click.option(
    "--csv",
    default="scrobbles.csv",
    help="sync scrobbles from a local csv file",
    show_default=True,
)
def sync_scrobbles(lastfm: str, csv: str):
    """Sync scrobbles to the database, either from lastfm or a csv"""
    init_db()
    with db_session:
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
    init_db()
    with db_session:
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
    init_db()
    with db_session:
        scrobbles.import_scrobbles(path)


@cli.command()
def renew():
    """Re-creates the database. Creates a backup of your scrobbles and restores them"""
    click.confirm("Are you sure you want to delete everything?")
    init_db()
    with db_session:
        click.echo("Start backing-up scrobbles")
        scrobbles.export_scrobbles("backup.csv")

    click.echo("Dropping all tables")
    db.drop_all_tables(with_all_data=True)

    click.echo("Creating tables")
    db.create_tables()

    with db_session:
        click.echo("Importing scrobbles")
        scrobbles.import_scrobbles("backup.csv")

        click.echo("Retrieving MusicBee data")
        mb.sync_data()


if __name__ == "__main__":
    cli()
