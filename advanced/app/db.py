from asyncpg import Pool

from advanced.app.errors import DbError


class Database:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_table(self) -> None:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS urls(
                        id SERIAL PRIMARY KEY,
                        url VARCHAR(512) UNIQUE,
                        depth INTEGER
                    )
                """)
        except Exception as e:
            raise DbError("Error while creating table") from e

    async def clear_urls(self) -> None:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("DELETE FROM urls")
        except Exception as e:
            raise DbError("Error while clearing urls") from e

    async def add_urls(self, urls: set[str], depth: int) -> None:
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    insert_data = [(url, depth) for url in urls]
                    query = "INSERT INTO urls(url, depth) VALUES ($1, $2) ON CONFLICT (url) DO NOTHING"
                    await conn.executemany(query, insert_data)
        except Exception as e:
            raise DbError("Error while adding urls") from e

    async def get_urls(self) -> set[str]:
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT url FROM urls")
                return {row["url"] for row in rows}
        except Exception as e:
            raise DbError("Error while getting urls") from e
