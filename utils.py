import re


def fetch_ulrs_from_html_content(html_content: str) -> set[str]:
    url_pattern = r'(https?://[^\s">]+)'
    return set(re.findall(url_pattern, html_content))


def create_str_list_uploaded_wiki_url(uploaded_urls: list[tuple]):
    return [url[0] for url in uploaded_urls]
