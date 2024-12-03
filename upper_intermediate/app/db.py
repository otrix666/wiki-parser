from psycopg_pool import ConnectionPool

from upper_intermediate.app.errors import DbError


class Database:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    def create_table(self) -> None:
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""CREATE TABLE IF NOT EXISTS urls(
                                    id SERIAL PRIMARY KEY,
                                    url VARCHAR(256) UNIQUE,
                                    depth INTEGER
                                    )""")
                conn.commit()
        except Exception as e:
            raise DbError("error while creating table", e)

    def clear_urls(self):
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM urls")

                conn.commit()
        except Exception as e:
            raise DbError("error while clearing urls", e)

    def add_urls(self, urls: set[str], depth: int) -> None:
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cursor:
                    insert_data = [(url, depth) for url in urls]
                    cursor.executemany("INSERT INTO urls(url, depth) VALUES (%s, %s)", insert_data)
                conn.commit()
        except Exception as e:
            raise DbError("error while adding urls", e)

    def get_urls(self, ) -> set[str]:
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM urls")
                    return {data[1] for data in cursor.fetchall()}
        except Exception as e:
            raise DbError("error while getting urls", e)
