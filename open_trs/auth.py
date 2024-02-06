import functools
import werkzeug.security

import flask

import open_trs.db


bp = flask.Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('POST', 'GET'))
def register():
    if flask.request.method == 'GET':
        return flask.render_template('auth/register.html')

    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']

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
            return flask.redirect(flask.url_for('auth.login'))

    # An error occurred
    flask.flash(error, 'error')
    return flask.render_template('auth/register.html')


@bp.route('/login', methods=('POST', 'GET'))
def login():
    if flask.request.method == 'GET':
        return flask.render_template('auth/login.html')

    username = flask.request.form['username']
    password = flask.request.form['password']

    db = open_trs.db.get_db()
    user = db.execute(
        'SELECT id, password FROM Users WHERE username = ?', (username,)).fetchone()

    error = None

    if not user:
        error = 'Incorrect username.'
    elif not werkzeug.security.check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        flask.session.clear()
        flask.session['user_id'] = user['id']

        return flask.redirect(flask.url_for('index'))

    # An error occurred
    flask.flash(error)
    return flask.render_template('auth/login.html')
