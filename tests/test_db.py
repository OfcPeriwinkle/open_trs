import sqlite3

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner

import open_trs.db


def test_get_close_db(app: Flask):
    with app.app_context():
        db = open_trs.db.get_db()
        assert db is open_trs.db.get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner: FlaskCliRunner, monkeypatch: pytest.MonkeyPatch):
    class Recorder:
        called = False

    def mock_init_db():
        Recorder.called = True

    monkeypatch.setattr('open_trs.db.init_db', mock_init_db)
    result = runner.invoke(args=['init-db'])

    assert 'Initialized' in result.output
    assert Recorder.called
