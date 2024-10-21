import  unittest
from unittest.mock import  patch, MagicMock

from simple.parser import get_url_content

class TestParser(unittest.TestCase):

    @patch("simple.parser.urlopen")
    def test_parser(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"test html content"
        mock_urlopen.return_value = mock_response

        html_content = get_url_content(url="https://ru.wikipedia.org/wiki/Spiranthes_ochroleuca")
        self.assertIsInstance(html_content, str)

if __name__ == "__main__":
  unittest.main()