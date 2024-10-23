import unittest
from unittest.mock import MagicMock

from simple.app.interactor import parse_wikipedia_page


class TestParseWikipediaPage(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_db = MagicMock()
        self.mock_wiki_client = MagicMock()
        self.urls_fetcher = MagicMock()

    def test_success_page_parse(self):
        test_content = '<html>Test content</html>'

        self.mock_wiki_client.get_url_content.return_value = test_content

        parse_wikipedia_page(
            logger=self.mock_logger,
            db=self.mock_db,
            urls_fetcher=self.urls_fetcher,
            wiki_client=self.mock_wiki_client,
            url='https://ru.wikipedia.org/wiki',
            max_depth=2
        )

        self.mock_wiki_client.get_url_content.assert_called_with(url='https://ru.wikipedia.org/wiki')
        self.urls_fetcher.assert_called_once_with(html_content=test_content)
        # self.mock_db.add_urls.assert_called_with(insert_values={('https://ru.wikipedia.org/wiki', 1)})
        self.mock_logger.error.assert_not_called()



if __name__ == "__main__":
    unittest.main()
