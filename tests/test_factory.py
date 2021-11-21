from TicketTracker import create_app

'''Check that app is not initialised in testing mode'''
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

'''Test that app initialised correctly'''
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'