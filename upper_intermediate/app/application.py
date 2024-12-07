import re
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from logging import Logger
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from upper_intermediate.app.db import Database
from upper_intermediate.app.errors import DbError, EncodeError, HttpError
from upper_intermediate.app.http_cli import HttpClient


class WikiParser:
    def __init__(
        self,
        logger: Logger,
        db: Database,
        thread_pool: ThreadPoolExecutor,
        process_pool: ProcessPoolExecutor,
        http_client: HttpClient,
    ) -> None:
        self._logger = logger
        self._db = db
        self._thread_pool = thread_pool
        self._process_pool = process_pool
        self._http_client = http_client

    def run(self, urls: set[str], max_depth: int, current_depth: int = 1) -> None:
        if not self._add_urls_to_db(urls, current_depth):
            return

        if current_depth >= max_depth:
            return

        html_contents = self._get_html_contents(urls)
        next_urls = self._process_html_contents(html_contents)

        self.run(next_urls, max_depth, current_depth + 1)

    def _add_urls_to_db(self, urls: set[str], current_depth: int) -> bool:
        future = self._thread_pool.submit(self._db.add_urls, urls, current_depth)
        try:
            future.result()
            self._logger.info(f"added urls to db: {urls} (depth: {current_depth})")
            return True
        except DbError:
            self._logger.exception("db Error")
            return False

    def _get_html_contents(self, urls: set[str]) -> set[str]:
        html_contents = set()
        futures = [self._thread_pool.submit(self._http_client.get_url_content, url) for url in urls]
        for future in as_completed(futures):
            try:
                html_contents.add(future.result())
            except HttpError as e:
                self._logger.warning(f"HTTP Error: {e}")
            except EncodeError as e:
                self._logger.warning(f"Encoding Error: {e}")
            except Exception as e:
                self._logger.warning(f"Unknown error while fetching content: {e}")
        return html_contents

    def _process_html_contents(self, html_contents: set[str]) -> set[str]:
        pages_urls = self._process_pool.map(self.url_finder, html_contents)
        all_urls = {url for urls in pages_urls for url in urls}
        new_urls = all_urls - self._db.get_urls()
        return new_urls

    @staticmethod
    def url_finder(content: str) -> set[str]:
        urls = set()
        url_pattern = re.compile(r"^/wiki/(?!.*\.(?:png|jpg|gif|pdf|svg|mp4)).*$")
        soup = BeautifulSoup(content, "lxml")
        for url in soup.find_all("a", href=url_pattern):
            href = url.get("href", "")
            if href:
                full_url = urljoin("https://en.wikipedia.org", href)
                urls.add(full_url)
        return urls
