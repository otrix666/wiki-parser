import re

from bs4 import BeautifulSoup

URL_PATTERN = re.compile(r"^/wiki/(?!.*\.(?:png|jpg|gif|pdf|svg|mp4)).*$")


def url_finder(content: str) -> set[str]:
    urls = set()
    soup = BeautifulSoup(content, "lxml")
    for url in soup.find_all("a", href=URL_PATTERN):
        urls.add(url.get("href"))

    return urls
