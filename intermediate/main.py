import argparse
import logging

import psycopg
import requests
from redis import Redis

from intermediate.app.application import parse_wiki_page
from intermediate.app.db import Database
from intermediate.app.errors import CustomDbError, CustomRedisError
from intermediate.app.http_cli import HttpClient
from intermediate.app.redis_cli import RedisClient
from intermediate.config import Config


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        encoding="utf-8",
    )
    logger = logging.getLogger(__name__)
    logger.info("wiki-cli started")

    config = Config()

    pg_conn = psycopg.connect(
        dbname=config.pg.pg_db,
        user=config.pg.pg_user,
        host=config.pg.pg_host,
        port=config.pg.pg_port,
        password=config.pg.pg_password,
    )
    try:
        parser = argparse.ArgumentParser(description="Argument for wiki parser")
        parser.add_argument("url", type=str, help="enter wiki url for parsing")
        parser.add_argument("max_depth", type=int, help="enter max depth for parsing")
        args = parser.parse_args()

        db = Database(connection=pg_conn)
        db.create_table()
        db.clear_urls()

        redis_conn = Redis(
            host=config.redis.redis_host,
            port=config.redis.redis_port,
            db=config.redis.redis_db,
        )
        redis_cli = RedisClient(connection=redis_conn)
        redis_cli.clear_urls()

        http_cli = HttpClient(client=requests.get)

        parse_wiki_page(
            logger=logger, db=db, redis_cli=redis_cli, http_cli=http_cli, urls={args.url}, max_depth=args.max_depth
        )

    except CustomDbError:
        logger.error("db error")

    except CustomRedisError:
        logger.error("redis error")

    except KeyboardInterrupt:
        logger.info("wiki-cli stopped")

    finally:
        pg_conn.close()


if __name__ == "__main__":
    main()
