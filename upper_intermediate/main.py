import argparse
import logging
import time

from upper_intermediate.app.application import WikiParser
from upper_intermediate.app.dependencies import DependenciesContainer
from upper_intermediate.app.errors import (
    DbError
)
from upper_intermediate.config import Config


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        encoding='utf-8'
    )
    logger = logging.getLogger(__name__)
    logger.info("wiki-cli started")
    return logger


def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Argument for wiki parser")
    parser.add_argument("url", type=str, help="enter wiki url for parsing")
    parser.add_argument("max_depth", type=int, help="enter max depth for parsing")
    return parser.parse_args()


def main():
    config = Config()
    logger = setup_logging()
    dependencies = DependenciesContainer(config=config)
    try:
        dependencies.db.create_table()
        dependencies.db.clear_urls()

        args = parse_argument()

        parser = WikiParser(logger=logger,
                            db=dependencies.db,
                            thread_pool=dependencies.thread_pool,
                            process_pool=dependencies.process_pool,
                            http_client=dependencies.http_client)
        parser.run(urls={args.url}, max_depth=args.max_depth)

    except DbError as e:
        logger.error("db error", e)

    except KeyboardInterrupt:
        logger.info("wiki-cli stopped")

    finally:
        dependencies.finalize()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    work_time = round(end_time - start_time, 2)
    print(f"Work time: {work_time}")
