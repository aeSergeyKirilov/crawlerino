import asyncio
import hashlib
import logging
from typing import List, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from crawlerino.models import CrawlRequest, ExtractedData, CrawlStatus
from crawlerino.queue_manager import PriorityQueue
from crawlerino.downloader import Downloader
from crawlerino.config import CrawlerConfig

logger = logging.getLogger(__name__)

class CrawlerAgent:
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.queue = PriorityQueue()
        self.downloader = Downloader()
        self.visited_urls: Set[str] = set()
        self.results: List[ExtractedData] = []
        self._semaphore = asyncio.Semaphore(config.concurrency_limit)

    async def run(self):
        """Main entry point."""
        for url in self.config.start_urls:
            await self.queue.put(CrawlRequest(url=url, priority=0))

        workers = [asyncio.create_task(self._worker()) for _ in range(self.config.concurrency_limit)]
        await asyncio.gather(*workers)
        await self.downloader.close()
        logger.info(f"Crawling finished. Processed {len(self.results)} pages.")

    async def _worker(self):
        while True:
            request = await self.queue.get()
            if not request:
                # Simple stop condition: if queue is empty and no tasks running
                if await self.queue.empty():
                    break
                await asyncio.sleep(0.1)
                continue

            async with self._semaphore:
                await self._process_request(request)

    async def _process_request(self, request: CrawlRequest):
        if str(request.url) in self.visited_urls:
            return
        
        self.visited_urls.add(str(request.url))
        logger.info(f"Processing: {request.url} (Depth: {request.depth})")

        try:
            html, final_url = await self.downloader.fetch(request)
            data = self._parse_html(html, final_url)
            self.results.append(data)
            
            # Dynamic Routing: Add new links to queue
            await self._schedule_new_links(data.links_found, request.depth + 1)

        except Exception as e:
            await self._handle_error(request, e)

    def _parse_html(self, html: str, url: str) -> ExtractedData:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else None
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        
        # Heuristic: if page has many scripts, assume children might need JS
        requires_js = len(soup.find_all('script')) > 5 

        content_hash = hashlib.md5(html.encode()).hexdigest()

        return ExtractedData(
            url=url,
            title=title,
            content_hash=content_hash,
            links_found=links[:50], # Limit links to prevent explosion
            metadata={"requires_js_next": requires_js}
        )

    async def _schedule_new_links(self, links: List[str], depth: int):
        if depth >= self.config.max_depth:
            return

        for link in links:
            if self._is_valid_domain(link) and link not in self.visited_urls:
                # Priority logic: deeper pages get lower priority (higher number)
                priority = depth 
                await self.queue.put(CrawlRequest(
                    url=link, 
                    depth=depth, 
                    priority=priority,
                    requires_js=False 
                ))

    def _is_valid_domain(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc in self.config.allowed_domains

    async def _handle_error(self, request: CrawlRequest, error: Exception):
        if request.retry_count < self.config.max_retries:
            request.retry_count += 1
            # Exponential backoff
            delay = (2 ** request.retry_count) 
            logger.warning(f"Retrying {request.url} in {delay}s. Attempt {request.retry_count}")
            await asyncio.sleep(delay)
            await self.queue.put(request)
        else:
            logger.error(f"Failed permanently: {request.url} - {error}")