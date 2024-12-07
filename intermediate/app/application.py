from logging import Logger

from intermediate.app.db import Database
from intermediate.app.errors import CustomDbError, CustomHTTPClientError, CustomRedisError
from intermediate.app.http_cli import HttpClient
from intermediate.app.redis_cli import RedisClient
from intermediate.app.utils import url_finder


def parse_wiki_page(
    logger: Logger,
    db: Database,
    redis_cli: RedisClient,
    http_cli: HttpClient,
    urls: set[str],
    max_depth: int,
    current_depth: int = 1,
) -> None:
    if current_depth > max_depth:
        return

    try:
        db.add_urls(urls=urls, depth=current_depth)
        logger.info(f"added urls to pg: {urls}")
    except CustomDbError as e:
        return logger.error(f"db error: {e}")

    try:
        redis_cli.add_urls(urls)
    except CustomRedisError as e:
        return logger.error(f"redis error: {e}")

    next_urls = set()
    for url in urls:
        try:
            html_content = http_cli.get_url_content(url=url)
            page_urls = url_finder(html_content)
            next_urls = {f"https://en.wikipedia.org{url}" for url in page_urls}
            logger.info(next_urls)
        except CustomHTTPClientError as e:
            logger.warning(f"http client error: {e}")
        except Exception as e:
            logger.warning(f"Unknown error: {e}")

    next_urls -= redis_cli.get_saved_urls()

    parse_wiki_page(
        logger=logger,
        db=db,
        redis_cli=redis_cli,
        http_cli=http_cli,
        urls=next_urls,
        max_depth=max_depth,
        current_depth=current_depth + 1,
    )
