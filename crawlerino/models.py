
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CrawlStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"

class CrawlRequest(BaseModel):
    url: HttpUrl
    priority: int = 0
    depth: int = 0
    retry_count: int = 0
    requires_js: bool = False
    
    class Config:
        arbitrary_types_allowed = True

class ExtractedData(BaseModel):
    url: str
    title: Optional[str] = None
    content_hash: str
    metadata: Dict[str, Any] = {}
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    links_found: List[str] = []