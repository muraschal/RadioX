#!/usr/bin/env python3
"""
🔗 RadioX RSS Service - Standalone CLI
Teste und verwende den RSS Service separat
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from services.rss_service import RSSService, get_crypto_news, get_tech_news


async def main():
    parser = argparse.ArgumentParser(description="🔗 RadioX RSS Service")
    parser.add_argument("--action", required=True, choices=[
        "feeds", "news", "crypto", "tech", "sources", "test"
    ], help="Aktion")
    parser.add_argument("--channel", default="zurich", help="Kanal (zurich, basel, bern)")
    parser.add_argument("--hours", type=int, default=6, help="Stunden zurück")
    parser.add_argument("--limit", type=int, default=5, help="Max. Anzahl")
    
    args = parser.parse_args()
    
    print("🔗 RSS SERVICE STANDALONE")
    print("=" * 50)
    
    service = RSSService()
    
    if args.action == "sources":
        print("📡 Konfigurierte RSS Quellen:")
        for source_name, config in service.rss_feeds.items():
            print(f"\n📰 {source_name.upper()} (P{config['priority']})")
            for category, url in config['feeds'].items():
                print(f"  • {category}: {url[:50]}...")
                
    elif args.action == "feeds":
        print(f"📡 Feeds für Kanal '{args.channel}':")
        feeds = await service.get_feeds_for_channel(args.channel)
        for i, feed in enumerate(feeds, 1):
            print(f"{i:2d}. {feed['source_name']} ({feed['feed_category']})")
            print(f"    📊 P{feed['priority']} | W{feed['weight']}")
                
    elif args.action == "news":
        print(f"📰 News für '{args.channel}' (letzte {args.hours}h)...")
        news = await service.get_recent_news(args.channel, args.hours)
        
        if not news:
            print("⚠️ Keine aktuellen News gefunden")
            print("💡 Versuche --hours 24 für mehr News")
            return
            
        print(f"✅ {len(news)} News gefunden:")
        for i, article in enumerate(news[:args.limit], 1):
            print(f"\n{i:2d}. [{article.category}] {article.title}")
            print(f"    📰 {article.source} | 🎯 P{article.priority}")
            print(f"    📝 {article.summary[:80]}...")
            
    elif args.action == "crypto":
        print("₿ Bitcoin/Crypto News:")
        news = await get_crypto_news()
        for i, article in enumerate(news[:args.limit], 1):
            print(f"{i:2d}. {article.title}")
            print(f"    📰 {article.source} | 🎯 P{article.priority}")
            
    elif args.action == "tech":
        print("💻 Tech News:")
        news = await get_tech_news()
        for i, article in enumerate(news[:args.limit], 1):
            print(f"{i:2d}. {article.title}")
            print(f"    📰 {article.source} | 🎯 P{article.priority}")
            
    elif args.action == "test":
        print("🧪 Teste RSS Feeds...")
        success = await service.test_rss_feeds()
        print(f"✅ Test {'erfolgreich' if success else 'fehlgeschlagen'}")


if __name__ == "__main__":
    asyncio.run(main()) 