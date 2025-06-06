#!/usr/bin/env python3
"""
₿ RadioX Crypto Service - Standalone CLI
Bitcoin-Preis und Crypto-Daten abrufen
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from services.crypto_service import CoinMarketCapService


async def main():
    parser = argparse.ArgumentParser(description="₿ RadioX Crypto Service")
    parser.add_argument("--action", required=True, choices=[
        "bitcoin", "price", "test", "formatted", "trend"
    ], help="Aktion")
    
    args = parser.parse_args()
    
    print("₿ CRYPTO SERVICE STANDALONE")
    print("=" * 50)
    
    service = CoinMarketCapService()
    
    if args.action == "bitcoin" or args.action == "price":
        print("₿ Hole aktuellen Bitcoin-Preis...")
        price_data = await service.get_bitcoin_price()
        
        if price_data:
            print(f"✅ Bitcoin-Preis: ${price_data['price']:,.2f}")
            print(f"📈 24h Änderung: {price_data['change_24h']:+.2f}%")
            print(f"📊 Marktkappe: ${price_data['market_cap']:,.0f}")
            print(f"📅 Letztes Update: {price_data['last_updated']}")
        else:
            print("❌ Fehler beim Abrufen des Bitcoin-Preises")
            
    elif args.action == "formatted":
        print("₿ Formatierte Bitcoin-Daten für Radio...")
        formatted = await service.get_formatted_bitcoin_data()
        
        if formatted:
            print(f"🎙️ Radio-Format: {formatted['formatted']}")
            print(f"📊 Raw Data: ${formatted['raw_price']:,.2f}")
            print(f"📈 Trend: {formatted['trend']}")
        else:
            print("❌ Fehler beim Formatieren der Bitcoin-Daten")
            
    elif args.action == "trend":
        print("📈 Bitcoin-Trend-Analyse...")
        price_data = await service.get_bitcoin_price()
        
        if price_data:
            change = price_data['change_24h']
            
            if change > 5:
                trend = "🚀 MOON! Starker Anstieg"
            elif change > 2:
                trend = "📈 Bullish! Guter Anstieg"
            elif change > 0:
                trend = "📊 Leicht positiv"
            elif change > -2:
                trend = "📉 Leicht negativ"
            elif change > -5:
                trend = "🔻 Bearish! Deutlicher Rückgang"
            else:
                trend = "💥 CRASH! Starker Rückgang"
                
            print(f"₿ Bitcoin: ${price_data['price']:,.0f}")
            print(f"📈 24h: {change:+.2f}%")
            print(f"🎯 Trend: {trend}")
        else:
            print("❌ Fehler beim Abrufen der Trend-Daten")
            
    elif args.action == "test":
        print("🧪 Teste Crypto Service...")
        success = await service.test_connection()
        
        if success:
            print("✅ Crypto Service funktioniert")
            print("✅ API-Verbindung erfolgreich")
        else:
            print("❌ Crypto Service Test fehlgeschlagen")
            print("💡 Prüfe COINMARKETCAP_API_KEY in .env")


if __name__ == "__main__":
    asyncio.run(main()) 