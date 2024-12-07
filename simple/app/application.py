import logging
import re

from simple.app.db import Database
from simple.app.errors import CustomDbError, CustomParserError
from simple.app.parser import WikiClient


def parse_wikipedia_page(
    logger: logging.Logger,
    db: Database,
    wiki_client: WikiClient,
    urls: set[str],
    max_depth: int,
    current_depth: int = 1,
) -> None:
    if current_depth > max_depth:
        return

    try:
        db.add_urls(urls=urls, depth=current_depth)
        logger.info(f"added urls {urls}")
    except CustomDbError:
        return logger.error("db error")

    next_urls = set()

    for url in urls:
        logger.info(url)
        try:
            html_content = wiki_client.get_url_content(url=url)
            parse_urls = re.findall(r'(/wiki/[^\s%"]+>\\)', html_content)
            next_urls.update(f"https://en.wikipedia.org{url}" for url in parse_urls)

        except CustomParserError:
            logger.error("parser error")
            continue

    next_urls -= db.get_urls()
    parse_wikipedia_page(
        logger=logger,
        db=db,
        wiki_client=wiki_client,
        urls=next_urls,
        max_depth=max_depth,
        current_depth=current_depth + 1,
    )
