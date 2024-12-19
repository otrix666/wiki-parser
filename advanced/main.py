import argparse
import asyncio
import logging
import time

from advanced.app.application import WikiCrawler
from advanced.app.dependencies import DependenciesContainer
from advanced.app.errors import DbError
from advanced.config import Config


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        encoding="utf-8",
    )
    logger = logging.getLogger(__name__)
    logger.info("wiki-cli started")
    return logger


def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Argument for wiki parser")
    parser.add_argument("url", type=str, help="enter wiki url for parsing")
    parser.add_argument("max_depth", type=int, help="enter max depth for parsing")
    return parser.parse_args()


async def main():
    config = Config()
    logger = setup_logging()
    dependencies = DependenciesContainer(config=config)
    await dependencies.initialize()
    try:
        await dependencies.db.create_table()
        await dependencies.db.clear_urls()

        args = parse_argument()

        parser = WikiCrawler(
            logger=logger,
            db=dependencies.db,
            process_pool=dependencies.process_pool,
            http_client=dependencies.http_client,
        )
        await parser.run(urls={args.url}, max_depth=args.max_depth)

    except DbError:
        logger.exception("db error")

    except KeyboardInterrupt:
        logger.info("wiki-cli stopped")

    finally:
        await dependencies.finalize()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    work_time = round(end_time - start_time, 2)
    print(f"Work time: {work_time}")
