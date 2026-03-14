import pytest
from crawlerino.agent import CrawlerAgent
from crawlerino.config import CrawlerConfig

@pytest.fixture
def agent():
    config = CrawlerConfig(
        start_urls=["http://example.com"],
        allowed_domains=["example.com"]
    )
    return CrawlerAgent(config)

def test_parse_html_title(agent):
    """Test HTML title extraction."""
    html = "<html><head><title>Test Page</title></head><body></body></html>"
    data = agent._parse_html(html, "http://example.com")
    
    assert data.title == "Test Page"
    assert data.url == "http://example.com"

def test_parse_html_links(agent):
    """Test link extraction from HTML."""
    html = """
    <html>
        <body>
            <a href="/page1">Link 1</a>
            <a href="/page2">Link 2</a>
            <a href="https://external.com">External</a>
        </body>
    </html>
    """
    data = agent._parse_html(html, "http://example.com")
    
    assert len(data.links_found) >= 2
    assert "http://example.com/page1" in data.links_found
    assert "http://example.com/page2" in data.links_found

def test_parse_html_content_hash(agent):
    """Test content hash generation."""
    html = "<html><body>Unique Content</body></html>"
    data1 = agent._parse_html(html, "http://example.com")
    data2 = agent._parse_html(html, "http://example.com")
    
    assert data1.content_hash == data2.content_hash
    assert len(data1.content_hash) == 32  # MD5 hash length

def test_is_valid_domain(agent):
    """Test domain validation."""
    assert agent._is_valid_domain("http://example.com/page") is True
    assert agent._is_valid_domain("http://other.com/page") is False
    assert agent._is_valid_domain("https://example.com") is True