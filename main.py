from collections import deque

from db import db

from parser import get_url_content
from utils import fetch_ulrs_from_html_content


def parse_wikipedia_page(url: str, max_depth: int = 6) -> None:
    queue = deque([(url, 1)])

    while queue:
        current_url, current_depth = queue.popleft()

        if current_depth > max_depth:
            continue

        if db.get_url(url=current_url):
            continue

        db.add_url(url=current_url, depth=current_depth)
        
        html_content = get_url_content(url=current_url)
        if not html_content:
            continue

        urls = fetch_ulrs_from_html_content(html_content=html_content)

        for next_url in urls:
            queue.append((next_url, current_depth + 1))


def main():
    url = input("Enter wiki URL for parsing: ")
    parse_wikipedia_page(url=url)


if __name__ == "__main__":
    try:
        db.create_table()
        main()
    except KeyboardInterrupt:
        print("wiki-cli stoped")
    finally:
        db._closer()
