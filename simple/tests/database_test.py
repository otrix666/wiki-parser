import unittest
from sqlite3 import OperationalError
from unittest.mock import MagicMock, call

from simple.app.db import Database
from simple.app.errors import CustomDbError


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.db = Database(connection=self.mock_connection)

    def tearDown(self):
        self.mock_connection.reset_mock()
        self.mock_cursor.reset_mock()

    def test_success_table_create(self):
        self.db.create_table()

        self.mock_connection.cursor.assert_called_once()

        self.mock_cursor.execute.assert_called_once_with("""CREATE TABLE IF NOT EXISTS urls(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url VARCHAR(256) UNIQUE,
                                depth INTEGER
                                )""")

        self.mock_connection.commit.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_failure_table_create(self):
        self.mock_cursor.execute.side_effect = OperationalError

        with self.assertRaises(CustomDbError):
            self.db.create_table()

        self.mock_connection.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_not_called()
        self.mock_cursor.close.assert_called_once()

    def test_success_add_urls(self):
        urls = {"https://wiki.org123", "https://wiki.org1234", "https://wiki.org1245"}
        depth = 1

        self.db.add_urls(urls=urls, depth=depth)

        assert self.mock_cursor.executemany.call_args == call(
            "INSERT OR REPLACE INTO urls(url, depth) VALUES (?, ?)",
            [("https://wiki.org1245", 1), ("https://wiki.org1234", 1), ("https://wiki.org123", 1)],
        )

        self.mock_connection.commit.assert_called()
        self.mock_cursor.close.assert_called()

    def test_failure_add_urls(self):
        self.mock_cursor.executemany.side_effect = OperationalError

        urls = {"https://wiki.org123", "https://wiki.org1234", "https://wiki.org1245"}
        depth = 1

        with self.assertRaises(CustomDbError):
            self.db.add_urls(urls=urls, depth=depth)

        self.mock_connection.cursor.assert_called()
        self.mock_cursor.execute.executemany.assert_not_called()
        self.mock_connection.commit.assert_not_called()
        self.mock_cursor.close.assert_called()


if __name__ == "__main__":
    unittest.main()
