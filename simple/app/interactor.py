import  logging
from typing import  TypeVar, Callable, Iterable
from collections import deque

from simple.app.db import  Database
from simple.app.errors import CustomDbError, CustomParserError
from simple.app.parser import WikiClient


fetch_util = TypeVar("fetch_util", bound=Callable[..., Iterable[str]])

def parse_wikipedia_page(logger: logging.Logger,
                         db: Database,
                         wiki_client: WikiClient,
                         urls_fetcher: fetch_util,
                         url: str,
                         max_depth: int = 3
) -> None:
    insert_values = set()
    already_uploaded_urls = set()

    last_depth = 0
    queue = deque([(url, 1)])

    while queue:
        current_url, current_depth = queue.popleft()

        if current_depth > max_depth:
            return

        insert_values.add((current_url, current_depth))

        if current_depth > last_depth:
            last_depth = current_depth
            try:
                db.add_urls(insert_values=insert_values)
                logger.info(f"added links: {insert_values} depth {current_depth}")
                insert_values.clear()
            except CustomDbError:
                logger.error(f"db error")

        try:
            html_content  = wiki_client.get_url_content(url=current_url)
        except CustomParserError:
            logging.error("parser error")
            continue

        urls = urls_fetcher(html_content=html_content)
        already_uploaded_urls.add(current_url)
        logger.info(urls)

        for next_url in urls:
            queue.append((next_url, current_depth + 1))
