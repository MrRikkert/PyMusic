import click
from pony.orm import db_session

from app.db.base import init_db
from scripts import mb


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


if __name__ == "__main__":
    cli()
