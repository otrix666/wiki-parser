import re


def fetch_ulrs_from_html_content(html_content: str) -> set[str]:
    url_pattern = r'(https?://[^\s">]+)'
    return set(re.findall(url_pattern, html_content))
