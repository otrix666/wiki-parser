import aiohttp
import pytest
from aioresponses import aioresponses

from advanced.app.errors import HttpError
from advanced.app.http_cli import HTTPClient


@pytest.mark.asyncio
async def test_get_content():
    url = "https://example.com"
    content = "Test content"

    async with aiohttp.ClientSession() as session:
        client = HTTPClient(session)

        with aioresponses() as mock:
            mock.get(url, body=content, status=200)
            result = await client.get_content(url)

            assert result == content


@pytest.mark.asyncio
async def test_get_content_not_found():
    url = "https://example.com"

    async with aiohttp.ClientSession() as session:
        client = HTTPClient(session)

        with aioresponses() as mock:
            mock.get(url, status=404)

            with pytest.raises(HttpError):
                await client.get_content(url)
