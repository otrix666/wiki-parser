import uuid
import  logging
import sqlite3

from collections import deque

from db import Database
from parser import get_url_content
from errors import CustomDbError
from utils import fetch_urls_from_html_content

from setup_logging import  setup_logging

logger = logging.getLogger(__name__)

def parse_wikipedia_page(db: Database, url: str, max_depth: int = 3) -> None:
    insert_values = set()
    already_uploaded_urls = db.get_urls()

    last_depth = 1
    queue = deque([(url, last_depth)])

    while queue:
        current_url, current_depth = queue.popleft()

        if current_depth > max_depth:
            continue

        if current_url in already_uploaded_urls:
            continue

        if current_depth > last_depth:
            last_depth = current_depth
            try:
                db.add_urls(insert_values=insert_values)
                insert_values.clear()
            except CustomDbError as e:
                logger.error(e)

        html_content = get_url_content(url=current_url)
        if not html_content:
            continue

        already_uploaded_urls.add(current_url)
        insert_values.add((current_url, current_depth))

        urls = fetch_urls_from_html_content(html_content=html_content)
        logger.info(urls)

        for next_url in urls:
            queue.append((next_url, current_depth + 1))


def main():
    setup_logging()
    connection = sqlite3.connect(f"{uuid.uuid4()}.db")

    try:
        url = input("Enter wiki URL for parsing: ")

        db = Database(connection=connection)
        db.create_table()

        parse_wikipedia_page(db=db, url=url)

    except CustomDbError as e:
        logger.error(e)

    except KeyboardInterrupt:
        logging.info("wiki-cli stopped")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
