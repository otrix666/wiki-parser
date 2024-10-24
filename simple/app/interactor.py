import  re
import  logging

from simple.app.db import  Database
from simple.app.errors import CustomDbError, CustomParserError
from simple.app.parser import WikiClient


def parse_wikipedia_page(logger: logging.Logger,
                         db: Database,
                         wiki_client: WikiClient,
                         url: str,
                         current_depth: int = 1,
                         max_depth: int = 3,
                         insert_urls: dict[int, set[str]] = None
) -> None:
    if current_depth > max_depth + 1:
        return

    is_new_depth = False

    if not insert_urls:
        insert_urls = {}

    if current_depth not in insert_urls:
        is_new_depth = True
        insert_urls[current_depth] = set()

    insert_urls[current_depth].add(url)

    if is_new_depth and current_depth != 1:
        prev_depth = current_depth - 1
        values = insert_urls[prev_depth]
        try:
            db.add_urls(urls=values, depth=prev_depth)
        except CustomDbError:
            return logger.error("db error")

    try:
        html_content = wiki_client.get_url_content(url=url)
    except CustomParserError:
        return logger.error("parser error")

    urls = re.findall(r'(https?://[^\s">]*wikipedia\.org[^\s">]*)', html_content)

    for next_url in urls:
        parse_wikipedia_page(logger=logger,
                             db=db,
                             wiki_client=wiki_client,
                             url=next_url,
                             current_depth=current_depth + 1,
                             max_depth=max_depth,
                             insert_urls=insert_urls)


