from aiohttp import ClientSession


class HttpClient:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def __init__(self) -> None:
        self.session: ClientSession = ClientSession()

    async def __aenter__(self):
        self.session.headers.update(self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


    async def json_request(self, method: str, url: str, **kwargs) -> dict:
        async with self.session.request(method, url, **kwargs) as response:
            return await response.json()


    async def html_request(self, method: str, url: str, **kwargs) -> str:
        async with self.session.request(method, url, **kwargs) as response:
            return await response.text()