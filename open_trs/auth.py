import functools
import re
import time
import werkzeug.security

import jwt
from flask import abort, Blueprint, current_app, request, jsonify

import open_trs
import open_trs.db

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view: callable):
    """
    Decorator that checks if the user is logged in before executing the view function by checking
    the validity of a JWT.

    If the provided JWT is invalid or expired, it returns a JSON response with an error message
    and status code 400.

    Decorated functions will receive the user's ID integer as an additional argument

    Args:
        view (callable): The view function to be decorated.

    Returns:
        callable: The decorated view function.
    """

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        try:
            encoded_jwt = request.headers['Authorization'].split(' ')[1]
        except KeyError:
            raise open_trs.InvalidUsage('Missing token', 400)

        try:
            decoded_jwt = jwt.decode(
                encoded_jwt,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'])
        except jwt.InvalidSignatureError:
            raise open_trs.InvalidUsage('Token signature verification failed', 400)
        except jwt.ExpiredSignatureError:
            raise open_trs.InvalidUsage('Expired token', 400)
        except jwt.DecodeError:
            raise open_trs.InvalidUsage('Unable to decode token', 400)

        user_id = decoded_jwt['sub']

        return view(user_id, *args, **kwargs)

    return wrapped_view


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    This function handles the registration of a new user by extracting the username, email, and
    password from the request form. It performs validation checks on the input fields and inserts
    the user's information into the database if the input is valid. If the registration is
    successful, it returns a JSON response with a success message and status code 201. If there is
    an error during registration, it returns a JSON response with an error message and status code
    400.

    Returns:
        JSON response with success message and status code 201 if registration is successful, JSON
        response with error message and status code 400 if there is an error during registration
    """

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username:
        raise open_trs.InvalidUsage('Username is required', 400)
    elif not email:
        raise open_trs.InvalidUsage('Email is required', 400)
    elif not EMAIL_REGEX.match(email):
        raise open_trs.InvalidUsage('Invalid email', 400)
    elif not password:
        raise open_trs.InvalidUsage('Password is required', 400)

    db = open_trs.db.get_db()

    try:
        db.execute('INSERT INTO Users (username, email, password) VALUES (?, ?, ?)',
                   (username, email, werkzeug.security.generate_password_hash(password)))
        db.commit()
    except db.IntegrityError:
        raise open_trs.InvalidUsage(
            f'Either user "{username}" or email "{email}" is already registered.', 400)

    return jsonify({'message': 'User registered successfully.'}), 201


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticates the user by checking the provided username and password.

    If the authentication is successful, a JSON response containing a JWT token is returned.
    If there is an error, a JSON response containing the error message is returned.

    Returns:
        JSON response with token or error message
    """

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    db = open_trs.db.get_db()
    user = db.execute(
        'SELECT id, password FROM Users WHERE username = ?', (username,)).fetchone()

    if user is None:
        raise open_trs.InvalidUsage('Incorrect username', 400)
    elif not werkzeug.security.check_password_hash(user['password'], password):
        raise open_trs.InvalidUsage('Incorrect password', 400)

    issue_time = int(time.time())
    expiration_time = issue_time + current_app.config['JWT_EXPIRATION']

    claims = {'iat': issue_time, 'exp': expiration_time, 'sub': user['id']}
    encoded_jwt = jwt.encode(claims, current_app.config['SECRET_KEY'])

    return jsonify({'token': encoded_jwt}), 200
