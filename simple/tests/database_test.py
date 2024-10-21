import  uuid
import  sqlite3
import unittest

from simple.db import  Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(f"{uuid.uuid4()}_test.db")
        self.db = Database(connection=self.connection)

    def tearDown(self):
        self.connection.close()

    def test_table_create(self):
        self.db.create_table()

        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls';")
        table_exists = cursor.fetchone()
        cursor.close()

        self.assertIsNotNone(table_exists)


    def test_add_urls(self):
        self.db.create_table()
        insert_values = {("https://wiki.org123", 1,), ("https://wiki.org1234", 2), ("https://wiki.org1245", 2)}
        self.db.add_urls(insert_values=insert_values)

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM urls")
        result = cursor.fetchall()
        cursor.close()

        self.assertEqual(len(insert_values), len(result))


if __name__ == "__main__":
  unittest.main()