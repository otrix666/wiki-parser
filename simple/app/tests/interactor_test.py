import unittest
from unittest.mock import MagicMock

from simple.app.interactor import parse_wikipedia_page


class TestParseWikipediaPage(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_db = MagicMock()
        self.mock_wiki_client = MagicMock()

    def test_success_page_parse(self):
        ...


if __name__ == "__main__":
    unittest.main()
