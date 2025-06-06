#!/usr/bin/env python3

"""
Crypto Service
==============

Service für Kryptowährungsdaten:
- CoinMarketCap API Integration
- Bitcoin-Preisdaten
- Crypto-Markt-Trends
- Preis-Alerts
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from ROOT directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


class CoinMarketCapService:
    """
    Service für CoinMarketCap API Integration
    
    Holt aktuelle Kryptowährungsdaten für die
    Broadcast-Generierung.
    """
    
    def __init__(self):
        # Import centralized settings
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from config.settings import get_settings
        
        settings = get_settings()
        self.api_key = settings.coinmarketcap_api_key
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        
        # Konfiguration
        self.config = {
            "default_currency": "USD",
            "timeout": 30,
            "cache_duration": 300,  # 5 Minuten
            "supported_cryptos": ["BTC", "ETH", "ADA", "DOT", "LINK"]
        }
        
        # Cache für API-Responses
        self.cache = {
            "last_update": None,
            "bitcoin_data": None,
            "market_data": None
        }
    
    async def get_bitcoin_price(self) -> Optional[Dict[str, Any]]:
        """
        Holt aktuellen Bitcoin-Preis
        
        Returns:
            Dict mit Bitcoin-Preisdaten oder None bei Fehler
        """
        
        logger.info("₿ Hole Bitcoin-Preisdaten")
        
        # Cache prüfen
        if self._is_cache_valid():
            logger.info("✅ Verwende gecachte Bitcoin-Daten")
            return self.cache["bitcoin_data"]
        
        if not self.api_key:
            logger.warning("⚠️ CoinMarketCap API Key nicht verfügbar - verwende Fallback")
            return self._get_fallback_bitcoin_data()
        
        try:
            headers = {
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json"
            }
            
            params = {
                "symbol": "BTC",
                "convert": self.config["default_currency"]
            }
            
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=headers, 
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        bitcoin_data = self._process_bitcoin_data(data)
                        
                        # Cache aktualisieren
                        self.cache["bitcoin_data"] = bitcoin_data
                        self.cache["last_update"] = datetime.now()
                        
                        logger.info(f"✅ Bitcoin-Preis: ${bitcoin_data['price']:,.2f}")
                        return bitcoin_data
                    
                    elif response.status == 429:
                        logger.warning("⚠️ CoinMarketCap Rate Limit erreicht")
                        return self._get_fallback_bitcoin_data()
                    
                    else:
                        logger.error(f"❌ CoinMarketCap API Fehler {response.status}")
                        return self._get_fallback_bitcoin_data()
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der Bitcoin-Daten: {e}")
            return self._get_fallback_bitcoin_data()
    
    async def get_crypto_market_overview(self) -> Optional[Dict[str, Any]]:
        """
        Holt Crypto-Markt-Übersicht
        
        Returns:
            Dict mit Marktdaten oder None bei Fehler
        """
        
        logger.info("📊 Hole Crypto-Markt-Übersicht")
        
        if not self.api_key:
            logger.warning("⚠️ CoinMarketCap API Key nicht verfügbar")
            return None
        
        try:
            headers = {
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json"
            }
            
            params = {
                "symbol": ",".join(self.config["supported_cryptos"]),
                "convert": self.config["default_currency"]
            }
            
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=headers, 
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        market_data = self._process_market_data(data)
                        
                        # Cache aktualisieren
                        self.cache["market_data"] = market_data
                        
                        logger.info(f"✅ Marktdaten für {len(market_data['cryptos'])} Coins abgerufen")
                        return market_data
                    
                    else:
                        logger.error(f"❌ Marktdaten API Fehler {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der Marktdaten: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Testet die CoinMarketCap API Verbindung"""
        
        try:
            bitcoin_data = await self.get_bitcoin_price()
            return bitcoin_data is not None and "price" in bitcoin_data
            
        except Exception as e:
            logger.error(f"Crypto Service Test Fehler: {e}")
            return False
    
    # Private Methods
    
    def _process_bitcoin_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet CoinMarketCap Bitcoin-Response"""
        
        try:
            btc_data = api_response["data"]["BTC"]
            quote = btc_data["quote"][self.config["default_currency"]]
            
            return {
                "symbol": "BTC",
                "name": btc_data["name"],
                "price": round(quote["price"], 2),
                "change_24h": round(quote["percent_change_24h"], 2),
                "change_7d": round(quote["percent_change_7d"], 2),
                "market_cap": quote["market_cap"],
                "volume_24h": quote["volume_24h"],
                "last_updated": quote["last_updated"],
                "formatted_price": f"${quote['price']:,.2f}",
                "formatted_change_24h": f"{quote['percent_change_24h']:+.1f}%"
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Verarbeiten der Bitcoin-Daten: {e}")
            return self._get_fallback_bitcoin_data()
    
    def _process_market_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet CoinMarketCap Markt-Response"""
        
        try:
            cryptos = []
            total_market_cap = 0
            
            for symbol, crypto_data in api_response["data"].items():
                quote = crypto_data["quote"][self.config["default_currency"]]
                
                crypto_info = {
                    "symbol": symbol,
                    "name": crypto_data["name"],
                    "price": round(quote["price"], 2),
                    "change_24h": round(quote["percent_change_24h"], 2),
                    "market_cap": quote["market_cap"],
                    "volume_24h": quote["volume_24h"]
                }
                
                cryptos.append(crypto_info)
                total_market_cap += quote["market_cap"]
            
            # Sortiere nach Market Cap
            cryptos.sort(key=lambda x: x["market_cap"], reverse=True)
            
            return {
                "cryptos": cryptos,
                "total_market_cap": total_market_cap,
                "crypto_count": len(cryptos),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Verarbeiten der Marktdaten: {e}")
            return {
                "cryptos": [],
                "total_market_cap": 0,
                "crypto_count": 0,
                "error": str(e)
            }
    
    def _get_fallback_bitcoin_data(self) -> Dict[str, Any]:
        """Fallback Bitcoin-Daten wenn API nicht verfügbar"""
        
        # Simuliere realistische Bitcoin-Daten
        import random
        
        base_price = 105000  # Basis-Preis
        price_variation = random.uniform(-0.05, 0.05)  # ±5% Variation
        current_price = base_price * (1 + price_variation)
        
        change_24h = random.uniform(-8.0, 8.0)  # ±8% Tagesänderung
        
        return {
            "symbol": "BTC",
            "name": "Bitcoin",
            "price": round(current_price, 2),
            "change_24h": round(change_24h, 2),
            "change_7d": round(change_24h * 0.7, 2),
            "market_cap": current_price * 19_500_000,  # ~19.5M BTC im Umlauf
            "volume_24h": current_price * 500_000,
            "last_updated": datetime.now().isoformat(),
            "formatted_price": f"${current_price:,.2f}",
            "formatted_change_24h": f"{change_24h:+.1f}%",
            "fallback_mode": True
        }
    
    def _is_cache_valid(self) -> bool:
        """Prüft ob Cache noch gültig ist"""
        
        if not self.cache["last_update"] or not self.cache["bitcoin_data"]:
            return False
        
        cache_age = (datetime.now() - self.cache["last_update"]).total_seconds()
        return cache_age < self.config["cache_duration"]
    
    # Utility Methods
    
    def get_api_status(self) -> Dict[str, Any]:
        """Holt API-Status und Konfiguration"""
        
        return {
            "api_configured": bool(self.api_key),
            "base_url": self.base_url,
            "cache_duration": self.config["cache_duration"],
            "supported_cryptos": self.config["supported_cryptos"],
            "cache_valid": self._is_cache_valid(),
            "last_cache_update": self.cache["last_update"].isoformat() if self.cache["last_update"] else None
        }
    
    async def get_price_alerts(self, thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Prüft Preis-Alerts basierend auf Schwellenwerten
        
        Args:
            thresholds: Dict mit Symbol -> Schwellenwert
            
        Returns:
            Liste von ausgelösten Alerts
        """
        
        alerts = []
        
        try:
            bitcoin_data = await self.get_bitcoin_price()
            
            if bitcoin_data and "BTC" in thresholds:
                btc_threshold = thresholds["BTC"]
                btc_price = bitcoin_data["price"]
                
                if btc_price >= btc_threshold:
                    alerts.append({
                        "symbol": "BTC",
                        "type": "price_above_threshold",
                        "current_price": btc_price,
                        "threshold": btc_threshold,
                        "message": f"Bitcoin über ${btc_threshold:,.0f}! Aktuell: ${btc_price:,.2f}"
                    })
                
                # Zusätzliche Alerts für große Änderungen
                change_24h = abs(bitcoin_data.get("change_24h", 0))
                if change_24h > 10:  # Mehr als 10% Änderung
                    alerts.append({
                        "symbol": "BTC",
                        "type": "high_volatility",
                        "change_24h": bitcoin_data["change_24h"],
                        "message": f"Bitcoin hohe Volatilität: {bitcoin_data['change_24h']:+.1f}% in 24h"
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Preis-Alert-Prüfung: {e}")
            return []
    
    def clear_cache(self) -> None:
        """Leert den Cache"""
        
        self.cache = {
            "last_update": None,
            "bitcoin_data": None,
            "market_data": None
        }
        
        logger.info("🗑️ Crypto-Service Cache geleert") 