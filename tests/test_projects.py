import pytest
from flask import Flask
from flask.testing import FlaskClient

import open_trs.db
from tests.conftest import AuthActions


def test_create_project(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()
    new_project_info = {
        'name': 'new_project',
        'category': 1,
        'description': 'This is a test project!'
    }

    response = client.post(
        '/projects/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json=new_project_info)

    assert response.status_code == 201

    success_message = response.get_json().get('message')
    assert success_message is not None
    assert 'created successfully' in success_message

    inserted_project = response.get_json().get('project')

    with app.app_context():
        db = open_trs.db.get_db()
        projects = db.execute(
            'SELECT * FROM Projects WHERE name = ? AND owner = ?',
            ('new_project', 1)).fetchall()

        assert len(projects) == 1

        for key in new_project_info:
            assert projects[0][key] == new_project_info[key]
            assert projects[0][key] == inserted_project[key]


@pytest.mark.parametrize(('name', 'category', 'description', 'message'), (
    ('', 1, '', b'Project name is required'),
    ('new_project', -1, '', b'Invalid category'),
    ('Existing Project', 0, '', b'already exists')
))
def test_create_project_validate_input(
        client: FlaskClient, auth: AuthActions, name, category, description, message):
    token = auth.login()

    response = client.post(
        '/projects/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'name': name, 'category': category, 'description': description})

    assert response.status_code == 400
    assert message in response.data


def test_get_projects(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()

    response = client.get(
        '/projects/',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

    assert response.status_code == 200

    projects = response.get_json().get('projects')
    assert projects is not None
    assert len(projects) == 2

    with app.app_context():
        db = open_trs.db.get_db()
        db_projects = db.execute(
            'SELECT * FROM Projects'
            ' WHERE owner = ?'
            ' ORDER BY id', (1,)).fetchall()

        assert len(projects) == len(db_projects)

        for project, db_project in zip(projects, db_projects):
            for key in project:
                if key == 'created':
                    continue

                assert project[key] == db_project[key]


def test_get_project(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()

    response = client.get(
        '/projects/1',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

    assert response.status_code == 200

    with app.app_context():
        db = open_trs.db.get_db()
        db_project = db.execute('SELECT * FROM Projects WHERE id = ?', (1,)).fetchone()

        project = response.get_json().get('project')

        for key, value in project.items():
            if key == 'created':
                continue

            assert value == db_project[key]


@pytest.mark.parametrize(('project_id', 'message', 'status'), (
    (42, b'Project 42 does not exist', 404),
    (3, b'Forbidden', 403)
))
def test_get_project_validate_input(
        client: FlaskClient, auth: AuthActions, project_id, message, status):
    token = auth.login()

    response = client.get(
        f'/projects/{project_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

    assert response.status_code == status
    assert message in response.data


def test_update_project(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()

    response = client.put(
        '/projects/1/update',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'},
        json={
            'name': 'Updated Project',
            'description': 'This is an updated project!',
            'category': 2})

    assert response.status_code == 200

    success_message = response.get_json().get('message')
    assert success_message is not None
    assert 'updated successfully' in success_message

    updated_project = response.get_json().get('project')

    with app.app_context():
        db = open_trs.db.get_db()
        db_project = db.execute('SELECT * FROM Projects WHERE id = ?', (1,)).fetchone()

        for key, value in updated_project.items():
            if key == 'created':
                continue

            assert value == db_project[key]


@pytest.mark.parametrize(('project_id', 'name', 'description', 'message', 'status'), (
    (42, 'Updated Project', 'This is an updated project!',
     b'Project 42 does not exist', 404),
    (3, 'Updated Project', 'This is an updated project!', b'Forbidden', 403),
    (1, '', '', b'Nothing to update', 400),
))
def test_update_project_validate_input(
        client: FlaskClient, auth: AuthActions, project_id, name, description, message, status):
    token = auth.login()

    response = client.put(
        f'/projects/{project_id}/update',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'},
        json={'name': name, 'description': description})

    assert response.status_code == status
    assert message in response.data


def test_delete_project(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()

    response = client.delete(
        '/projects/1/delete',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

    assert response.status_code == 200

    success_message = response.get_json().get('message')
    assert success_message is not None
    assert 'deleted successfully' in success_message

    with app.app_context():
        db = open_trs.db.get_db()

        project = db.execute('SELECT * FROM Projects WHERE id = ?', (1,)).fetchone()
        assert project is None

        charges = db.execute('SELECT * FROM Charges WHERE project = ?', (1,)).fetchall()
        assert len(charges) == 0


@pytest.mark.parametrize(('project_id', 'message', 'status'), (
    (42, b'Project 42 does not exist', 404),
    (3, b'Forbidden', 403)
))
def test_delete_project_validate_input(
        client: FlaskClient, auth: AuthActions, project_id, message, status):
    token = auth.login()

    response = client.delete(
        f'/projects/{project_id}/delete',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

    assert response.status_code == status
    assert message in response.data
