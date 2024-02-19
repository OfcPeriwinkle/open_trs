from flask import Blueprint, jsonify, request

import open_trs.db
import open_trs.auth

_UPDATABLE_FIELDS = ['name', 'description', 'category']

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('/', methods=['GET'])
@open_trs.auth.login_required
def get_projects(user_id: int):
    """
    Get all projects owned by the user.

    Args:
        user_id: The user's ID.
    """

    db = open_trs.db.get_db()

    projects = db.execute('SELECT * FROM Projects WHERE owner = ? ORDER BY id',
                          (user_id,)).fetchall()

    return jsonify({'projects': [dict(project) for project in projects]}), 200


@bp.route('/<int:project_id>', methods=['GET'])
@open_trs.auth.login_required
def get_project(user_id: int, project_id: int):
    db = open_trs.db.get_db()

    project = db.execute(
        'SELECT * FROM Projects WHERE id = ?', (project_id, )).fetchone()

    if project is None:
        raise open_trs.InvalidUsage(f'Project {project_id} does not exist', 404)

    if project['owner'] != user_id:
        raise open_trs.InvalidUsage('Forbidden', 403)

    return jsonify({'project': dict(project)}), 200


@bp.route('/create', methods=['POST'])
@open_trs.auth.login_required
def create_project(user_id: int):
    request_json = request.get_json()
    name = request_json.get('name')
    category = request_json.get('category')
    description = request_json.get('description')

    if not name:
        raise open_trs.InvalidUsage('Project name is required', 400)
    elif category is not None and category < 0:
        # TODO: this should check for existence in enum, or db table
        raise open_trs.InvalidUsage('Invalid category', 400)

    db = open_trs.db.get_db()
    existing_project = db.execute(
        'SELECT name FROM Projects WHERE name = ? AND owner = ?', (name, user_id)).fetchone()

    if existing_project is not None:
        raise open_trs.InvalidUsage(f'A project named "{name}" already exists for this user', 400)

    db.execute(
        'INSERT INTO Projects (owner, name, category, description)'
        ' VALUES (?, ?, ?, ?)', (user_id, name, category, description))
    db.commit()

    return jsonify({'message': 'Project created successfully'}), 201


@bp.route('/<int:project_id>/update', methods=['PUT'])
@open_trs.auth.login_required
def update_project(user_id: int, project_id: int):
    request_json = request.get_json()

    db = open_trs.db.get_db()
    project = db.execute('SELECT * FROM Projects WHERE id = ?',
                         (project_id,)).fetchone()

    if project is None:
        raise open_trs.InvalidUsage(f'Project {project_id} does not exist', 404)

    if project['owner'] != user_id:
        raise open_trs.InvalidUsage('Forbidden', 403)

    updated = False
    project = dict(project)

    for field in _UPDATABLE_FIELDS:
        if field in request_json and request_json[field]:
            project[field] = request_json[field]
            updated = True

    if not updated:
        raise open_trs.InvalidUsage('Nothing to update', 400)

    update_query = f'UPDATE Projects SET {" = ?, ".join(_UPDATABLE_FIELDS)} = ? WHERE owner = ? AND id = ?'
    update_values = [project[field] for field in _UPDATABLE_FIELDS]
    update_values.extend([user_id, project_id])

    db.execute(update_query, update_values)
    db.commit()

    return jsonify({'message': f'Project {project_id} updated successfully',
                   'project': project}), 200


@bp.route('/<int:project_id>/delete', methods=['DELETE'])
@open_trs.auth.login_required
def delete_project(user_id: int, project_id: int):
    db = open_trs.db.get_db()
    project = db.execute('SELECT * FROM Projects WHERE id = ?',
                         (project_id,)).fetchone()

    if project is None:
        raise open_trs.InvalidUsage(f'Project {project_id} does not exist', 404)

    if project['owner'] != user_id:
        raise open_trs.InvalidUsage('Forbidden', 403)

    db.execute('DELETE FROM Projects WHERE owner = ? AND id = ?', (user_id, project_id))
    db.commit()

    return jsonify({'message': f'Project {project_id} deleted successfully'}), 200
