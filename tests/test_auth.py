import pytest
from flask import Flask
from flask.testing import FlaskClient

import open_trs.db


def test_register_new_user(client: FlaskClient, app: Flask):
    new_user_info = {
        'username': 'new_user',
        'email': 'new_user@email.com',
        'password': 'new_user_password'}

    response = client.post(
        '/auth/register',
        headers={'Content-Type': 'application/json'},
        json=new_user_info)

    assert response.status_code == 201

    success_message = response.get_json().get('message')
    assert success_message is not None
    assert 'registered successfully' in success_message

    with app.app_context():
        db = open_trs.db.get_db()
        users = db.execute('SELECT * FROM Users WHERE username = ?', ('new_user',)).fetchall()

        assert len(users) == 1
        assert users[0]['username'] == new_user_info['username']
        assert users[0]['email'] == new_user_info['email']
        assert users[0]['password'] != new_user_info['password']


@pytest.mark.parametrize(('username', 'email', 'password', 'message'), (
    ('', '', '', b'Username is required'),
    ('test', '', '', b'Email is required'),
    ('test', 'test@test.com', '', b'Password is required'),
    ('test', 'test@test.com', 'test',
     b'Either user \\"test\\" or email \\"test@test.com\\" is already registered.')
))
def test_register_validate_input(client: FlaskClient, username, email, password, message):
    response = client.post(
        '/auth/register',
        headers={'Content-Type': 'application/json'},
        json={'username': username, 'email': email, 'password': password})

    assert response.status_code == 400
    assert message in response.data
