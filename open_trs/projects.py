from flask import abort, Blueprint, jsonify

import open_trs.db
import open_trs.auth


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
