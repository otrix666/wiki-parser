from psycopg import  Connection

from intermediate.app.errors import  CustomDbError

class Database:
    def __init__(self, connection: Connection):
        self.connection = connection

    def create_table(self) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS urls(
                                id SERIAL PRIMARY KEY,
                                url VARCHAR(256) UNIQUE,
                                depth INTEGER
                                )""")

            self.connection.commit()
        except Exception as e:
            raise CustomDbError(f"create table error: {e}") from e
        finally:
            cursor.close()

    def clear_urls(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM urls")

            self.connection.commit()
        except Exception as e:
            raise CustomDbError(f"clear urls error: {e}") from e
        finally:
            cursor.close()

    def add_urls(self, urls: set[str], depth: int) -> None:
        cursor = self.connection.cursor()

        try:
            insert_data = [(url, depth) for url in urls]
            cursor.executemany("INSERT INTO urls(url, depth) VALUES (%s, %s)", insert_data)

            self.connection.commit()
        except Exception as e:
            raise CustomDbError(f"add urls error: {e} {urls}") from e

        finally:
            cursor.close()

