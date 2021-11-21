import pytest
from flask import g, session
from TicketTracker.db import get_db

'''Testing that the register view is successfully rendered on GET. Redirect to login URL on POST with valid data, and user's data added to database.'''
def test_register(client, app):
    '''Test that GET for /auth/register is successful.'''
    assert client.get('/auth/register').status_code == 200 #NB 200 = successful request. Failed rendering would give 500 Internal Server Error.
    
    '''Test that posting a valid username and password will redirect to the login page.'''
    response = client.post('/auth/register', data={'username': 'a', 'password': 'a'})
    assert 'http://localhost/auth/login' == response.headers['Location']

    '''Test that the user has been added to the database, and that they are set to not have adminRights by default.'''
    with app.app_context():
        testUser = get_db().execute("SELECT * FROM user WHERE username = 'a'",).fetchone()
        assert testUser is not None
        assert testUser["adminRights"] == 0

'''Check that error messages if either username or password are missing, or if a user is already registered are correct.
pytest.mark.parametrize runs the same function multiple times with different arguments, allowing for testing of multiple entry sets.'''
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'), #What does the b do?
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post('/auth/register',data={'username': username, 'password': password})
    assert message in response.data

'''Test that login is successfully rendered, and that posting will call the login function. Then test that there is a redirection to /'''
def test_login_user(client, authUser):
    assert client.get('/auth/login').status_code == 200
    response = authUser.login()
    assert response.headers['Location'] == 'http://localhost/'

    '''Test that the session data is correct for the user. 
    "Using client in a with block allows accessing context variables such as session after the response is returned. Normally, accessing session outside of a request would raise an error."'''
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'
        
def test_login_admin(client, authAdmin):
    assert client.get('/auth/login').status_code == 200
    response = authAdmin.login()
    assert response.headers['Location'] == 'http://localhost/'

    '''Test that the session data is correct for the user. 
    "Using client in a with block allows accessing context variables such as session after the response is returned. Normally, accessing session outside of a request would raise an error."'''
    with client:
        client.get('/')
        assert g.user['username'] == 'adminTest'
        assert g.user['adminRights'] == 1

'''Test that both username and password are correctly validated.'''
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(authUser, username, password, message):
    response = authUser.login(username, password)
    assert message in response.data

'''Test that users are no longer in session after logging out'''
def test_logout(client, authUser):
    authUser.login()

    with client:
        authUser.logout()
        assert 'user_id' not in session

'''Test that adminRights are correctly updated in database'''
def test_updateAdminRights(client, app, authAdmin):
    authAdmin.login()
    assert client.get('http://localhost/auth/updateAdminRights').status_code == 200
    response = client.post('/auth/updateAdminRights', data={'username': 'other', 'newAdminRights': '1'})
    with app.app_context():
        assert get_db().execute("SELECT adminRights FROM user WHERE username = 'other'",).fetchone()["adminRights"] == 1
    

'''Test that users can't change adminRights'''
def test_updateAdminRights_user_login(client, app, authUser):
    authUser.login()
    response = client.post('/auth/updateAdminRights', data={'username': 'other', 'newAdminRights': '1'})
    '''confirm that adminRights was not changed'''
    with app.app_context():
        assert get_db().execute("SELECT adminRights FROM user WHERE username = 'other'",).fetchone()["adminRights"] == 0
    



@pytest.mark.parametrize(('username', 'message'), (
    ('t', b'User t is not registered.'), #What does the b do?
    ('adminTest', b'Do not try to change your own access rights.'),
))        
def test_updateAdminRights_validate_input(client, authAdmin, username, message):
    authAdmin.login()
    response = client.post('/auth/updateAdminRights', data={'username': username, 'newAdminRights': '1'})
    assert message in response.data