import  unittest

from simple.parser import get_url_content

class TestParser(unittest.TestCase):

    def test_parser(self):
        html_content = get_url_content(url="https://ru.wikipedia.org/wiki/Spiranthes_ochroleuca")
        self.assertIsInstance(html_content, str)

if __name__ == "__main__":
  unittest.main()