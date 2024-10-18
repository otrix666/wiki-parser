import argparse
import logging
import sqlite3
import uuid
from urllib.request import urlopen

from simple.app.db import Database
from simple.app.errors import CustomDbError
from simple.app.interactor import parse_wikipedia_page
from simple.app.parser import WikiClient


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        encoding='utf-8'
    )
    logger = logging.getLogger(__name__)
    logger.info("wiki-cli started")

    connection = sqlite3.connect(f"{uuid.uuid4()}.db")

    try:
        parser = argparse.ArgumentParser(description="Argument for wiki parser")
        parser.add_argument("url", type=str, help="enter wiki url for parsing")
        parser.add_argument("max_depth", type=int, help="enter max depth for parsing")
        args = parser.parse_args()

        db = Database(connection=connection)
        db.create_table()

        wiki_client = WikiClient(client=urlopen)

        parse_wikipedia_page(logger=logger,
                             db=db,
                             wiki_client=wiki_client,
                             urls={args.url},
                             max_depth=args.max_depth,
                             )

    except CustomDbError:
        logger.error(f"db error")

    except KeyboardInterrupt:
        logging.info("wiki-cli stopped")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
