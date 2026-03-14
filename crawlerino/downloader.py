import aiohttp
from playwright.async_api import async_playwright
from typing import Optional, Tuple
import logging
from crawlerino.models import CrawlRequest

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, user_agent: str = "Crawlerino/1.0"):
        self.headers = {"User-Agent": user_agent}
        self._browser = None

    async def fetch(self, request: CrawlRequest) -> Tuple[str, str]:
        """
        Fetches content. Returns (html_content, final_url).
        Switches to Playwright if JS is required.
        """
        if request.requires_js:
            return await self._fetch_with_playwright(request)
        return await self._fetch_with_aiohttp(request)

    async def _fetch_with_aiohttp(self, request: CrawlRequest) -> Tuple[str, str]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(str(request.url), timeout=10) as response:
                    response.raise_for_status()
                    return await response.text(), str(response.url)
            except Exception as e:
                logger.error(f"aiohttp error for {request.url}: {e}")
                raise

    async def _fetch_with_playwright(self, request: CrawlRequest) -> Tuple[str, str]:
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=True)
        
        async with self._browser.new_context() as context:
            page = await context.new_page()
            try:
                await page.goto(str(request.url), wait_until="networkidle", timeout=30000)
                content = await page.content()
                return content, page.url
            except Exception as e:
                logger.error(f"Playwright error for {request.url}: {e}")
                raise
            finally:
                await page.close()

    async def close(self):
        if self._browser:
            await self._browser.close()