from unittest.mock import AsyncMock

import pytest
from asyncpg import Connection, Pool

from advanced.app.db import Database
from advanced.app.errors import DbError


@pytest.fixture()
def connection_fixture():
    connection = AsyncMock(spec=Connection)
    connection.transaction.return_value.__aenter__.return_value = connection
    connection.transaction.return_value.__aexit__.return_value = None
    connection.fetch = AsyncMock()
    connection.execute = AsyncMock()

    return connection


@pytest.fixture
def pool_fixture(connection_fixture):
    mock_pool = AsyncMock(spec=Pool)
    mock_pool.acquire.return_value.__aenter__.return_value = connection_fixture
    mock_pool.acquire.return_value.__aexit__.return_value = None

    return mock_pool


@pytest.fixture
def database_fixture(pool_fixture):
    return Database(pool=pool_fixture)


@pytest.mark.asyncio
async def test_success_clear_urls(database_fixture, pool_fixture, connection_fixture):
    await database_fixture.clear_urls()
    pool_fixture.acquire.assert_called_once()
    connection_fixture.execute.assert_called_once_with("DELETE FROM urls")


@pytest.mark.asyncio
async def test_failure_clear_urls(database_fixture, pool_fixture, connection_fixture):
    connection_fixture.execute.side_effect = ConnectionError()

    with pytest.raises(DbError):
        await database_fixture.clear_urls()
    pool_fixture.acquire.assert_called_once()
    connection_fixture.execute.assert_called_once_with("DELETE FROM urls")


@pytest.mark.asyncio
async def test_success_add_urls(database_fixture, pool_fixture, connection_fixture):
    urls = {"https://wiki.org123"}
    depth = 1

    await database_fixture.add_urls(urls=urls, depth=depth)
    pool_fixture.acquire.assert_called_once()
    connection_fixture.transaction.assert_called_once()
    connection_fixture.executemany.assert_called_once_with(
        "INSERT INTO urls(url, depth) VALUES ($1, $2) ON CONFLICT (url) DO NOTHING", [("https://wiki.org123", 1)]
    )


@pytest.mark.asyncio
async def test_success_add_urls(database_fixture, pool_fixture, connection_fixture):
    urls = {"https://wiki.org123"}
    depth = 1

    await database_fixture.add_urls(urls=urls, depth=depth)
    pool_fixture.acquire.assert_called_once()
    connection_fixture.transaction.assert_called_once()
    connection_fixture.executemany.assert_called_once_with(
        "INSERT INTO urls(url, depth) VALUES ($1, $2) ON CONFLICT (url) DO NOTHING", [("https://wiki.org123", 1)]
    )


@pytest.mark.asyncio
async def test_failure_add_urls(database_fixture, pool_fixture, connection_fixture):
    urls = {"https://wiki.org123"}
    depth = 1

    connection_fixture.executemany.side_effect = ConnectionError()

    with pytest.raises(DbError):
        await database_fixture.add_urls(urls=urls, depth=depth)

    pool_fixture.acquire.assert_called_once()
    connection_fixture.transaction.assert_called_once()
    connection_fixture.executemany.assert_called_once_with(
        "INSERT INTO urls(url, depth) VALUES ($1, $2) ON CONFLICT (url) DO NOTHING", [("https://wiki.org123", 1)]
    )


@pytest.mark.asyncio
async def test_success_get_urls(database_fixture, pool_fixture, connection_fixture):
    connection_fixture.fetch.return_value = [{"url": "http://example.com"}, {"url": "http://example.org"}]
    result = await database_fixture.get_urls()

    pool_fixture.acquire.assert_called_once()
    connection_fixture.fetch.assert_called_once_with("SELECT url FROM urls")

    assert result == {"http://example.com", "http://example.org"}


@pytest.mark.asyncio
async def test_failure_get_urls(database_fixture, pool_fixture, connection_fixture):
    connection_fixture.fetch.side_effect = ConnectionError()

    with pytest.raises(DbError):
        await database_fixture.get_urls()

    pool_fixture.acquire.assert_called_once()
    connection_fixture.fetch.assert_called_once_with("SELECT url FROM urls")
