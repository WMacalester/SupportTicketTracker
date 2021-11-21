import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from TicketTracker.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            admin = user["adminRights"]
            if not admin:          
                session.clear()
                session['user_id'] = user['id']
                session['adminRights'] = 0 #not sure if this is an appropriate way to set up whether the user is an admin for rest of the site
                return redirect(url_for('index'))
            if admin:
                session.clear()
                session['user_id'] = user['id']
                session['adminRights'] = 1 #not sure if this is an appropriate way to set up whether the user is an admin for rest of the site
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/updateAdminRights', methods=('GET', 'POST'))
@login_required
def updateAdminRights():
    adminRights = session.get('adminRights')
    if request.method == 'POST':
        username = request.form['username']
        newAdminRights = request.form['newAdminRights']
        
        '''If user has admin rights, attempt to update target user's adminRights.'''
        if adminRights:
            db = get_db()
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            '''Raise error if the target user does not exist, or if the user is trying to change their own adminRights.'''
            if user is None:
                error = f"User {username} is not registered."
            elif user["id"] == session.get("user_id"):
                error = "Do not try to change your own access rights."

            '''Try executing update'''
            if error is None:
                try:
                    db.execute(
                        'UPDATE user SET adminRights =? WHERE username = ?',
                        (newAdminRights, username)
                    )
                    db.commit()
                except db.IntegrityError:
                    #UPDATE THIS WHEN YOU UNDERSTAND WHAT INTEGRITY ERROR MEANS
                    error = f"Error updating admin rights for {username}. Please try again."
                else:
                    return redirect(url_for("index"))

            flash(error)
            
            pass
        else:
            flash("You do not have permission to view this.")
            return redirect(url_for('index'))
        

    return render_template('auth/updateAdminRights.html')

