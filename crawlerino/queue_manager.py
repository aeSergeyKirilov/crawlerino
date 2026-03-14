import asyncio
from typing import Optional
from crawlerino.models import CrawlRequest
import heapq

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._counter = 0
        self._lock = asyncio.Lock()

    async def put(self, request: CrawlRequest) -> None:
        """Add a request to the queue. Lower priority number = higher priority."""
        async with self._lock:
            # Heapq is a min-heap, so we use (priority, counter, item)
            # Counter ensures FIFO for same priority
            entry = (request.priority, self._counter, request)
            self._counter += 1
            heapq.heappush(self._queue, entry)

    async def get(self) -> Optional[CrawlRequest]:
        """Get the highest priority request."""
        async with self._lock:
            if not self._queue:
                return None
            _, _, request = heapq.heappop(self._queue)
            return request

    async def empty(self) -> bool:
        async with self._lock:
            return len(self._queue) == 0