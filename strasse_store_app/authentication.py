import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from strasse_store_app.db_config import db_connection

blue_prints = Blueprint('authentication', __name__, url_prefix='/authentication')

# This view handles the seller registration on the CMS
@blue_prints.route('/registration', methods=('GET', 'POST'))
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_connect = db_connection()
        error = None

        if not username:
            error = 'The username is a required field.'
        elif not password:
            error = 'The password is a required field.'
        elif db_connect.execute('SELECT id from seller WHERE username = ?', (username,)).fetchone() is not None:
            error = 'The given username \"{}\" is already registered.'.format(username)

        if error is None:
            db_connect.execute(
                'INSERT INTO seller (username, password) VALUES ?,?', (username, generate_password_hash(password))
            )
            db_connect.commit()
            return redirect(url_for('authentication.login'))

        flash(error)

    return render_template('authentication/registration.html')


# This view handles the Login section of the CMS
@blue_prints.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_connect = db_connection()
        error = None
        seller = db_connect.execute('SELECT * FROM seller WHERE username = ?', (username,)).fetchone()

        if seller is None:
            error = 'The username is either not registered or incorrect. Please verify your entry and try again.'
        elif not check_password_hash(seller['password'], password):
            error = 'The password is incorrect. Please verify your entry and try again.'

        if error is None:
            session.clear()
            session['seller_id'] = seller['id']
            return redirect(url_for('homepage'))

        flash(error)

    return render_template('authentication/login.html')


# This view ensures that logged in user have their information made available to other views
@blue_prints.before_app_request()
def load_already_logged_in_sellers():
    seller_id = session.get('seller_id')
    if seller_id is None:
        g.seller = None
    else:
        g.seller = db_connection().execute(
            'SELECT * FROM seller WHERE id = ?', (seller_id,)).fetchone()

# This view is called when the seller logs out
@blue_prints.route('/logout')
def seller_logout():
    session.clear()
    return redirect(url_for('homepage'))


# This view is called to ensure that the seller are loggedin to perform some main functions
def login_is_required(view):
    @functools.wraps(view)
    def all_wrapped_view(**kwargs):
        if g.seller is None:
            return redirect(url_for('authentication.login'))
        return view(**kwargs)

    return all_wrapped_view
