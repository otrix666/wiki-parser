from typing import (
    Callable,
    TypeVar
)

from requests import (
    Response,
    HTTPError
)

from intermediate.app.errors import CustomHTTPClientError

Client = TypeVar("Client", bound=Callable[..., Response])


class HttpClient:
    def __init__(self, client: Client) -> None:
        self.client = client

    def get_url_content(self, url: str) -> str:
        try:
            response = self.client(url)
            return response.content.decode("utf-8")
        except UnicodeEncodeError as e:
            raise CustomHTTPClientError from e
        except HTTPError as e:
            raise CustomHTTPClientError from e
