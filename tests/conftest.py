import os

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

import open_trs
import open_trs.db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app() -> Flask:
    """
    Creates and initializes the Flask app for testing purposes.

    Returns:
        Flask: The Flask app object.
    """
    app = open_trs.create_app(testing=True)

    with app.app_context():
        open_trs.db.init_db()

        db = open_trs.db.get_db()
        db.executescript(_data_sql)

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """
    Returns a test client for the Flask application. This client may be used to make requests
    to the application without running the server.

    Args:
        app: The Flask application object.

    Returns:
        A FlaskClient instance.
    """

    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """
    Returns a FlaskCliRunner instance for testing the Flask app. This can be used to call command
    line components registered with the application.

    Args:
        app: The Flask app to be tested.

    Returns:
        A FlaskCliRunner instance.

    """

    return app.test_cli_runner()
