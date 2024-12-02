from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
)
from logging import Logger

from upper_intermediate.app.db import Database
from upper_intermediate.app.errors import (
    CustomHTTPClientError,
    CustomRedisError,
    CustomDbError
)
from upper_intermediate.app.http_cli import HttpClient
from upper_intermediate.app.redis_cli import RedisClient
from upper_intermediate.app.utils import url_finder


def parse_wiki_page(
        logger: Logger,
        db: Database,
        redis_cli: RedisClient,
        http_cli: HttpClient,
        urls: set[str],
        max_depth: int,
        current_depth: int = 1
) -> None:
    if current_depth > max_depth:
        return

    try:
        db.add_urls(urls=urls, depth=current_depth)
        logger.info(f"added urls to pg: {urls} {current_depth}")
    except CustomDbError as e:
        return logger.error(f"db error: {e}")

    try:
        redis_cli.add_urls(urls)
    except CustomRedisError as e:
        return logger.error(f"redis error: {e}")

    html_contents = set()

    with ThreadPoolExecutor() as thread_pool:
        futures = [thread_pool.submit(http_cli.get_url_content, url) for url in urls]
        done_iter = as_completed(futures)
        for future in done_iter:
            try:
                html_contents.add(future.result())
            except CustomHTTPClientError as e:
                logger.warning(f"http client error: {e}")
            except Exception as e:
                logger.warning(f"Unknown error while parsing: {e}")

    with ProcessPoolExecutor() as process_pool:
        pages_urls = process_pool.map(url_finder, html_contents)

    next_urls = {url for urls in pages_urls for url in urls}
    next_urls -= redis_cli.get_saved_urls()

    parse_wiki_page(logger=logger,
                    db=db,
                    redis_cli=redis_cli,
                    http_cli=http_cli,
                    urls=next_urls,
                    max_depth=max_depth,
                    current_depth=current_depth + 1)
