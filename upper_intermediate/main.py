import argparse
import logging
import time

import requests
from psycopg_pool import ConnectionPool

from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
)

from upper_intermediate.app.application import parse_wiki_page
from upper_intermediate.app.db import Database
from upper_intermediate.app.errors import (
    CustomDbError
)
from upper_intermediate.app.http_cli import HttpClient
from upper_intermediate.config import Config


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        encoding='utf-8'
    )
    logger = logging.getLogger(__name__)
    logger.info("wiki-cli started")

    config = Config()

    db_url = f"postgresql://{config.pg.user}:{config.pg.password}@{config.pg.host}:{config.pg.port}/{config.pg.db}"
    pool = ConnectionPool(db_url, max_size=10)

    thread_pool = ThreadPoolExecutor(max_workers=8)
    process_pool = ProcessPoolExecutor(max_workers=4)

    try:
        parser = argparse.ArgumentParser(description="Argument for wiki parser")
        parser.add_argument("url", type=str, help="enter wiki url for parsing")
        parser.add_argument("max_depth", type=int, help="enter max depth for parsing")
        args = parser.parse_args()

        db = Database(pool=pool)
        db.create_table()
        db.clear_urls()

        http_cli = HttpClient(client=requests.get)

        parse_wiki_page(logger=logger,
                        db=db,
                        thread_pool=thread_pool,
                        process_pool=process_pool,
                        http_cli=http_cli,
                        urls={args.url},
                        max_depth=args.max_depth)

    except CustomDbError:
        logger.error(f"db error")

    except KeyboardInterrupt:
        logger.info("wiki-cli stopped")

    finally:
        pool.close()
        thread_pool.shutdown(wait=False, cancel_futures=True)
        process_pool.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    work_time = round(end_time - start_time, 2)
    print(f"Work time: {work_time}")
