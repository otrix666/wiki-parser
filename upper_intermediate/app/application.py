from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from logging import Logger

from upper_intermediate.app.db import Database
from upper_intermediate.app.errors import (
    DbError,
    EncodeError,
    HttpError
)
from upper_intermediate.app.http_cli import HttpClient
from upper_intermediate.app.utils import url_finder


class WikiParser:
    def __init__(
            self,
            logger: Logger,
            db: Database,
            thread_pool: ThreadPoolExecutor,
            process_pool: ProcessPoolExecutor,
            http_client: HttpClient,
    ) -> None:
        self.logger = logger
        self.db = db
        self.thread_pool = thread_pool
        self.process_pool = process_pool
        self.http_client = http_client

    def run(self,
            urls: set[str],
            max_depth: int) -> None:

        self.parse_wiki_page(urls, max_depth, current_depth=1)

    def parse_wiki_page(self,
                        urls: set[str],
                        max_depth: int,
                        current_depth: int) -> None:
        if not self.add_urls_to_db(urls, current_depth):
            return

        if current_depth >= max_depth:
            return

        html_contents = self.get_html_contents(urls)
        next_urls = self.process_html_contents(html_contents)

        self.parse_wiki_page(next_urls, max_depth, current_depth + 1)

    def add_urls_to_db(self,
                       urls: set[str],
                       current_depth: int) -> bool:
        future = self.thread_pool.submit(self.db.add_urls, urls, current_depth)
        try:
            future.result()
            self.logger.info(f"added urls to db: {urls} (depth: {current_depth})")
            return True
        except DbError as e:
            self.logger.error(f"db Error: {e}")
            return False

    def get_html_contents(self, urls: set[str]) -> set[str]:
        html_contents = set()
        futures = [
            self.thread_pool.submit(
                self.http_client.get_url_content, url
            ) for url in urls
        ]
        for future in as_completed(futures):
            try:
                html_contents.add(future.result())
            except HttpError as e:
                self.logger.warning(f"HTTP Error: {e}")
            except EncodeError as e:
                self.logger.warning(f"Encoding Error: {e}")
            except Exception as e:
                self.logger.warning(f"Unknown error while fetching content: {e}")
        return html_contents

    def process_html_contents(self, html_contents: set[str]) -> set[str]:
        pages_urls = self.process_pool.map(url_finder, html_contents)
        all_urls = {url for urls in pages_urls for url in urls}
        new_urls = all_urls - self.db.get_urls()
        return new_urls
