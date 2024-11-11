import unittest
from unittest.mock import MagicMock, call

from simple.app.application import parse_wikipedia_page


class TestParseWikipediaPage(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_db = MagicMock()
        self.mock_wiki_client = MagicMock()

    def test_success_page_parse(self):
        self.mock_wiki_client.get_url_content.return_value = "https://ru.wikipedia.org/wiki/%D0%92%D0%B0%D0%B7%D1%8F%D0%BC"
        urls = {"https://ru.wikipedia.org/wiki/Porsche_Lizenz-_und_Handelsgesellschaft_mbH_%26_Co._KG"}

        parse_wikipedia_page(
            logger=self.mock_logger,
            db=self.mock_db,
            wiki_client=self.mock_wiki_client,
            urls=urls,
            current_depth=1,
            max_depth=2
        )

        self.mock_db.add_urls.assert_has_calls([
            call(urls={"https://ru.wikipedia.org/wiki/Porsche_Lizenz-_und_Handelsgesellschaft_mbH_%26_Co._KG"},
                 depth=1),
            call(urls={"https://ru.wikipedia.org/wiki/%D0%92%D0%B0%D0%B7%D1%8F%D0%BC"}, depth=2)
        ])


if __name__ == "__main__":
    unittest.main()
