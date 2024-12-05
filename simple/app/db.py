import sqlite3

from simple.app.errors import CustomDbError


class Database:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create_table(self) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS urls(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url VARCHAR(256) UNIQUE,
                                depth INTEGER
                                )""")

            self.connection.commit()
        except Exception as e:
            raise CustomDbError(f"create table error: {e}") from e
        finally:
            cursor.close()

    def add_urls(self, urls: set[str], depth: int) -> None:
        cursor = self.connection.cursor()
        try:
            insert_data = [(url, depth) for url in urls]

            query = "INSERT OR REPLACE INTO urls(url, depth) VALUES (?, ?)"
            cursor.executemany(query, insert_data)

            self.connection.commit()
        except Exception as e:
            raise CustomDbError(f"add urls error: {e}") from e

        finally:
            cursor.close()

    def get_urls(self) -> set[str]:
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT url from urls")
            return {url[0] for url in cursor.fetchall()}
        except Exception as e:
            raise CustomDbError(f"get urls error {e}") from e
        finally:
            cursor.close()
