from aiohttp import ClientSession, ClientError
import asyncio
import random
import logging
from typing import Optional


class HttpClient:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self._session_lock: asyncio.Lock = asyncio.Lock()

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None


    async def json_request(self, method: str, url: str, **kwargs) -> dict:
        session = await self._ensure_session()
        async with session.request(method, url, **kwargs) as response:
            return await response.json()


    async def html_request(self, method: str, url: str, **kwargs) -> str:
        for attempt in range(5):
            try:
                session = await self._ensure_session()
                async with session.request(method, url, **kwargs) as response:
                    if attempt > 0:
                        logging.warning(f"After attempts: {attempt+1} finally did the request")
                    return await response.text()
            except (ClientError, asyncio.TimeoutError, RuntimeError) as e:
                logging.info(f'trying to get content from page {url} attempt #{attempt}, error: {e}')
                if isinstance(e, RuntimeError) or (self.session and self.session.closed):
                    await self._recreate_session()
                await asyncio.sleep(min(60, (2 ** attempt) + random.random()))
            
        logging.error(f'URL {url} failed after 5 attempts. Sleeping for 5 minutes before retry....')
        await self._recreate_session()
        await asyncio.sleep(5 * 60)
        try:
            session = await self._ensure_session()
            async with session.request(method, url, **kwargs) as response:
                return await response.text()
        except Exception as e:
            logging.critical(f'Final attempt for {url} failed: {e}')
            raise
        
    async def _ensure_session(self) -> ClientSession:
        async with self._session_lock:
            if self.session is None or self.session.closed:
                if self.session and not self.session.closed:
                    await self.session.close()
                self.session = ClientSession()
                self.session.headers.update(self.headers)
            return self.session

    async def _recreate_session(self) -> None:
        async with self._session_lock:
            if self.session and not self.session.closed:
                await self.session.close()
            self.session = ClientSession()
            self.session.headers.update(self.headers)
