import sqlite3

from collections import deque

from db import Database

from parser import get_url_content
from utils import create_str_list_uploaded_wiki_url, fetch_ulrs_from_html_content


def parse_wikipedia_page(db: Database, url: str, max_depth: int = 3) -> None:
    already_uploaded_urls = create_str_list_uploaded_wiki_url(db.get_urls())

    queue = deque([(url, 1)])

    while queue:
        current_url, current_depth = queue.popleft()
        print(current_depth)

        if current_depth > max_depth:
            continue

        if current_url in already_uploaded_urls:
            continue

        db.add_url(url=current_url, depth=current_depth)
        already_uploaded_urls.append(current_url)

        html_content = get_url_content(url=current_url)
        if not html_content:
            continue

        urls = fetch_ulrs_from_html_content(html_content=html_content)

        for next_url in urls:
            queue.append((next_url, current_depth + 1))


def main():
    try:
        url = input("Enter wiki URL for parsing: ")

        connection = sqlite3.connect("parser.db")
        db = Database(connection=connection)

        parse_wikipedia_page(db=db, url=url)
    finally:
        connection.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("wiki-cli stoped")
