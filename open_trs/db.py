import click
import sqlite3

import flask


def get_db():
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES)
        flask.g.db.row_factory = sqlite3.Row

    return flask.g.db


def close_db(e: Exception = None):
    db = flask.g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with flask.current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """
    Clear existing tables and create new tables.
    """

    init_db()
    click.echo('Initialized the database.')


def init_app(app: flask.Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
