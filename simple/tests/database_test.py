import  uuid
import  sqlite3
import unittest
from unittest.mock import MagicMock

from simple.db import  Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.db = Database(connection=self.mock_connection)

    # def tearDown(self):
    #     self.connection.close()

    def test_success_table_create(self):
        self.db.create_table()

        mock_cursor = self.mock_connection.cursor()
        mock_cursor.execute.return_value = ("urls", )
        mock_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls';")
        mock_cursor.fetchone.return_value = ("urls",)
        table_exists = mock_cursor.fetchone()

        self.assertIsNotNone(table_exists)

    def test_failure_table_create(self):
        self.db.create_table()

        mock_cursor = self.mock_connection.cursor()
        mock_cursor.execute.return_value = ("urls", )
        mock_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls';")
        mock_cursor.fetchone.return_value = None
        table_exists = mock_cursor.fetchone()

        self.assertIsNotNone(table_exists)

    def test_success_add_urls(self):
        self.db.create_table()

        insert_values = {("https://wiki.org123", 1,), ("https://wiki.org1234", 2), ("https://wiki.org1245", 2)}
        self.db.add_urls(insert_values=insert_values)

        self.mock_cursor.execute("SELECT * FROM urls")
        self.mock_cursor.fetchall.return_value = list(insert_values)
        result = self.mock_cursor.fetchall()

        self.assertEqual(len(insert_values), len(result))

    def test_failure_add_urls(self):
        self.db.create_table()

        insert_values = {("https://wiki.org123", 1,), ("https://wiki.org1234", 2), ("https://wiki.org1245", 2)}
        self.db.add_urls(insert_values=insert_values)

        self.mock_cursor.execute("SELECT * FROM urls")
        self.mock_cursor.fetchall.return_value = list()
        result = self.mock_cursor.fetchall()

        self.assertEqual(len(insert_values), len(result))


if __name__ == "__main__":
  unittest.main()