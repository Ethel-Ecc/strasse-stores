import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from strasse_store_blog.database_store_blog import connect_to_store_blog_db


blueprint_store_blog = Blueprint('authentication_store_blog', __name__, url_prefix='/authentication')

# The registration route and view function
@blueprint_store_blog.route('/registration', methods=('GET', 'POST'))
def registration_store_blog():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connect_db = connect_to_store_blog_db()
        error = None

        if not username:
            error = 'None of the fields can be empty. please enter username/password'
        elif not password:
            error = 'None of the field can be empty. please enter the password/username'
        elif connect_db.execute('SELECT id FROM users_store_blog WHERE username = ?', (username,)).fetchone() is not None:
            error = 'The given username {} is already registered.'.format(username)

        if error is None:
            connect_db.execute('INSERT INTO users_store_blog (username, password) VALUES (?, ?)',
                               (username, generate_password_hash(password))
                               )
            connect_db.commit()

            return redirect(url_for('authentication_store_blog.login_store_blog'))

        flash(error)

    return render_template('authentication/registration.html')


# The login route and view function
@blueprint_store_blog.route('/login', methods=('GET', 'POST'))
def login_store_blog():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connect_db = connect_to_store_blog_db()
        error = None

        logged_in_user = connect_db.execute('SELECT * FROM users_store_blog WHERE username  = ?', (username,)).fetchone()

        if logged_in_user is None:
            error = 'The Username or Password is incorrect'
        elif not check_password_hash(logged_in_user['password'], password):
            error = 'The Username or password is incorrect.'

        if error is None:
            session.clear()
            session['logged_in_user_id'] = logged_in_user['id']

            return redirect(url_for('blog_store_blog.homepage'))

        flash(error)

    return render_template('authentication/login.html')


# This ensures that a logged in user session is transferred across all views
@blueprint_store_blog.before_app_request
def load_logged_in_user_sessions():

    logged_in_user_id = session.get('logged_in_user_id')

    if logged_in_user_id is None:
        g.logged_in_user = None
    else:
        g.logged_in_user = connect_to_store_blog_db().execute(
            'SELECT * FROM users_store_blog WHERE id = ? ', (logged_in_user_id,)
        ).fetchone()


# This logs out a user session entirely from all pages
@blueprint_store_blog.route('/logout')
def logout_user_sessions():

    session.clear()
    return redirect(url_for('homepage'))


# This ensures that login_requirements are met for all views
def user_login_required(view):
    @functools.wraps(view)
    def all_wrapped_views(**kwargs):

        if g.logged_in_user is None:
            return redirect(url_for('authentication_store_blog.login_store_blog'))

        return view(**kwargs)

    return all_wrapped_views
