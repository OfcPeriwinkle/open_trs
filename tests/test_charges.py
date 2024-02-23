import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient

import open_trs.db
from tests.conftest import AuthActions


def _compare_charges(charges, db_charges):
    for db_charge, charge in zip(db_charges, charges):
        for key in db_charge.keys():
            if key == 'created':
                continue
            elif key == 'date_charged':
                assert str(db_charge[key]) == charge[key]
            else:
                assert db_charge[key] == charge[key]


def test_create_charges(client: FlaskClient, auth: AuthActions, app: Flask):
    token = auth.login()
    test_date = str(datetime.date(2024, 1, 1))

    new_charges = [{'hours': 1,
                    'project': 1,
                    'date_charged': test_date},
                   {'hours': 2,
                    'project': 2,
                    'date_charged': test_date}]

    response = client.post('/charges/create',
                           headers={'Content-Type': 'application/json',
                                    'Authorization': f'Bearer {token}'},
                           json={'charges': new_charges})

    assert response.status_code == 201
    inserted_charges = response.get_json().get('charges')

    with app.app_context():
        db = open_trs.db.get_db()
        db_charges = db.execute(
            'SELECT * FROM Charges WHERE user = ? AND date_charged = ? ORDER BY id',
            (1,
             test_date)).fetchall()

        assert len(db_charges) == 2

        for i, db_charge in enumerate(db_charges):
            assert db_charge['hours'] == inserted_charges[i]['hours'] == new_charges[i]['hours']
            assert db_charge['project'] == inserted_charges[i]['project'] == new_charges[i]['project']
            assert str(
                db_charge['date_charged']) == inserted_charges[i]['date_charged'] == new_charges[i]['date_charged']
            assert db_charge['user'] == inserted_charges[i]['user'] == 1


@pytest.mark.parametrize('hours, project, date_charged, message, status', (
    (None, 1, datetime.date(2024, 1, 1), b'Hours required', 400),
    (1, None, datetime.date(2024, 1, 1), b'Project required', 400),
    (1, 2, None, b'Invalid date format, use YYYY-MM-DD', 400),
    (0, 1, datetime.date(2024, 1, 1), b'Hours must be greater than 0', 400),
    (1, 42, datetime.date(2024, 1, 1), b'Project not found', 404),
    (1, 3, datetime.date(2024, 1, 1), b'Forbidden', 403),
    (1, 1, datetime.date(2024, 2, 1), b'Project already charged for this date', 400),
    (1, 1, 'not-a-date', b'Invalid date format, use YYYY-MM-DD', 400),
    (-1, 1, datetime.date(2024, 1, 1), b'Hours must be greater than 0', 400),
))
def test_create_charges_validate_input(client: FlaskClient, auth: AuthActions, app: Flask, hours,
                                       project, date_charged, message, status):
    token = auth.login()

    response = client.post(
        '/charges/create',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'charges': [{'hours': hours, 'project': project, 'date_charged': str(date_charged)}]})

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

        _compare_charges(charges, db_charges)


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
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={})

    assert response.status_code == 200
    charges = response.get_json().get('charges')

    assert len(charges) == 3

    with app.app_context():
        db = open_trs.db.get_db()
        db_charges = db.execute(
            'SELECT * FROM Charges WHERE user = ? ORDER BY date_charged, id',
            (1,)).fetchall()

        _compare_charges(charges, db_charges)


@pytest.mark.parametrize('start, end, message, status', (
    (None, '2024-02-28', b'Start date required', 400),
    ('2024-02-01', None, b'End date required', 400),
    ('2024-03-01', '2024-02-28', b'End date must be after start date', 400),
    ('not-a-date', '2024-02-28', b'Invalid date format, use YYYY-MM-DD', 400),
    ('2024-02-01', 'not-a-date', b'Invalid date format, use YYYY-MM-DD', 400),
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


def test_update_charges(auth: AuthActions, client: FlaskClient, app: Flask):
    token = auth.login()
    charge_updates = [{'id': 1, 'hours': 3},
                      {'id': 2, 'hours': 4}]

    response = client.put(
        '/charges/update',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'charges': charge_updates})

    assert response.status_code == 200
    updated_charges = response.get_json().get('charges')

    with app.app_context():
        db = open_trs.db.get_db()
        db_charges = db.execute(
            'SELECT * FROM Charges WHERE user = ? ORDER BY date_charged, id',
            (1,)).fetchall()

        assert len(db_charges) == 2

        for db_charge, updated_charge in zip(db_charges, updated_charges):
            assert db_charge['hours'] == updated_charge['hours']
            assert db_charge['id'] == updated_charge['id']


@pytest.mark.parametrize('id, hours, message, status', (
    (1, None, b'Hours required', 400),
    (1, -1, b'Hours must be greater than 0', 400),
    (42, 1, b'Charge not found', 404),
    (3, 1, b'Forbidden', 403),
))
def test_update_charges_validate_input(client: FlaskClient, auth: AuthActions, id, hours,
                                       message, status):
    token = auth.login()

    response = client.put(
        '/charges/update',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        json={'charges': [{'id': id, 'hours': hours}]})

    assert response.status_code == status
    assert message in response.data
