import sqlite3


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("parser.db")
        self.cursor = self.connection.cursor()

    def _commiter(self):
        self.connection.commit()

    def _closer(self):
        self.connection.close()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS urls(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            url TEXT,
                            depth INTEGER
                            )""")
        self._commiter()

    def add_url(self, url: str, depth: int):
        self.cursor.execute(
            "INSERT INTO urls(url, depth) VALUES (?, ?)", (url, depth, ))
        self._commiter()

    def get_url(self, url: str) -> tuple | None:
        self.cursor.execute("select url from urls where url = ?", (url, ))
        return self.cursor.fetchone()


db = Database()
