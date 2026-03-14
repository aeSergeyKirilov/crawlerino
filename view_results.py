# view_results.py
import json
from pathlib import Path
from typing import Optional

def view_results(
    filepath: str = "output/results.json",
    limit: int = 10,
    filter_title: Optional[str] = None
):
    """Просмотр результатов краулинга в консоли."""
    
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Файл не найден: {filepath}")
        return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Фильтрация по заголовку
    if filter_title:
        data = [d for d in data if filter_title.lower() in (d.get("title") or "").lower()]
    
    print(f"📊 Crawlerino Results Viewer")
    print(f"📁 Файл: {filepath}")
    print(f"📄 Записей: {len(data)}")
    print(f"🔍 Фильтр: {filter_title or 'нет'}")
    print("=" * 70)
    
    for i, item in enumerate(data[:limit], 1):
        title = item.get("title") or "[no title]"
        url = item["url"]
        links_count = len(item.get("links_found", []))
        extracted = item.get("extracted_at", "")[:19]  # Обрезать время
        
        print(f"\n{i}. {title}")
        print(f"   🔗 {url}")
        print(f"   📎 Links: {links_count} | ⏰ {extracted}")
        
        # Показать первые 3 найденные ссылки
        if item.get("links_found"):
            print(f"   🔍 First links:")
            for link in item["links_found"][:3]:
                print(f"      • {link[:60]}...")
    
    if len(data) > limit:
        print(f"\n💡 Показано {limit} из {len(data)} записей")
        print(f"   Используйте limit=N для показа большего количества")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View crawler results")
    parser.add_argument("-f", "--file", default="output/results.json", help="Path to JSON file")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Number of results to show")
    parser.add_argument("-t", "--title", help="Filter by title substring")
    
    args = parser.parse_args()
    view_results(args.file, args.limit, args.title)