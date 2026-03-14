from pydantic import BaseModel
from typing import List

class CrawlerConfig(BaseModel):
    start_urls: List[str]
    allowed_domains: List[str]
    max_depth: int = 3
    concurrency_limit: int = 5
    max_retries: int = 3
    use_playwright_for_js: bool = True