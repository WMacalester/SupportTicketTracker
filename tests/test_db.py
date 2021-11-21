import sqlite3
import pytest
from TicketTracker.db import get_db


def test_get_close_db(app):
    '''Check that the database is the same each time that it is called'''
    with app.app_context():
        db = get_db()
        assert db is get_db()

    '''Check that database closes after it has been used'''
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

'''Check that the init_db command calls the init_db function and outputs the message "Initialized" to the command line.'''
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    '''Creating a record that says init_db has been called'''
    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('TicketTracker.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called