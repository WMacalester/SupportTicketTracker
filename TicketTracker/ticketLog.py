from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.exceptions import abort

from TicketTracker.auth import login_required
from TicketTracker.db import get_db

bp = Blueprint('ticketLog', __name__)

@bp.route('/')
def index():
    db = get_db()
    adminRights = session.get("adminRights")
    id = session.get('user_id')
    if adminRights:
        '''Admins can view all posts'''
        posts = db.execute( 
            'SELECT p.id, title, body, ticket_status, created, author_id, username, adminBody'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()

        return render_template('ticketLog/admin/index.html', posts=posts)

    if not adminRights:
        '''Users can only view their own tickets if not an admin'''
        posts = db.execute(
        'SELECT p.id, title, body, ticket_status, created, author_id, username, adminBody'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC',([id]) #needs to be in a list for some reason
        ).fetchall()

        return render_template('ticketLog/user/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('ticketLog.index'))
            
    '''Separate destination between admins and users'''
    adminRights = session.get("adminRights")
    if adminRights:
        return render_template('ticketLog/admin/create.html')
    if not adminRights:
        return render_template('ticketLog/user/create.html')

def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, ticket_status, adminBody'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    adminRights = session.get("adminRights")

    '''Prevent non-admin users from editing other users post if they are able to view them for some reason.'''
    if not adminRights and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)   
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        ticket_status = request.form['ticket_status']
        '''If adminBody is not changed, then keep as it is. Necessary as users do not have access to admin comments in update'''
        try:
            adminBody = request.form['adminBody']
        except:
            adminBody = post["adminBody"]
        error = None

        if not title:
            error = 'Title is required.'

        if ticket_status != "Submitted" and  ticket_status != "In Progress" and ticket_status != "Completed":
            error = "Need to put ticket status." #Shouldn't occur as radio buttons for ticket status initialise as checked.

        if error is not None:
            flash(error)
        else:           
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, ticket_status = ?, adminBody = ?'
                ' WHERE id = ?',
                (title, body, ticket_status, adminBody, id)
            )
            db.commit()
            return redirect(url_for('ticketLog.index'))

    '''Separate destination between admins and users'''
    adminRights = session.get("adminRights")
    if adminRights:
        return render_template('ticketLog/admin/update.html', post=post)
    elif not adminRights:
        return render_template('ticketLog/user/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('ticketLog.index'))

