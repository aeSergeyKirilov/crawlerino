import pytest
from unittest.mock import AsyncMock, patch
from crawlerino.agent import CrawlerAgent
from crawlerino.config import CrawlerConfig
from crawlerino.models import CrawlRequest

@pytest.fixture
def config():
    return CrawlerConfig(
        start_urls=["http://example.com"],
        allowed_domains=["example.com"],
        max_depth=1,
        concurrency_limit=2
    )

@pytest.mark.asyncio
async def test_agent_visits_url(config):
    agent = CrawlerAgent(config)
    
    # Mock the downloader to avoid real network calls
    with patch.object(agent.downloader, 'fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ("<html><body><a href='/page2'>Link</a></body></html>", "http://example.com")
        
        # Mock queue to stop infinite loop quickly
        call_count = 0
        
        async def mock_get():
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return CrawlRequest(url="http://example.com")
            return None
            
        agent.queue.get = mock_get
        
        await agent._process_request(CrawlRequest(url="http://example.com"))
        
        assert len(agent.results) == 1
        assert agent.results[0].url == "http://example.com"
        mock_fetch.assert_called_once()