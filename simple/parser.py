from urllib.request import urlopen



def get_url_content(url: str) -> str | None:
    try:
        response = urlopen(url=url)
        content = response.read()
        return content.decode("utf-8")
    except:
        return  None

