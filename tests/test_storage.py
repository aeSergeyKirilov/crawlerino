import pytest
import json
import tempfile
import os
from pathlib import Path

@pytest.fixture
def sample_data():
    return [
        {
            "url": "http://example.com",
            "title": "Test Page",
            "content_hash": "abc123",
            "meta": {},
            "links_found": []
        }
    ]

def test_save_json(sample_data):
    """Test JSON export."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_path = f.name
    
    try:
        with open(temp_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert len(loaded) == 1
        assert loaded[0]["url"] == "http://example.com"
    finally:
        os.unlink(temp_path)