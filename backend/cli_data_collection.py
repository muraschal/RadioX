#!/usr/bin/env python3

"""
CLI Data Collection Tool
========================

Einfaches CLI Tool für die rohe Datensammlung.
Sammelt wertefrei alle verfügbaren Daten aus:
- RSS News (Show Preset basiert)
- Weather Data
- Bitcoin/Crypto Prices

Keine Bewertung, keine Filterung - nur sammeln!
"""

import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

# Import des Data Collection Service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.data_collection_service import DataCollectionService


class DataCollectionCLI:
    """
    CLI für rohe Datensammlung - wertefrei und einfach
    Sammelt ALLE verfügbaren Daten ohne Presets oder Filterung
    """
    
    def __init__(self):
        self.service = DataCollectionService()
    
    async def run_full_collection(self, max_age: int = 12) -> Dict[str, Any]:
        """
        Sammelt ALLE verfügbaren Daten
        """
        
        print(f"🔄 Sammle ALLE Daten (Max Age: {max_age}h)...")
        
        try:
            data = await self.service.collect_all_data(max_age_hours=max_age)
            
            print(f"✅ Datensammlung abgeschlossen!")
            return data
            
        except Exception as e:
            print(f"❌ Fehler bei Datensammlung: {e}")
            logger.error(f"CLI Full Collection Fehler: {e}")
            return {}
    
    async def run_news_only(self, max_age: int = 12) -> Dict[str, Any]:
        """
        Sammelt nur RSS News - ALLE verfügbaren
        """
        
        print(f"📰 Sammle ALLE RSS News (Max Age: {max_age}h)...")
        
        try:
            data = await self.service.collect_news_only(max_age_hours=max_age)
            
            print(f"✅ News-Sammlung abgeschlossen!")
            return data
            
        except Exception as e:
            print(f"❌ Fehler bei News-Sammlung: {e}")
            logger.error(f"CLI News Collection Fehler: {e}")
            return {}
    
    async def run_context_only(self, location: str = "Zürich") -> Dict[str, Any]:
        """
        Sammelt nur Kontext-Daten (Weather + Crypto)
        """
        
        print(f"🌍 Sammle Kontext-Daten für '{location}'...")
        
        try:
            data = await self.service.collect_context_data(location=location)
            
            print(f"✅ Kontext-Sammlung abgeschlossen!")
            return data
            
        except Exception as e:
            print(f"❌ Fehler bei Kontext-Sammlung: {e}")
            logger.error(f"CLI Context Collection Fehler: {e}")
            return {}
    
    async def test_connections(self) -> Dict[str, bool]:
        """
        Testet alle Datenquellen-Verbindungen
        """
        
        print("🔧 Teste alle Datenquellen...")
        
        try:
            results = await self.service.test_connections()
            
            print("✅ Verbindungstests abgeschlossen!")
            return results
            
        except Exception as e:
            print(f"❌ Fehler bei Verbindungstests: {e}")
            logger.error(f"CLI Connection Test Fehler: {e}")
            return {}
    
    def display_results(self, data: Dict[str, Any], output_format: str = "summary"):
        """
        Zeigt gesammelte Daten an
        """
        
        if not data:
            print("❌ Keine Daten verfügbar")
            return
        
        if output_format == "json":
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
            return
        
        # Summary Format
        print("\n" + "="*50)
        print("📊 DATENSAMMLUNG ERGEBNISSE")
        print("="*50)
        
        # Timestamp
        if "collection_timestamp" in data:
            print(f"⏰ Zeitstempel: {data['collection_timestamp']}")
        
        # Max Age Info
        if "max_age_hours" in data:
            print(f"📅 Max Age: {data['max_age_hours']}h")
        
        # News
        if "news" in data and data["news"]:
            print(f"\n📰 News: {len(data['news'])} Artikel gefunden")
            for i, news_item in enumerate(data["news"][:3], 1):  # Nur erste 3 anzeigen
                # JSON-Dictionary statt RSSNewsItem Objekt
                title = news_item.get('title', 'Kein Titel')[:60]
                source = news_item.get('source', 'Unknown')
                category = news_item.get('category', 'general')
                link = news_item.get('link', '')
                print(f"   {i}. [{category}] {title}... ({source})")
                if link:
                    print(f"      🔗 {link}")
        
        # Weather - wieder einfaches Zürich Wetter
        if "weather" in data and data["weather"]:
            weather = data["weather"]
            temp = weather.get("temperature", "N/A")
            desc = weather.get("description", "N/A")
            location = weather.get("location", "Zürich")
            print(f"\n🌤️ Wetter {location}: {temp}°C, {desc}")
        
        # Crypto - Dict mit Bitcoin + Trend
        if "crypto" in data and data["crypto"]:
            crypto_data = data["crypto"]
            if "bitcoin" in crypto_data:
                bitcoin = crypto_data["bitcoin"]
                price = bitcoin.get("price_usd", "N/A")
                change_24h = bitcoin.get("change_24h", 0)
                print(f"\n₿ Bitcoin: ${price:,.0f} ({change_24h:+.1f}%)")
                
                # Trend anzeigen wenn verfügbar
                if "trend" in crypto_data and crypto_data["trend"]:
                    trend = crypto_data["trend"]
                    trend_msg = trend.get("formatted", "")
                    if trend_msg:
                        print(f"   📈 Trend: {trend_msg}")
        
        print("\n" + "="*50)
    
    def display_test_results(self, results: Dict[str, bool]):
        """
        Zeigt Verbindungstest-Ergebnisse an
        """
        
        print("\n" + "="*40)
        print("🔧 VERBINDUNGSTEST ERGEBNISSE")
        print("="*40)
        
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            service_name = service.replace("_", " ").title()
            print(f"{status_icon} {service_name}")
        
        print("="*40)


async def main():
    """
    Hauptfunktion für CLI
    """
    
    parser = argparse.ArgumentParser(
        description="RadioX Data Collection CLI - Sammelt ALLE verfügbaren Daten ohne Bewertung"
    )
    
    parser.add_argument(
        "--max-age", 
        type=int, 
        default=12,
        help="Maximales Alter der News in Stunden (default: 12)"
    )
    
    parser.add_argument(
        "--location", 
        default="Zürich",
        help="Location für Wetterdaten (default: Zürich)"
    )
    
    parser.add_argument(
        "--news-only", 
        action="store_true",
        help="Sammle nur RSS News (ALLE verfügbaren)"
    )
    
    parser.add_argument(
        "--context-only", 
        action="store_true",
        help="Sammle nur Kontext-Daten (Weather + Crypto)"
    )
    
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Teste alle Datenquellen-Verbindungen"
    )
    
    parser.add_argument(
        "--format", 
        choices=["summary", "json"],
        default="summary",
        help="Ausgabeformat (default: summary)"
    )
    
    args = parser.parse_args()
    
    # CLI initialisieren
    cli = DataCollectionCLI()
    
    try:
        # Verschiedene Modi
        if args.test:
            results = await cli.test_connections()
            cli.display_test_results(results)
            
        elif args.news_only:
            data = await cli.run_news_only(args.max_age)
            cli.display_results(data, args.format)
            
        elif args.context_only:
            data = await cli.run_context_only(args.location)
            cli.display_results(data, args.format)
            
        else:
            # Full Collection (default)
            data = await cli.run_full_collection(args.max_age)
            cli.display_results(data, args.format)
    
    except KeyboardInterrupt:
        print("\n⏹️  Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        logger.error(f"CLI Main Fehler: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 