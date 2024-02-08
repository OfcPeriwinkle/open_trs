import pytest
from flask import Flask
from flask.testing import FlaskClient

import open_trs.db
from tests.conftest import AuthActions


def test_create_project(client: FlaskClient, auth: AuthActions, app: Flask):
    new_project_info = {'owner': 1,
                        'name': 'new_project',
                        'category': 1,
                        'description': 'This is a test project!'}

    token = auth.login()

    response = client.post(
        '/projects/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json=new_project_info)

    assert response.status_code == 201

    success_message = response.get_json().get('message')
    assert success_message is not None
    assert 'created successfully' in success_message

    with app.app_context():
        db = open_trs.db.get_db()
        projects = db.execute(
            'SELECT * FROM Projects WHERE name = ? AND owner = ?',
            ('new_project', 1)).fetchall()

        assert len(projects) == 1

        for key in new_project_info:
            assert projects[0][key] == new_project_info[key]


@pytest.mark.parametrize(('owner', 'name', 'category', 'description', 'message'), (
    (1, '', 1, '', b'Project name is required'),
    (42, 'new_project', 1, '', b'Unauthorized'),
    (1, 'new_project', -1, '', b'Invalid category'),
    (1, 'Existing Project', 0, '', b'Project already exists')
))
def test_create_project_validate_input(
        client: FlaskClient, auth: AuthActions, owner, name, category, description, message):
    token = auth.login()

    response = client.post(
        '/projects/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'owner': owner, 'name': name, 'category': category, 'description': description})

    assert response.status_code == 400
    assert message in response.data
