#!/usr/bin/env python3

"""
CoinMarketCap API Service für RadioX
Holt aktuelle Bitcoin Preise und Crypto Market Data
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
from dataclasses import dataclass
from pathlib import Path

# Load .env from ROOT directory (not backend!)
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

@dataclass
class CryptoPrice:
    """Crypto Price Data"""
    symbol: str
    name: str
    price_usd: float
    price_chf: float
    change_24h: float
    market_cap: float
    volume_24h: float
    last_updated: datetime

class CoinMarketCapService:
    """Service für CoinMarketCap API Integration"""
    
    def __init__(self):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.api_key = os.getenv("COINMARKETCAP_API_KEY")
        self.session = None
        
        # Fallback: Free API endpoint (ohne API Key)
        self.free_base_url = "https://api.coinmarketcap.com/v1"
        
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_bitcoin_price(self) -> Optional[CryptoPrice]:
        """Holt aktuellen Bitcoin Preis in USD und CHF"""
        try:
            # Primär: CoinGecko API (kostenlos, kein API Key nötig)
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin',
                'vs_currencies': 'usd,chf',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    btc_data = data['bitcoin']
                    
                    return CryptoPrice(
                        symbol="BTC",
                        name="Bitcoin",
                        price_usd=btc_data['usd'],
                        price_chf=btc_data['chf'],
                        change_24h=btc_data['usd_24h_change'],
                        market_cap=btc_data.get('usd_market_cap', 0),
                        volume_24h=btc_data.get('usd_24h_vol', 0),
                        last_updated=datetime.now()
                    )
                else:
                    self.logger.error(f"CoinGecko API Error: {response.status}")
                    return await self._fallback_coinmarketcap()
                    
        except Exception as e:
            self.logger.error(f"Error fetching Bitcoin price from CoinGecko: {e}")
            return await self._fallback_coinmarketcap()
    
    async def _fallback_coinmarketcap(self) -> Optional[CryptoPrice]:
        """Fallback zu CoinMarketCap Free API"""
        try:
            url = "https://api.coinmarketcap.com/v1/ticker/bitcoin/"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    btc_data = data[0]
                    price_usd = float(btc_data['price_usd'])
                    
                    return CryptoPrice(
                        symbol="BTC",
                        name="Bitcoin",
                        price_usd=price_usd,
                        price_chf=price_usd * 0.82,  # Approximation USD->CHF
                        change_24h=float(btc_data['percent_change_24h']),
                        market_cap=float(btc_data['market_cap_usd']),
                        volume_24h=float(btc_data['24h_volume_usd']),
                        last_updated=datetime.now()
                    )
                else:
                    self.logger.error(f"CoinMarketCap Fallback API Error: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Fallback CoinMarketCap error: {e}")
            return None
    
    async def get_top_cryptos(self, limit: int = 10) -> List[CryptoPrice]:
        """Holt Top Crypto Currencies"""
        try:
            if self.api_key:
                url = f"{self.base_url}/cryptocurrency/listings/latest"
                headers = {
                    'X-CMC_PRO_API_KEY': self.api_key,
                    'Accept': 'application/json'
                }
                params = {
                    'start': '1',
                    'limit': str(limit),
                    'convert': 'USD'
                }
            else:
                # Free API
                url = f"https://api.coinmarketcap.com/v1/ticker/?limit={limit}"
                headers = {'Accept': 'application/json'}
                params = {}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    cryptos = []
                    
                    if self.api_key:
                        # Pro API
                        for crypto in data['data']:
                            quote = crypto['quote']['USD']
                            cryptos.append(CryptoPrice(
                                symbol=crypto['symbol'],
                                name=crypto['name'],
                                price_usd=quote['price'],
                                price_chf=quote['price'] * 0.82,
                                change_24h=quote['percent_change_24h'],
                                market_cap=quote['market_cap'],
                                volume_24h=quote['volume_24h'],
                                last_updated=datetime.now()
                            ))
                    else:
                        # Free API
                        for crypto in data:
                            price_usd = float(crypto['price_usd'])
                            cryptos.append(CryptoPrice(
                                symbol=crypto['symbol'],
                                name=crypto['name'],
                                price_usd=price_usd,
                                price_chf=price_usd * 0.82,
                                change_24h=float(crypto['percent_change_24h']),
                                market_cap=float(crypto['market_cap_usd']),
                                volume_24h=float(crypto['24h_volume_usd']),
                                last_updated=datetime.now()
                            ))
                    
                    return cryptos
                else:
                    self.logger.error(f"CoinMarketCap API Error: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching top cryptos: {e}")
            return []
    
    def format_bitcoin_news_text(self, btc_price: CryptoPrice) -> str:
        """Formatiert Bitcoin Preis für Radio News"""
        try:
            change_text = "gestiegen" if btc_price.change_24h > 0 else "gefallen"
            change_abs = abs(btc_price.change_24h)
            
            # Formatiere Preis schön
            price_usd_formatted = f"{btc_price.price_usd:,.0f}".replace(",", "'")
            price_chf_formatted = f"{btc_price.price_chf:,.0f}".replace(",", "'")
            
            text = f"Bitcoin steht aktuell bei {price_usd_formatted} US-Dollar, "
            text += f"das sind umgerechnet etwa {price_chf_formatted} Schweizer Franken. "
            text += f"In den letzten 24 Stunden ist der Kurs um {change_abs:.1f} Prozent {change_text}."
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error formatting Bitcoin news: {e}")
            return "Bitcoin Preis konnte nicht abgerufen werden."

# Test Funktion
async def test_coinmarketcap_service():
    """Test der CoinMarketCap Service"""
    async with CoinMarketCapService() as cmc:
        print("🪙 COINMARKETCAP SERVICE TEST")
        print("=" * 50)
        
        # Bitcoin Preis
        btc = await cmc.get_bitcoin_price()
        if btc:
            print(f"✅ Bitcoin: ${btc.price_usd:,.2f} USD (CHF {btc.price_chf:,.2f})")
            print(f"   24h Change: {btc.change_24h:+.2f}%")
            print(f"   Radio Text: {cmc.format_bitcoin_news_text(btc)}")
        else:
            print("❌ Bitcoin Preis konnte nicht abgerufen werden")
        
        # Top 5 Cryptos
        print("\n📊 Top 5 Cryptocurrencies:")
        top_cryptos = await cmc.get_top_cryptos(5)
        for crypto in top_cryptos:
            print(f"   {crypto.symbol}: ${crypto.price_usd:,.2f} ({crypto.change_24h:+.1f}%)")

if __name__ == "__main__":
    asyncio.run(test_coinmarketcap_service()) 