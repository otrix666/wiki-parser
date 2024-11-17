from unittest.mock import MagicMock, call

import pytest
from intermediate.app.db import Database
from intermediate.app.errors import CustomDbError
from psycopg.errors import ConnectionFailure


@pytest.fixture
def cursor_fixture():
    return MagicMock()


@pytest.fixture
def connection_fixture(cursor_fixture):
    connection = MagicMock()
    connection.cursor.return_value = cursor_fixture
    return connection


@pytest.fixture
def database_fixture(connection_fixture):
    database = Database(connection_fixture)
    return database


def test_success_clear_urls(cursor_fixture, connection_fixture, database_fixture):
    database_fixture.clear_urls()
    connection_fixture.cursor.assert_called_once()
    cursor_fixture.execute.assert_called_once_with("DELETE FROM urls")
    connection_fixture.commit.assert_called_once()
    cursor_fixture.close.assert_called_once()


def test_failure_clear_urls(cursor_fixture, connection_fixture, database_fixture):
    cursor_fixture.execute.side_effect = ConnectionFailure

    with pytest.raises(CustomDbError):
        database_fixture.clear_urls()

    connection_fixture.cursor.assert_called_once()
    cursor_fixture.close.assert_called_once()


def test_success_add_urls(cursor_fixture, connection_fixture, database_fixture):
    urls = {"https://wiki.org123", "https://wiki.org1234", "https://wiki.org1245"}
    depth = 1

    database_fixture.add_urls(urls=urls, depth=depth)

    connection_fixture.cursor.assert_called_once()
    assert (cursor_fixture.executemany.call_args,
            call('INSERT OR REPLACE INTO urls(url, depth) VALUES (%s, %2)',
                 [('https://wiki.org1245', 1), ('https://wiki.org1234', 1), ('https://wiki.org123', 1)]))

    connection_fixture.commit.assert_called()
    cursor_fixture.close.assert_called()


def test_failure_add_urls(cursor_fixture, connection_fixture, database_fixture):
    cursor_fixture.executemany.side_effect = ConnectionFailure

    urls = {"https://wiki.org123", "https://wiki.org1234", "https://wiki.org1245"}
    depth = 1

    with pytest.raises(CustomDbError):
        database_fixture.add_urls(urls=urls, depth=depth)

    connection_fixture.cursor.assert_called_once()
    cursor_fixture.close.assert_called()
