import logging
from concurrent.futures import (
    ProcessPoolExecutor,
)
from unittest.mock import create_autospec

import aiohttp
import pytest
from asyncpg import create_pool

from advanced.app.application import WikiCrawler, url_finder
from advanced.app.db import Database
from advanced.app.errors import DbError
from advanced.app.http_cli import HTTPClient


@pytest.fixture
def wiki_parser() -> WikiCrawler:
    return WikiCrawler(
        logger=create_autospec(logging.Logger),
        db=create_autospec(Database),
        process_pool=create_autospec(ProcessPoolExecutor),
        http_client=create_autospec(HTTPClient),
    )


@pytest.mark.asyncio
async def test_success_add_urls(wiki_parser: WikiCrawler) -> None:
    result = await wiki_parser._add_urls_to_db(urls={"http://wiki.test.com"}, current_depth=1)
    wiki_parser._db.add_urls.assert_called_once_with({"http://wiki.test.com"}, 1)
    assert result is True


@pytest.mark.asyncio
async def test_failure_add_urls(wiki_parser: WikiCrawler) -> None:
    wiki_parser._db.add_urls.side_effect = DbError()
    result = await wiki_parser._add_urls_to_db(urls={"http://wiki.test.com"}, current_depth=1)
    wiki_parser._db.add_urls.assert_called_once_with({"http://wiki.test.com"}, 1)
    assert result is False


@pytest.mark.asyncio
async def test_success_get_html_content(wiki_parser: WikiCrawler) -> None:
    test_url = {"http://wiki.test.com"}
    content = """<html>
            <body>
                <a href="/wiki/Programming">Programming</a>
            </body>
        </html>"""

    wiki_parser._http_client.get_content.return_value = content

    result = await wiki_parser._get_html_contents(urls=test_url)
    assert result == {content}


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
def test_success_url_finder(wiki_parser: WikiCrawler, content: str, expected_result: set[str]) -> None:
    result = url_finder(content=content)
    assert result == expected_result


@pytest.mark.asyncio
async def test_success_run():
    logger = logging.getLogger(__name__)

    async with create_pool(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        database="test",
        password="admin",
        min_size=10,
        max_size=10,
    ) as pool:
        db = Database(pool=pool)
        await db.create_table()
        await db.clear_urls()

        process_pool = ProcessPoolExecutor(max_workers=4)
        session = aiohttp.ClientSession()
        http_client = HTTPClient(session=session)

        parser = WikiCrawler(
            logger=logger,
            db=db,
            process_pool=process_pool,
            http_client=http_client,
        )

        await parser.run(urls={"https://en.wikipedia.org/wiki/Mark_T._Vande_Hei"}, max_depth=2)

        async with pool.acquire() as connection:
            result = await connection.fetch("SELECT count(*) from urls")
            count = result[0][0]
            assert 1000 < count < 2000
