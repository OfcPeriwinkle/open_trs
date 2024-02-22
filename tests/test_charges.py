from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient

import open_trs.db
from tests.conftest import AuthActions


def test_create_charges(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()
    test_date = datetime(2024, 1, 1)
    new_charges = [{'hours': 1,
                    'project': 1,
                    'date_charged': test_date},
                   {'hours': 2,
                    'project': 2,
                    'date_charged': test_date}]

    response = client.post('/charges/create',
                           headers={'Content-Type': 'application/json',
                                    'Authorization ': f'Bearer {token}'},
                           json={'charges': new_charges})

    assert response.status_code == 200
    inserted_charges = response.get_json().get('charges')

    with app.app_context():
        db = open_trs.db.get_db()
        charges = db.execute(
            'SELECT * FROM Charges WHERE user = ? AND date_charged = ? ORDER BY id',
            (1,
             test_date)).fetchall()

        assert len(charges) == 2

        for i, charge in enumerate(charges):
            assert charge['hours'] == inserted_charges[i]['hours'] == new_charges[i]['hours']
            assert charge['project'] == inserted_charges[i]['project'] == new_charges[i]['project']
            assert charge['date_charged'] == inserted_charges[i]['date_charged'] == new_charges[i]['date_charged']
            assert charge['user'] == inserted_charges[i]['user'] == 1


@pytest.mark.parametrize('hours, project, date_charged, message, status', (
    (None, 1, datetime(2024, 1, 1), b'Hours required', 400),
    (1, None, datetime(2024, 1, 1), b'Project ID required', 400),
    (1, 2, None, b'Date required', 400),
    (0, 1, datetime(2024, 1, 1), b'Hours must be greater than 0', 400),
    (1, 42, datetime(2024, 1, 1), b'Project not found', 404),
    (1, 3, datetime(2024, 1, 1), b'Forbidden', 403),
    (1, 1, datetime(2024, 2, 1), b'Project already charged for this date', 400),
))
def test_create_charges_validate_input(client: FlaskClient, auth: AuthActions, app: Flask, hours,
                                       project, date_charged, message, status):
    token = auth.login()

    response = client.post(
        '/charges/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'charges': [{'hours': hours, 'project': project, 'date_charged': date_charged}]})

    assert response.status_code == status
    assert message in response.data


def test_create_charges_empty(client: FlaskClient, auth: AuthActions):
    token = auth.login()

    response = client.post(
        '/charges/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'charges': []})

    assert response.status_code == 400
    assert b'No charges provided' in response.data


def test_get_charges(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()

    response = client.get(
        '/charges/',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'date_range': {'start': '2024-02-01', 'end': '2024-02-28'}})

    assert response.status_code == 200
    charges = response.get_json().get('charges')

    assert len(charges) == 2

    with app.app_context():
        db = open_trs.db.get_db()
        db_charges = db.execute(
            'SELECT * FROM Charges WHERE user = ? AND date_charged BETWEEN ? AND ?'
            'ORDER BY date_charged, id',
            (1, '2024-02-01', '2024-02-28')).fetchall()

        assert charges == [dict(charge) for charge in db_charges]


def test_get_charges_missing(client: FlaskClient, auth: AuthActions):
    token = auth.login()

    response = client.get(
        '/charges/',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'date_range': {'start': '2024-03-01', 'end': '2024-03-31'}})

    assert response.status_code == 200
    charges = response.get_json().get('charges')

    assert len(charges) == 0


def test_get_charges_all(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()

    response = client.get(
        '/charges/',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    charges = response.get_json().get('charges')

    assert len(charges) == 3

    with app.app_context():
        db = open_trs.db.get_db()
        db_charges = db.execute(
            'SELECT * FROM Charges WHERE user = ? ORDER BY date_charged, id',
            (1,)).fetchall()

        assert charges == [dict(charge) for charge in db_charges]


@pytest.mark.parametrize('start, end, message, status', (
    (None, '2024-02-28', b'Start date required', 400),
    ('2024-02-01', None, b'End date required', 400),
    ('2024-03-01', '2024-02-28', b'End date must be after start date', 400),
))
def test_get_charges_validate_input(client: FlaskClient, auth: AuthActions, start, end, message,
                                    status):
    token = auth.login()

    response = client.get(
        '/charges/',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'date_range': {'start': start, 'end': end}})

    assert response.status_code == status
    assert message in response.data
