from unittest.mock import MagicMock, call

import pytest
from psycopg.errors import ConnectionFailure

from upper_intermediate.app.db import Database
from upper_intermediate.app.errors import DbError


@pytest.fixture
def cursor_fixture():
    return MagicMock()


@pytest.fixture
def connection_fixture(cursor_fixture):
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor_fixture
    connection.__enter__.return_value = connection
    return connection


@pytest.fixture
def pool_fixture(connection_fixture):
    pool = MagicMock()
    pool.connection.return_value.__enter__.return_value = connection_fixture
    return pool


@pytest.fixture
def database_fixture(pool_fixture):
    return Database(pool=pool_fixture)


def test_success_clear_urls(database_fixture, connection_fixture, cursor_fixture):
    database_fixture.clear_urls()

    cursor_fixture.execute.assert_called_once_with("DELETE FROM urls")
    connection_fixture.commit.assert_called_once()


def test_failure_clear_urls(database_fixture, connection_fixture, cursor_fixture):
    cursor_fixture.execute.side_effect = ConnectionFailure()

    with pytest.raises(DbError):
        database_fixture.clear_urls()

    cursor_fixture.execute.assert_called_once_with("DELETE FROM urls")
    connection_fixture.commit.assert_not_called()


def test_success_add_urls(database_fixture, connection_fixture, cursor_fixture):
    urls = {"https://wiki.org123"}
    depth = 1

    database_fixture.add_urls(urls=urls, depth=depth)

    assert cursor_fixture.executemany.call_args == call(
        "INSERT INTO urls(url, depth) VALUES (%s, %s)",
        [("https://wiki.org123", 1)],
    )
    connection_fixture.commit.assert_called_once()


def test_failure_add_urls(database_fixture, connection_fixture, cursor_fixture):
    urls = {"https://wiki.org123"}
    depth = 1

    cursor_fixture.executemany.side_effect = ConnectionFailure()

    with pytest.raises(DbError):
        database_fixture.add_urls(urls=urls, depth=depth)

    assert cursor_fixture.executemany.call_args == call(
        "INSERT INTO urls(url, depth) VALUES (%s, %s)",
        [("https://wiki.org123", 1)],
    )
    connection_fixture.commit.assert_not_called()
