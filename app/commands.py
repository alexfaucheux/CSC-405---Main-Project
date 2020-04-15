import click
from flask.cli import with_appcontext
from app.extensions import db


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
