from typing import Callable, TypeVar

from requests import HTTPError, Response

from upper_intermediate.app.errors import EncodeError, HttpError

Client = TypeVar("Client", bound=Callable[..., Response])


class HttpClient:
    def __init__(self, client: Client) -> None:
        self.client = client

    def get_url_content(self, url: str) -> str:
        try:
            response = self.client(url)
            return response.content.decode("utf-8")
        except UnicodeEncodeError as e:
            raise EncodeError from e
        except HTTPError as e:
            raise HttpError from e
