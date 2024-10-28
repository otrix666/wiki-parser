from http.client import HTTPResponse
from typing import Callable, TypeVar
from urllib.error import HTTPError

from simple.app.errors import CustomParserError

Client = TypeVar("Client", bound=Callable[..., HTTPResponse])


class WikiClient:
    def __init__(self, client: Client) -> None:
        self.client = client

    def get_url_content(self, url: str) -> str:
        try:
            response = self.client(url)
            content = response.read()
            return content.decode("utf-8")
        except UnicodeEncodeError as e:
            raise CustomParserError from e
        except HTTPError as e:
            raise CustomParserError from e
