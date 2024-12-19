from concurrent.futures import (
    ProcessPoolExecutor,
)
from dataclasses import dataclass, field

from aiohttp import ClientSession
from asyncpg import Pool, create_pool

from advanced.app.db import Database
from advanced.app.http_cli import HTTPClient
from advanced.config import Config


@dataclass
class DependenciesContainer:
    config: Config = field(default_factory=Config)
    session: ClientSession = field(default_factory=ClientSession)
    pool: Pool = field(init=False)
    db: Database = field(init=False)
    process_pool: ProcessPoolExecutor = field(init=False)
    http_client: HTTPClient = field(init=False)

    def __post_init__(self) -> None:
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        self.http_client = HTTPClient(session=self.session)

    async def initialize(self) -> None:
        self.pool = await create_pool(
            host=self.config.pg.host,
            port=self.config.pg.port,
            user=self.config.pg.user,
            database=self.config.pg.db,
            password=self.config.pg.password,
            min_size=10,
            max_size=10,
        )
        self.db = Database(pool=self.pool)

    async def finalize(self) -> None:
        await self.pool.close()
        await self.session.close()
        self.process_pool.shutdown()
