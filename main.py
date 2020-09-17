import click
from pony.orm import db_session

from app.db.base import init_db
from scripts import mb


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--no-progress",
    is_flag=True,
    default=True,
    help="Dont print progress of the sync, may result in speedup",
)
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
def sync_mb(no_progress, replace, query, field):
    """Sync MusicBee data to the database"""
    init_db()
    with db_session:
        mb.sync_data(
            print_progress=no_progress,
            replace_existing=replace,
            query=query,
            fields=field,
        )


if __name__ == "__main__":
    cli()
