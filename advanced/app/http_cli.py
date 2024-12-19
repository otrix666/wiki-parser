from aiohttp import ClientSession

from advanced.app.errors import HttpError


class HTTPClient:
    def __init__(self, session: ClientSession) -> None:
        self.session = session

    async def get_content(self, url: str) -> str:
        async with self.session.get(url) as resp:
            if resp.status != 200:
                raise HttpError(f"HTTP request failed with status {resp.status}")
            try:
                return await resp.text(encoding="utf-8")
            except Exception as e:
                raise HttpError from e
