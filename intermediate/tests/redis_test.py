from unittest.mock import MagicMock

import pytest
from redis.exceptions import ConnectionError

from intermediate.app.errors import CustomRedisError
from intermediate.app.redis_cli import RedisClient


@pytest.fixture
def connection_fixture():
    return MagicMock()


@pytest.fixture
def redis_client_fixture(connection_fixture):
    redis_client = RedisClient(connection_fixture)
    return redis_client


def test_success_add_urls(connection_fixture, redis_client_fixture):
    urls = {"https://en.wiki.org0", "https://en.wiki.org1"}

    redis_client_fixture.add_urls(urls=urls)
    connection_fixture.sadd.assert_called_once_with("saved_urls", *urls)


def test_failure_add_urls(connection_fixture, redis_client_fixture):
    connection_fixture.sadd.side_effect = ConnectionError

    urls = {"https://example.com", "https://example.org"}
    with pytest.raises(CustomRedisError):
        redis_client_fixture.add_urls(urls)


def test_success_get_saved_urls(connection_fixture, redis_client_fixture):
    connection_fixture.smembers.return_value = {b"https://en.wiki.org0", b"https://en.wiki.org1"}

    result = redis_client_fixture.get_saved_urls()
    connection_fixture.smembers.assert_called_once_with("saved_urls")
    assert result == {"https://en.wiki.org0", "https://en.wiki.org1"}


def test_failure_get_saved_urls(connection_fixture, redis_client_fixture):
    connection_fixture.smembers.side_effect = ConnectionError

    with pytest.raises(CustomRedisError):
        redis_client_fixture.get_saved_urls()


def test_success_clear_urls(connection_fixture, redis_client_fixture):
    redis_client_fixture.clear_urls()
    connection_fixture.delete.assert_called_once_with("saved_urls")


def test_failure_clear_urls(connection_fixture, redis_client_fixture):
    connection_fixture.delete.side_effect = ConnectionError

    with pytest.raises(CustomRedisError):
        redis_client_fixture.clear_urls()
