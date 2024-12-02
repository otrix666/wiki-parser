import re
from bs4 import BeautifulSoup


def url_finder(content: str) -> set[str]:
    urls = set()
    url_pattern = re.compile(r"^/wiki/[^\s%]+$")
    soup = BeautifulSoup(content, "lxml")

    for url in soup.find_all("a", href=url_pattern):
        urls.add(url.get("href"))

    return urls
