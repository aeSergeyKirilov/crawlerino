# test_run.py
import asyncio
import json
import logging
from pathlib import Path
from crawlerino.agent import CrawlerAgent
from crawlerino.config import CrawlerConfig

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

async def main():
    print("🚀 Запускаем Crawlerino...")
    
    # Конфигурация для тестового запуска
    config = CrawlerConfig(
        start_urls=["https://books.toscrape.com/"],
        allowed_domains=["books.toscrape.com"],
        max_depth=2,              # Не уходим слишком глубоко
        concurrency_limit=3,      # Ограничиваем параллелизм для теста
        max_retries=2
    )
    
    agent = CrawlerAgent(config)
    
    try:
        await agent.run()
    except KeyboardInterrupt:
        print("\n⚠️  Остановлено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        raise
    finally:
        await agent.downloader.close()
    
    # Сохраняем результаты
    results = [r.model_dump() for r in agent.results]
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # JSON export
    json_path = output_dir / "results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    # Parquet export (если есть pandas/pyarrow)
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        parquet_path = output_dir / "results.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"💾 Parquet: {parquet_path}")
    except ImportError:
        print("ℹ️  pandas/pyarrow не установлены, пропуск Parquet")
    
    # Статистика
    print(f"\n✅ Crawling finished!")
    print(f"📊 Processed: {len(agent.results)} pages")
    print(f"🔗 Unique URLs: {len(agent.visited_urls)}")
    print(f"💾 JSON: {json_path}")
    
    # Пример результатов
    if agent.results:
        print(f"\n📄 Sample entries:")
        for i, r in enumerate(agent.results[:3], 1):
            title = r.title or "[no title]"
            print(f"  {i}. {title[:50]}...")
            print(f"     {r.url}")
            print(f"     Links found: {len(r.links_found)}")

if __name__ == "__main__":
    asyncio.run(main())