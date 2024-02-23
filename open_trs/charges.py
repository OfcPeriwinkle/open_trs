import datetime
import sqlite3
from typing import List, Tuple

from flask import Blueprint, jsonify, request
from open_trs import projects

import open_trs.db
import open_trs.auth


bp = Blueprint('charges', __name__, url_prefix='/charges')


def _validate_and_filter_charges(charges: List[dict]) -> Tuple[set, set]:
    """
    Validate charges from an incoming request and filter them so that all are unique.

    Args:
        charges: List of charges.

    Returns:
        A tuple containing unique charges and unique projects.
    """

    unique_charges = set()
    unique_projects = set()

    for charge in charges:
        hours = charge.get('hours')
        project_id = charge.get('project')
        date_charged = charge.get('date_charged')

        if hours is None or not isinstance(hours, int):
            raise open_trs.InvalidUsage('Hours required', 400)
        elif hours <= 0:
            raise open_trs.InvalidUsage('Hours must be greater than 0', 400)
        elif not project_id or not isinstance(project_id, int):
            raise open_trs.InvalidUsage('Project required', 400)
        elif not date_charged:
            raise open_trs.InvalidUsage('Date required', 400)

        try:
            date_charged = datetime.date.fromisoformat(date_charged)
        except ValueError:
            raise open_trs.InvalidUsage('Invalid date format, use YYYY-MM-DD', 400)

        unique_charges.add((hours, project_id, date_charged))
        unique_projects.add(project_id)

    return unique_charges, unique_projects


def _validate_and_get_projects(db: sqlite3.Connection, user_id: int,
                               project_ids: List[int]) -> List[dict]:
    """
    Get projects from the database and validate that all exist and are owned by the provided user.

    Args:
        db: The database connection.
        user_id: The user's ID.
        project_ids: List of project IDs.

    Returns:
        A list of project dictionaries.
    """

    projects = db.execute(
        f'SELECT owner FROM Projects WHERE id IN ({",".join("?" * len(project_ids))})',
        (*project_ids,)).fetchall()

    if len(projects) != len(project_ids):
        raise open_trs.InvalidUsage('Project not found', 404)

    for project in projects:
        if project['owner'] != user_id:
            raise open_trs.InvalidUsage('Forbidden', 403)

    return [dict(project) for project in projects]


@bp.route('/', methods=['GET'])
@open_trs.auth.login_required
def get_charges(user_id: int):
    """
    Get the user's charges.

    Args:
        user_id: The user's ID.

    Returns:
        A JSON response containing the user's charges within a specified `date_range`. If a `date_range` is not
        specified, all charges are returned.
    """

    request_json = request.get_json()
    date_range = request_json.get('date_range')

    start, end = None, None

    if date_range is not None:
        start = date_range.get('start')
        end = date_range.get('end')

        if start is None:
            raise open_trs.InvalidUsage('Start date required', 400)
        elif end is None:
            raise open_trs.InvalidUsage('End date required', 400)

        try:
            start = datetime.date.fromisoformat(start)
            end = datetime.date.fromisoformat(end)
        except ValueError:
            raise open_trs.InvalidUsage('Invalid date format, use YYYY-MM-DD', 400)

        if start > end:
            raise open_trs.InvalidUsage('End date must be after start date', 400)

    db = open_trs.db.get_db()

    if start is None and end is None:
        charges = db.execute('SELECT * FROM Charges WHERE user = ? ORDER BY date_charged, id',
                             (user_id,)).fetchall()
    else:
        charges = db.execute('SELECT * FROM Charges WHERE user = ? AND date_charged BETWEEN ? AND ?'
                             ' ORDER BY date_charged, id',
                             (user_id, start, end)).fetchall()

    charges = [dict(charge) for charge in charges]

    for charge in charges:
        charge['date_charged'] = str(charge['date_charged'])

    return jsonify({'charges': charges}), 200


@bp.route('/create', methods=['POST'])
@open_trs.auth.login_required
def create_charges(user_id: int):
    """
    Create new charges.

    Args:
        user_id: The user's ID.

    Returns:
        A JSON response containing the newly created charges.
    """

    request_json = request.get_json()
    new_charges = request_json.get('charges')

    if not new_charges:
        raise open_trs.InvalidUsage('No charges provided', 400)

    db = open_trs.db.get_db()

    unique_charges, unique_projects = _validate_and_filter_charges(new_charges)
    _validate_and_get_projects(db, user_id, list(unique_projects))

    charge_data = [(hours, project_id, date_charged, user_id)
                   for hours, project_id, date_charged in unique_charges]
    db.executemany(
        'INSERT INTO Charges (hours, project, date_charged, user)'
        ' VALUES (?, ?, ?, ?)', charge_data)
    db.commit()

    inserted_charges = db.execute(
        'SELECT * FROM Charges'
        ' WHERE (hours, project, date_charged, user) IN '
        f'({",".join(["(?,?,?,?)"] * len(charge_data))})',
        tuple([element for data in charge_data for element in data])).fetchall()

    inserted_charges = [dict(charge) for charge in inserted_charges]

    for charge in inserted_charges:
        charge['date_charged'] = str(charge['date_charged'])

    return jsonify({'message': f'Successfully inserted {len(inserted_charges)} charges',
                    'charges': inserted_charges}), 201
