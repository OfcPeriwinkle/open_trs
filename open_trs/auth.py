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
    db = open_trs.db.get_db()

    error = None

    if not username:
        error = 'Uesrname is required'
    elif not email:
        error = 'Email is required'
    elif not password:
        error = 'Password is required'

    if error is None:
        try:
            db.execute('INSERT INTO Users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, werkzeug.security.generate_password_hash(password)))
            db.commit()
        except db.IntegrityError:
            error = f'Either user {username} or email {email} is already registered.'
        else:
            return flask.redirect(flask.url_for('auth.login'))

    if error:
        flask.flash(error, 'error')

    return flask.render_template('auth/register.html')
