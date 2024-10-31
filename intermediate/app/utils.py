from bs4 import BeautifulSoup


def url_finder(content: str) -> set[str]:
    urls = set()
    soup = BeautifulSoup(content, "html.parser")
    for url in soup.find_all('a'):
        urls.add(url.get('href'))

    return  urls