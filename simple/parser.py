import urllib.request


def get_url_content(url: str) -> str | None:
    try:
        response = urllib.request.urlopen(url=url)
        content = response.read()
        return content.decode("utf-8")
    except:
        return None
