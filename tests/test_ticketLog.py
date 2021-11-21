import pytest
from TicketTracker.db import get_db

'''Test that the index page and tickets are being displayed correctly for a user, using data from data.sql'''
def test_index_user(client, authUser):
    '''Test that there are links to Log In and Register when no user is logged in'''
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    'Test that when logged in, tickets are shown correctly and there is a button to log out'
    authUser.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Lon In' not in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    '''Check the user can edit their ticket.'''
    assert b'href="/1/update"' in response.data

'''Test that accessing create, update and delete without being logged in directs to login.'''
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required_user(app, client, authUser):
    '''change the post author to another user'''
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    authUser.login()
    '''current user can't modify other user's post'''
    assert client.post('/1/update').status_code == 403 #403 = forbidden
    assert client.post('/1/delete').status_code == 403
    '''current user doesn't see edit link'''
    assert b'href="/1/update"' not in client.get('/').data
    
'''Test if admins can see posts from all users'''
def test_author_not_required_admin(app, client, authAdmin):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    authAdmin.login()
    response = client.get('/')
    assert b'test title' in response.data
    assert b'by other on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    '''Check the admin can edit the ticket of another user.'''
    assert b'href="/1/update"' in response.data

'''Test if a non-existing entry returns 404'''
@pytest.mark.parametrize('path', ('/2/update','/2/delete',))
def test_exists_required(client, authUser, path):
    authUser.login()
    assert client.post(path).status_code == 404

'''Test if the create page works, and creates an entry in the database on post for a user.'''
def test_create_user(client, authUser, app):
    authUser.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': '',"ticket_status":"","adminBody":""})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2
        '''Confirm that ticket_status is set to "Submitted"'''
        assert db.execute('SELECT * FROM post WHERE id = 1').fetchone()["ticket_status"] == "Submitted"

'''Test if the create page works, and creates an entry in the database on post for an admin.'''        
def test_create_admin(client, authAdmin, app):
    authAdmin.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': '',"ticket_status":"","adminBody":""})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2
        '''Confirm that ticket_status is set to "Submitted"'''
        assert db.execute('SELECT * FROM post WHERE id = 1').fetchone()["ticket_status"] == "Submitted"

'''Testing that the update function is correctly changing the entries for the relevant ticket in the database.'''
def test_update_user(client, authUser, app):
    authUser.login()
    assert client.get('/1/update').status_code == 200
    '''Test that user can't see admin comments box if empty, and can't change ticket_status'''
    response = client.get('/1/update')
    assert b"Admin Comments" not in response.data
    assert b"disabled" in response.data
    client.post('/1/update', data={'title': 'updated', 'body': '',"ticket_status":"Submitted",})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'
        assert post['ticket_status'] == 'Submitted'
        assert post['adminBody'] == 'testAdminBody'

'''Testing that an error is stated if there is no title for a ticket when submitted'''
@pytest.mark.parametrize('path', ('/create','/1/update',))
def test_create_update_validate_title(client, authUser, path):
    authUser.login()
    response = client.post(path, data={'title': '', 'body': '',"ticket_status":"Submitted","adminBody":"",})
    assert b'Title is required.' in response.data
    
'''Test that an admin can modify the admin comments and the ticket_status'''
def test_update_admin(client, authAdmin, app):
    authAdmin.login()
    assert client.get('/1/update').status_code == 200
    response = client.get('/1/update')
    assert b"Admin Comments"  in response.data
    assert b"disabled" not in response.data
    client.post('/1/update', data={'title': 'updated', 'body': '',"ticket_status":"Completed","adminBody":"updated",})
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'
        assert post['ticket_status'] == 'Completed'
        assert post['adminBody'] == 'updated'
        
'''Testing that an error is stated if there is no ticket_status when update is submitted'''
def test_create_update_validate_ticket_status(client, authAdmin, app):
    authAdmin.login()
    response = client.post('/1/update', data={'title': 'testTitle', 'body': 'testBody',"ticket_status":"","adminBody":"",})
    assert b'Need to put ticket status.' in response.data
    '''Confirm the ticket has not been updated'''
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'test title'
        assert post['ticket_status'] == 'Submitted'
        assert post['adminBody'] == 'testAdminBody'

'''Testing that the delete function removes the ticket entry from the database and redirects to index.'''
def test_delete(client, authUser, app):
    authUser.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None