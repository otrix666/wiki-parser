from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from dataclasses import dataclass, field

import requests
from psycopg_pool import ConnectionPool

from upper_intermediate.app.db import Database
from upper_intermediate.app.http_cli import HttpClient
from upper_intermediate.config import Config


@dataclass
class DependenciesContainer:
    config: Config = field(default_factory=Config)
    pool: ConnectionPool = field(init=False)
    db: Database = field(init=False)
    thread_pool: ThreadPoolExecutor = field(init=False)
    process_pool: ProcessPoolExecutor = field(init=False)
    http_client: HttpClient = field(init=False)

    def __post_init__(self) -> None:
        db_url = (
            f"postgresql://{self.config.pg.user}:{self.config.pg.password}@"
            f"{self.config.pg.host}:{self.config.pg.port}/"
            f"{self.config.pg.db}"
        )
        self.pool = ConnectionPool(db_url, max_size=10)
        self.db = Database(pool=self.pool)

        self.thread_pool = ThreadPoolExecutor(max_workers=8)
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        self.http_client = HttpClient(client=requests.get)

    def finalize(self) -> None:
        self.pool.close()
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
