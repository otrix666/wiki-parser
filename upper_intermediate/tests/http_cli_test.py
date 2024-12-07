from unittest.mock import MagicMock

import pytest
from requests import HTTPError

from upper_intermediate.app.errors import HttpError
from upper_intermediate.app.http_cli import HttpClient


@pytest.fixture
def client_fixture():
    return MagicMock()


@pytest.fixture
def http_client_fixture(client_fixture):
    http_client = HttpClient(client_fixture)
    return http_client


def test_success_get_url_content(http_client_fixture, client_fixture):
    client_fixture.return_value.content = b"Test content"
    result = http_client_fixture.get_url_content("http://example.com")

    client_fixture.assert_called_once_with("http://example.com")
    assert result == "Test content"


def test_failure_get_url_content_http_error(client_fixture, http_client_fixture):
    client_fixture.side_effect = HTTPError("HTTP Error occurred")

    with pytest.raises(HttpError):
        http_client_fixture.get_url_content("http://example.com")

    client_fixture.assert_called_once_with("http://example.com")
