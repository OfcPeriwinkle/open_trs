import functools
import time
import werkzeug.security

import jwt
from flask import Blueprint, current_app, g, request, jsonify

import open_trs.db


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view: callable):
    """
    Decorator that checks if the user is logged in before executing the view function by checking
    the validity of a JWT.

    If the provided JWT is invalid or expired, it returns a JSON response with an error message
    and status code 400.

    Decorated functions will receive an additional argument, a dictionary containing the user
    information as specified in the Users table.

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
            return jsonify({'error': 'Missing token'}, 400)

        try:
            decoded_jwt = jwt.decode(encoded_jwt, current_app.config['SECRET_KEY'])
        except jwt.InvalidSignatureError:
            return jsonify({'error': 'Token signature verification failed'}, 400)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}, 400)

        user_id = decoded_jwt['sub']

        db = open_trs.db.get_db()
        user = db.execute('SELECT * FROM Users WHERE id = ?', (user_id,))

        return view(user, *args, **kwargs)

    return wrapped_view


@bp.route('/register', methods=('POST'))
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

    error = None

    if username is None:
        error = 'Username is required'
    elif email is None:
        error = 'Email is required'
    elif password is None:
        error = 'Password is required'

    if error is None:
        db = open_trs.db.get_db()

        try:
            db.execute('INSERT INTO Users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, werkzeug.security.generate_password_hash(password)))
            db.commit()
        except db.IntegrityError:
            error = f'Either user "{username}" or email "{email}" is already registered.'
        else:
            return jsonify({'message': 'User registered successfully.'}, 201)

    return jsonify({'error': error}, 400)


@bp.route('/login', methods=('POST'))
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

    error = None

    if user is None:
        error = 'Incorrect username.'
    elif not werkzeug.security.check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        issue_time = int(time.time())
        expiration_time = issue_time + current_app.config['JWT_EXPIRATION']

        claims = {'iat': issue_time, 'exp': expiration_time, 'sub': user['id']}
        encoded_jwt = jwt.encode(claims, current_app.config['SECRET_KEY'])

        return jsonify({'token': encoded_jwt}, 200)

    # An error occurred
    return jsonify({'error': error}, 400)
