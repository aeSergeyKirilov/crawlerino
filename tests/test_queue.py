import pytest
from crawlerino.queue_manager import PriorityQueue
from crawlerino.models import CrawlRequest

# tests/test_queue.py - ЗАМЕНИТЕ функции test_queue_priority и test_queue_fifo

@pytest.mark.asyncio
async def test_queue_priority():
    """Test that higher priority items are retrieved first."""
    queue = PriorityQueue()
    
    await queue.put(CrawlRequest(url="http://example.com/low", priority=10))
    await queue.put(CrawlRequest(url="http://example.com/high", priority=1))
    await queue.put(CrawlRequest(url="http://example.com/med", priority=5))
    
    first = await queue.get()
    # Исправление: преобразуем HttpUrl в строку
    assert str(first.url) == "http://example.com/high"
    assert first.priority == 1

@pytest.mark.asyncio
async def test_queue_fifo():
    """Test FIFO order for same priority."""
    queue = PriorityQueue()
    
    await queue.put(CrawlRequest(url="http://example.com/first", priority=5))
    await queue.put(CrawlRequest(url="http://example.com/second", priority=5))
    
    first = await queue.get()
    second = await queue.get()
    
    # Исправление: преобразуем HttpUrl в строку
    assert str(first.url) == "http://example.com/first"
    assert str(second.url) == "http://example.com/second"
    
@pytest.mark.asyncio
async def test_queue_empty():
    """Test empty queue behavior."""
    queue = PriorityQueue()
    assert await queue.empty() is True
    
    await queue.put(CrawlRequest(url="http://example.com"))
    assert await queue.empty() is False