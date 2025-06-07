#!/usr/bin/env python3
"""
₿ RadioX Bitcoin Service - Standalone CLI
Bitcoin price and Bitcoin data retrieval
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.bitcoin_service import BitcoinService


async def main():
    print("₿ BITCOIN SERVICE")
    print("=" * 30)
    
    service = BitcoinService()
    success = await service.test_connection()
    
    if success:
        # Show complete Bitcoin data
        price_data = await service.get_bitcoin_price()
        if price_data:
            print(f"₿ Bitcoin: ${price_data['price_usd']:,.2f}")
            print(f"📈 1h: {price_data.get('change_1h', 0):+.2f}%")
            print(f"📈 24h: {price_data['change_24h']:+.2f}%")
            print(f"📊 7d: {price_data['change_7d']:+.2f}%")
            print(f"📊 30d: {price_data.get('change_30d', 0):+.2f}%")
            print(f"📊 60d: {price_data.get('change_60d', 0):+.2f}%")
            print(f"📊 90d: {price_data.get('change_90d', 0):+.2f}%")
            print(f"💰 Market Cap: ${price_data['market_cap']:,.0f}")
            print(f"📦 Volume 24h: ${price_data['volume_24h']:,.0f}")
            
            # Trend Analysis
            trend = await service.get_bitcoin_trend()
            print(f"📈 Trend: {trend['formatted']}")
            
            # Radio Format (different timeframes)
            print(f"🎙️ 1h: {service.format_for_radio(price_data, '1h')}")
            print(f"🎙️ 24h: {service.format_for_radio(price_data, '24h')}")
            print(f"🎙️ 7d: {service.format_for_radio(price_data, '7d')}")
        else:
            print("❌ Bitcoin data not available")
    else:
        print("❌ CoinMarketCap API not reachable")
        print("💡 Check COINMARKETCAP_API_KEY in .env")


if __name__ == "__main__":
    asyncio.run(main()) 