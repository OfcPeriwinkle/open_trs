import datetime

from flask import Blueprint, jsonify, request

import open_trs.db
import open_trs.auth


bp = Blueprint('charges', __name__, url_prefix='/charges')


@bp.route('/', methods=['GET'])
@open_trs.auth.login_required
def get_charges(user_id: int):
    """
    Get all charges for the user.

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
