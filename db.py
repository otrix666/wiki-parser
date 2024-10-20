import sqlite3

from errors import CustomDbError


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

    def add_urls(self, insert_values: list[tuple]) -> None:
        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO urls(url, depth) VALUES (?, ?)"
            cursor.executemany(query, insert_values)

            self.connection.commit()
        except Exception as e:
            raise CustomDbError(f"add urls error: {e}") from e

        finally:
            cursor.close()

    def get_urls(self) -> set[tuple]:
        cursor = self.connection.cursor()
        try:
            result = cursor.execute("select url from urls").fetchall()
            return {row[0] for row in result}
        except Exception as e:
            raise CustomDbError(f"get urls error: {e}") from e
        finally:
            cursor.close()
