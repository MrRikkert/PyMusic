import click

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
def sync_mb(no_progress):
    """Sync MusicBee data to the database"""
    init_db()
    mb.sync_data(print_progress=no_progress)


if __name__ == "__main__":
    cli()
