import re


def fetch_urls_from_html_content(html_content: str) -> set[str]:
    url_pattern = r'(https?://[^\s">]*wikipedia\.org[^\s">]*)'
    return set(re.findall(url_pattern, html_content))


