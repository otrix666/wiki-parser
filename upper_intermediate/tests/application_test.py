import logging
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from unittest.mock import MagicMock, create_autospec, patch

import pytest
import requests
from psycopg_pool import ConnectionPool

from upper_intermediate.app.application import WikiParser
from upper_intermediate.app.db import Database
from upper_intermediate.app.errors import DbError, EncodeError, HttpError
from upper_intermediate.app.http_cli import HttpClient


@pytest.fixture
def wiki_parser() -> WikiParser:
    return WikiParser(
        logger=create_autospec(logging.Logger),
        db=create_autospec(Database),
        thread_pool=create_autospec(ThreadPoolExecutor),
        process_pool=create_autospec(ProcessPoolExecutor),
        http_client=create_autospec(HttpClient),
    )


def test_success_add_urls(wiki_parser: WikiParser) -> None:
    result = wiki_parser._add_urls_to_db(urls={"http://wiki.test.com"}, current_depth=1)
    wiki_parser._thread_pool.submit.assert_called_once_with(wiki_parser._db.add_urls, {"http://wiki.test.com"}, 1)
    wiki_parser._thread_pool.submit.return_value.result.assert_called_once()
    assert result is True


def test_failed_add_urls(wiki_parser: WikiParser) -> None:
    wiki_parser._thread_pool.submit.return_value.result = MagicMock(side_effect=DbError)
    result = wiki_parser._add_urls_to_db(urls={"http://wiki.test.com"}, current_depth=1)
    wiki_parser._thread_pool.submit.assert_called_once_with(wiki_parser._db.add_urls, {"http://wiki.test.com"}, 1)
    wiki_parser._thread_pool.submit.return_value.result.assert_called_once()
    assert result is False


def test_success_get_html_content(wiki_parser: WikiParser) -> None:
    test_url = "http://wiki.test.com"
    content = """<html>
        <body>
            <a href="/wiki/Programming">Programming</a>
        </body>
    </html>"""

    mock_future = wiki_parser._thread_pool.submit.return_value = MagicMock()
    mock_future.result.return_value = content

    with patch("upper_intermediate.app.application.as_completed", return_value=[mock_future]) as as_completed:
        result = wiki_parser._get_html_contents(urls={test_url})

        wiki_parser._thread_pool.submit.assert_called_once_with(wiki_parser._http_client.get_url_content, test_url)

        mock_future.result.assert_called_once()
        assert result == {content}


def test_failed_get_html_content_http_error(wiki_parser: WikiParser) -> None:
    test_url = "http://wiki.test.com"

    mock_future = wiki_parser._thread_pool.submit.return_value = MagicMock()
    mock_future.result.side_effect = HttpError("http error")

    with patch("upper_intermediate.app.application.as_completed", return_value=[mock_future]) as as_completed:
        result = wiki_parser._get_html_contents(urls={test_url})

        wiki_parser._thread_pool.submit.assert_called_once_with(wiki_parser._http_client.get_url_content, test_url)

        mock_future.result.assert_called_once()
        wiki_parser._logger.warning.assert_called_with("HTTP Error: http error")

        assert result == set()


def test_failed_get_html_content_encode_error(wiki_parser: WikiParser) -> None:
    test_url = "http://wiki.test.com"

    mock_future = wiki_parser._thread_pool.submit.return_value = MagicMock()
    mock_future.result.side_effect = EncodeError("encoding error")

    with patch("upper_intermediate.app.application.as_completed", return_value=[mock_future]) as as_completed:
        result = wiki_parser._get_html_contents(urls={test_url})

        wiki_parser._thread_pool.submit.assert_called_once_with(wiki_parser._http_client.get_url_content, test_url)

        mock_future.result.assert_called_once()

        wiki_parser._logger.warning.assert_called_with("Encoding Error: encoding error")
        assert result == set()


def test_failed_get_html_content_unknown_error(wiki_parser: WikiParser) -> None:
    test_url = "http://wiki.test.com"

    mock_future = wiki_parser._thread_pool.submit.return_value = MagicMock()
    mock_future.result.side_effect = Exception("smth error")

    with patch("upper_intermediate.app.application.as_completed", return_value=[mock_future]) as as_completed:
        result = wiki_parser._get_html_contents(urls={test_url})

        wiki_parser._thread_pool.submit.assert_called_once_with(wiki_parser._http_client.get_url_content, test_url)

        mock_future.result.assert_called_once()

        wiki_parser._logger.warning.assert_called_with("Unknown error while fetching content: smth error")
        assert result == set()


@pytest.mark.parametrize(
    "content, expected_result",
    [
        (
            """<html>
                    <body>
                        <a href="/wiki/Programming">Programming</a>
                    </body>
                </html>""",
            {"https://en.wikipedia.org/wiki/Programming"},
        ),
        (
            """<html>
                    <body>
                        <a href="/wiki/Software">Software</a>
                        <a href="/wiki/Hardware">Hardware</a>
                    </body>
                </html>""",
            {"https://en.wikipedia.org/wiki/Software", "https://en.wikipedia.org/wiki/Hardware"},
        ),
        (
            """<html>
                    <body>
                        <a href="/wiki/Python_(programming_language)">Python</a>
                        <a href="/wiki/JavaScript">JavaScript</a>
                    </body>
                </html>""",
            {"https://en.wikipedia.org/wiki/Python_(programming_language)", "https://en.wikipedia.org/wiki/JavaScript"},
        ),
    ],
)
def test_success_url_finder(wiki_parser: WikiParser, content: str, expected_result: set[str]) -> None:
    result = wiki_parser.url_finder(content=content)
    assert result == expected_result


def test_success_run():
    logger = logging.getLogger(__name__)
    db_url = "postgresql://postgres:admin@127.0.0.1:5432/test"
    with ConnectionPool(db_url, max_size=10) as pool:
        db = Database(pool=pool)
        db.create_table()
        db.clear_urls()

        thread_pool = ThreadPoolExecutor(max_workers=8)
        process_pool = ProcessPoolExecutor(max_workers=4)
        http_client = HttpClient(client=requests.get)

        parser = WikiParser(
            logger=logger, db=db, thread_pool=thread_pool, process_pool=process_pool, http_client=http_client
        )

        parser.run(urls={"https://en.wikipedia.org/wiki/Mark_T._Vande_Hei"}, max_depth=2)

        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM urls")
                assert 1000 < cursor.fetchone()[0] < 2000
