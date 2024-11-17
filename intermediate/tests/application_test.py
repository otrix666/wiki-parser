import logging
from unittest.mock import call, create_autospec

import pytest

from intermediate.app.application import parse_wiki_page
from intermediate.app.db import Database
from intermediate.app.errors import CustomHTTPClientError
from intermediate.app.http_cli import HttpClient
from intermediate.app.redis_cli import RedisClient


@pytest.fixture
def database() -> Database:
    return create_autospec(Database)


@pytest.fixture
def logger() -> logging.Logger:
    return create_autospec(logging.Logger)


@pytest.fixture
def redis_cli() -> RedisClient:
    return create_autospec(RedisClient)


@pytest.fixture
def http_cli() -> HttpClient:
    return create_autospec(HttpClient)


def test_success_parse_wiki_page(database, logger, redis_cli, http_cli):
    http_cli.get_url_content.return_value = """
    <html>
        <body>
            <a href="/wiki/Programming">Programming</a>
        </body>
    </html>
    """
    redis_cli.get_saved_urls.return_value = set()

    urls = {"https://en.wikipedia.org/wiki/Python"}

    parse_wiki_page(
        logger=logger,
        db=database,
        redis_cli=redis_cli,
        http_cli=http_cli,
        urls=urls,
        max_depth=2,
        current_depth=1
    )

    database.add_urls.assert_any_call(urls=urls, depth=1)
    redis_cli.add_urls.assert_any_call(urls)

    http_cli.get_url_content.assert_has_calls([
        call(url="https://en.wikipedia.org/wiki/Python"),
        call(url="https://en.wikipedia.org/wiki/Programming")
    ])

    new_urls = {"https://en.wikipedia.org/wiki/Programming"}
    database.add_urls.assert_any_call(urls=new_urls, depth=2)
    redis_cli.add_urls.assert_any_call(new_urls)


def test_parse_wiki_page_http_error(database, logger, redis_cli, http_cli):
    http_cli.get_url_content.side_effect = CustomHTTPClientError("HTTP error")

    urls = {"https://en.wikipedia.org/wiki/Python"}

    parse_wiki_page(
        logger=logger,
        db=database,
        redis_cli=redis_cli,
        http_cli=http_cli,
        urls=urls,
        max_depth=2,
        current_depth=1
    )

    database.add_urls.assert_any_call(urls=urls, depth=1)
    redis_cli.add_urls.assert_any_call(urls)
    http_cli.get_url_content.assert_called_once_with(url="https://en.wikipedia.org/wiki/Python")
    logger.warning.assert_any_call("http client error: HTTP error")
