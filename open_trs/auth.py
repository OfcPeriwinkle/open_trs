import functools
import time
import werkzeug.security

import jwt
from flask import Blueprint, current_app, g, redirect, url_for, request, jsonify, flash, render_template, session

import open_trs.db


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view: callable):
    """
    Decorator that checks if the user is logged in before executing the view function.

    Args:
        view (callable): The view function to be decorated.

    Returns:
        callable: The decorated view function.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'error': 'User is not logged in'}, 401)

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """
    Load the logged-in user from the JWT token in the request headers.

    Returns:
        If the token is valid and the user exists in the database, the function sets the `g.user` global variable to the user object.
        If the token is missing or invalid, the function returns a JSON response with an error message and a status code of 400.
    """

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
    g.user = db.execute('SELECT * FROM Users WHERE id = ?', (user_id))


@bp.route('/register', methods=('POST'))
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    error = None

    if not username:
        error = 'Username is required'
    elif not email:
        error = 'Email is required'
    elif not password:
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
    username = request.form['username']
    password = request.form['password']

    db = open_trs.db.get_db()
    user = db.execute(
        'SELECT id, password FROM Users WHERE username = ?', (username,)).fetchone()

    error = None

    if not user:
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
