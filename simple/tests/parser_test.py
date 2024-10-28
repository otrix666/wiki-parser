import unittest
from unittest.mock import MagicMock

from simple.app.parser import WikiClient


# from simple.parser import get_url_content

class TestParser(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.client = WikiClient(client=self.mock_client)

    def test_parser(self):
        mock_response = MagicMock()
        mock_response.read.return_value = b"test html content"

        self.mock_client.return_value = mock_response

        result = self.client.get_url_content("https://example.com")

        self.assertIsInstance(result, str)
        self.assertEqual(result, "test html content")

        self.mock_client.assert_called_once_with("https://example.com")
        mock_response.read.assert_called_once()


if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
