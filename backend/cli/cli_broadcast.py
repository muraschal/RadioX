#!/usr/bin/env python3
"""
🎭 RadioX Broadcast Generation Service - Standalone CLI
Generiere und teste Broadcast-Skripte
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from services.broadcast_generation_service import BroadcastGenerationService


async def main():
    parser = argparse.ArgumentParser(description="🎭 RadioX Broadcast Generation Service")
    parser.add_argument("--action", required=True, choices=[
        "test", "generate", "styles", "quick", "demo"
    ], help="Aktion")
    parser.add_argument("--channel", default="zurich", help="Kanal (zurich, basel, bern)")
    parser.add_argument("--language", choices=["en", "de"], default="en", help="Sprache")
    parser.add_argument("--time", help="Zielzeit (HH:MM)")
    parser.add_argument("--news-count", type=int, default=3, help="Anzahl News")
    
    args = parser.parse_args()
    
    print("🎭 BROADCAST GENERATION SERVICE STANDALONE")
    print("=" * 50)
    
    service = BroadcastGenerationService()
    
    if args.action == "styles":
        print("🎭 Verfügbare Broadcast-Stile:")
        for style_name, config in service.broadcast_styles.items():
            print(f"\n📻 {style_name.upper()}")
            print(f"   Name: {config['name']}")
            print(f"   Beschreibung: {config['description']}")
            print(f"   Marcel: {config['marcel_mood']}")
            print(f"   Jarvis: {config['jarvis_mood']}")
            print(f"   Tempo: {config['tempo']}")
            print(f"   Dauer: {config['duration_target']} Min")
            if 'v3_style' in config:
                print(f"   V3 Style: {config['v3_style']}")
                
    elif args.action == "test":
        print("🧪 Teste Broadcast Generation Service...")
        success = await service.test_generation()
        
        if success:
            print("✅ Broadcast Generation Test erfolgreich")
        else:
            print("❌ Broadcast Generation Test fehlgeschlagen")
            print("💡 Prüfe OpenAI API Key und Supabase Verbindung")
            
    elif args.action == "quick":
        print(f"⚡ Quick Broadcast für '{args.channel}'...")
        result = await service.generate_quick_broadcast(
            news_count=args.news_count,
            channel=args.channel
        )
        
        if result.get('session_id'):
            print(f"✅ Quick Broadcast generiert!")
            print(f"📁 Session ID: {result['session_id']}")
            print(f"🎭 Stil: {result['broadcast_style']}")
            print(f"⏱️ Dauer: {result['estimated_duration_minutes']} Min")
            print(f"\n📝 Script Preview:")
            script_lines = result['script_content'].split('\n')[:6]
            for line in script_lines:
                if line.strip():
                    print(f"   {line}")
            if len(result['script_content'].split('\n')) > 6:
                print("   ...")
        else:
            print("❌ Fehler beim Generieren des Quick Broadcasts")
            
    elif args.action == "demo":
        print("🎭 Demo: V3 English Broadcast mit Mock-Daten...")
        
        # Mock Content für Demo
        demo_content = {
            "selected_news": [
                {
                    "title": "Bitcoin Reaches New All-Time High Above $100,000",
                    "summary": "Bitcoin breaks through the psychological $100,000 barrier amid institutional adoption and ETF inflows.",
                    "primary_category": "bitcoin_crypto",
                    "source_name": "CoinTelegraph",
                    "hours_old": 1
                },
                {
                    "title": "Swiss National Bank Announces Digital Currency Research",
                    "summary": "SNB reveals plans for comprehensive digital franc pilot program starting 2024.",
                    "primary_category": "wirtschaft",
                    "source_name": "NZZ",
                    "hours_old": 2
                },
                {
                    "title": "Zurich Tech Hub Attracts Major AI Investment",
                    "summary": "New AI research center announced with CHF 500 million funding from international investors.",
                    "primary_category": "technologie",
                    "source_name": "Tages-Anzeiger",
                    "hours_old": 3
                }
            ],
            "context_data": {
                "weather": {"formatted": "18°C, partly cloudy in Zurich"},
                "crypto": {"formatted": "$103,091 (+2.8%)"}
            }
        }
        
        print("🎤 Generiere Demo Broadcast...")
        result = await service.generate_broadcast(
            content=demo_content,
            target_time=args.time,
            channel=args.channel,
            language=args.language
        )
        
        if result.get('session_id'):
            print(f"✅ Demo Broadcast generiert!")
            print(f"📁 Session ID: {result['session_id']}")
            print(f"🎭 Stil: {result['broadcast_style']}")
            print(f"⏱️ Dauer: {result['estimated_duration_minutes']} Min")
            print(f"🌐 Sprache: {'English V3' if args.language == 'en' else 'Deutsch'}")
            
            print(f"\n📝 Generated Script:")
            print("-" * 40)
            script_lines = result['script_content'].split('\n')[:15]
            for line in script_lines:
                if line.strip():
                    print(line)
            if len(result['script_content'].split('\n')) > 15:
                print("\n... (script continues) ...")
        else:
            print("❌ Fehler beim Generieren des Demo Broadcasts")
            
    elif args.action == "generate":
        print("🎭 Broadcast Generation - benötigt echte News-Daten")
        print("💡 Verwende stattdessen --action demo für einen Test")
        print("💡 Oder nutze den radiox_master.py für komplette Generierung")


if __name__ == "__main__":
    asyncio.run(main()) 