import asyncio
import logging
from crawlerino.agent import CrawlerAgent
from crawlerino.config import CrawlerConfig
import json

logging.basicConfig(level=logging.INFO)

async def main():
    config = CrawlerConfig(
        start_urls=["https://books.toscrape.com/"],
        allowed_domains=["books.toscrape.com"],
        max_depth=2,
        concurrency_limit=5
    )
    
    agent = CrawlerAgent(config)
    await agent.run()
    
    # Save results
    with open("results.json", "w") as f:
        data = [r.dict() for r in agent.results]
        json.dump(data, f, indent=2, default=str)
    
    print(f"Saved {len(agent.results)} records to results.json")

if __name__ == "__main__":
    asyncio.run(main())