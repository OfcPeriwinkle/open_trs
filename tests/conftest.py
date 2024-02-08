import os

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient

import open_trs
import open_trs.db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


class AuthActions:
    """
    Helper class for performing authentication actions.
    """

    def __init__(self, client: FlaskClient):
        """
        Instantiate helper class for performing authentication actions.

        Args:
            client (FlaskClient): The Flask client object.
        """

        self._client = client

    def login(self, username: str = 'test', email: str = 'test@test.com', password: str = 'test'):
        """
        Performs a login action.

        Args:
            username: The username to use for login. Defaults to 'test'.
            email: The email to use for login. Defaults to 'test@test.com'.
            password: The password to use for login. Defaults to 'test'.

        Returns:
            The JWT token received from the server or None if authentication was unsuccessful.
        """

        response = self._client.post(
            '/auth/login',
            headers={'Content-Type': 'application/json'},
            json={'username': username,
                  'email': email,
                  'password': password})

        return response.get_json().get('token')


@pytest.fixture
def app() -> Flask:
    """
    Creates and initializes the Flask app for testing purposes.

    Yields:
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


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)
