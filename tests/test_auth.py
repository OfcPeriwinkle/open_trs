import json

import pytest
from flask import Flask
from flask.testing import FlaskClient


def test_register_already_existing(client: FlaskClient):
    response = client.post(
        '/auth/register',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test'}))

    assert response.status_code == 400

    error_message = response.get_json().get('error')
    assert error_message is not None
    assert 'is already registered' in error_message
