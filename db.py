import sqlite3


class Database:
    def __init__(self, connection: sqlite3.Connection = None):
        self.connection = connection

    def create_table(self) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS urls(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url TEXT,
                                depth INTEGER
                                )""")

            self.connection.commit()
        finally:
            cursor.close()

    def add_url(self, url: str, depth: int) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO urls(url, depth) VALUES (?, ?)", (url, depth, ))

            self.connection.commit()
        finally:
            cursor.close()

    def get_urls(self) -> list[tuple]:
        try:
            cursor = self.connection.cursor()
            result = cursor.execute("select url from urls")
            return result.fetchall()
        finally:
            cursor.close()
