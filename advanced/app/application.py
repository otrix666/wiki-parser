import asyncio
import re
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from logging import Logger
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from advanced.app.db import Database
from advanced.app.errors import DbError
from advanced.app.http_cli import HTTPClient

URL_PATTERN = re.compile(r"^/wiki/(?!.*\.(?:png|jpg|gif|pdf|svg|mp4)).*$")


class WikiCrawler:
    def __init__(
        self,
        logger: Logger,
        db: Database,
        process_pool: ProcessPoolExecutor,
        http_client: HTTPClient,
    ) -> None:
        self._logger = logger
        self._db = db
        self._process_pool = process_pool
        self._http_client = http_client

    async def run(self, urls: set[str], max_depth: int, current_depth: int = 1) -> None:
        if not await self._add_urls_to_db(urls, current_depth):
            return

        if current_depth >= max_depth:
            return

        html_contents = await self._get_html_contents(urls)
        next_urls = await self._process_html_contents(html_contents)

        await self.run(next_urls, max_depth, current_depth + 1)

    async def _add_urls_to_db(self, urls: set[str], current_depth: int) -> bool:
        try:
            await self._db.add_urls(urls=urls, depth=current_depth)
            return True
        except DbError:
            self._logger.exception("db Error")
            return False

    async def _get_html_contents(self, urls: set[str]) -> set[str]:
        html_contents = set()
        tasks = [self._http_client.get_content(url) for url in urls]
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                html_contents.add(result)

        return html_contents

    async def _process_html_contents(self, html_contents: set[str]) -> set[str]:
        loop = asyncio.get_running_loop()
        calls = [partial(url_finder, content) for content in html_contents]
        results = await asyncio.gather(*(loop.run_in_executor(self._process_pool, call) for call in calls))

        all_urls = {url for urls in results for url in urls}
        new_urls = all_urls - await self._db.get_urls()

        return new_urls


def url_finder(content: str) -> set[str]:
    urls = set()
    soup = BeautifulSoup(content, "lxml")
    for url in soup.find_all("a", href=URL_PATTERN):
        href = url.get("href", "")
        if href:
            full_url = urljoin("https://en.wikipedia.org", href)
            urls.add(full_url)
    return urls
