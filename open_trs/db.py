import click
import sqlite3

from flask import Flask, g, current_app


def get_db() -> sqlite3.Connection:
    """
    Get the SQLite database connection.

    Returns:
        sqlite3.Connection: The SQLite database connection.
    """

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e: Exception = None):
    """
    Close the SQLite database connection.

    Args:
        e (Exception, optional): The exception that occurred, if any.
    """

    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    Initialize the database by executing the schema.sql file.
    """

    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """
    Click command to initialize the database.

    This command clears existing tables and creates new tables.
    """

    init_db()
    click.echo('Initialized the database.')


def init_app(app: Flask):
    """
    Initialize the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
