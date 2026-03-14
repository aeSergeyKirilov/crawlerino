import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from crawlerino.downloader import Downloader
from crawlerino.models import CrawlRequest

@pytest.fixture
def downloader():
    return Downloader()

# tests/test_downloader.py - ЗАМЕНИТЕ тест на этот вариант

@pytest.mark.asyncio
async def test_fetch_with_aiohttp(downloader):
    """Test static HTML fetching with aiohttp."""
    request = CrawlRequest(url="http://example.com", requires_js=False)
    
    # Создаём моки с правильной асинхронной цепочкой
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
    mock_response.url = "http://example.com"
    mock_response.raise_for_status = MagicMock()
    
    # Mock для async with session.get() as response:
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    
    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_get_context)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        content, url = await downloader.fetch(request)
        
        # Проверяем функциональный результат (главное!)
        assert "Test" in content
        assert str(url) in ["http://example.com", "http://example.com/"]
        
        # Проверяем, что get() был вызван (без строгой проверки аргументов)
        mock_session.get.assert_called_once()
        
        # Опционально: проверяем, что первый аргумент содержит домен
        call_args = mock_session.get.call_args[0]
        assert "example.com" in call_args[0]

@pytest.mark.asyncio
async def test_fetch_with_playwright(downloader):
    """Test dynamic content fetching with Playwright mock."""
    request = CrawlRequest(url="http://example.com", requires_js=True)
    
    mock_page = AsyncMock()
    mock_page.content = AsyncMock(return_value="<html><body>JS Content</body></html>")
    mock_page.url = "http://example.com"
    mock_page.goto = AsyncMock()
    mock_page.close = AsyncMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.__aenter__ = AsyncMock(return_value=mock_context)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    
    mock_browser = AsyncMock()
    mock_browser.new_context = MagicMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    downloader._browser = mock_browser
    
    content, url = await downloader.fetch(request)
    
    assert "JS Content" in content
    mock_page.goto.assert_called_once()

@pytest.mark.asyncio
async def test_downloader_close(downloader):
    """Test browser cleanup."""
    mock_browser = AsyncMock()
    downloader._browser = mock_browser
    
    await downloader.close()
    
    mock_browser.close.assert_called_once()