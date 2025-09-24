from aiohttp import ClientSession, ClientError
import asyncio
import random


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
        for attempt in range(5):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    return await response.text()
            except (ClientError, asyncio.TimeoutError) as e:
                print(f'trying to get content from page {url} attempt #{attempt}, error: {e}')
                await asyncio.sleep(5 * random.randint(1, 10) / 10)
        raise