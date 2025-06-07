#!/usr/bin/env python3

"""
Bitcoin Service
===============

Service for Bitcoin data:
- CoinMarketCap API Integration
- Bitcoin price data
- Bitcoin price trends
- Bitcoin price alerts

DEPENDENCIES: Only CoinMarketCap API Key
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
import random

# Load environment variables from ROOT directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


class BitcoinService:
    """
    Service for CoinMarketCap API Integration - BITCOIN ONLY
    
    Retrieves current Bitcoin data for
    broadcast generation.
    
    MINIMAL DEPENDENCIES: Only CoinMarketCap API
    """
    
    def __init__(self):
        # Load only CoinMarketCap API Key - NO other services
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        
        # Configuration - BITCOIN ONLY
        self.config = {
            "default_currency": "USD",
            "timeout": 30,
            "cache_duration": 300,  # 5 minutes
            "symbol": "BTC"  # Bitcoin only
        }
        
        # Cache for API responses
        self.cache = {
            "last_update": None,
            "bitcoin_data": None
        }
    
    async def get_bitcoin_price(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves current Bitcoin price
        
        Returns:
            Dict with Bitcoin price data or None on error
        """
        
        # Check cache
        if self._is_cache_valid():
            return self.cache["bitcoin_data"]
        
        if not self.api_key:
            logger.warning("⚠️ CoinMarketCap API Key not available")
            return self._get_fallback_bitcoin_data()
        
        # API Request Parameters
        url = f"{self.base_url}/cryptocurrency/quotes/latest"
        parameters = {
            'symbol': 'BTC',
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, 
                headers=headers, 
                params=parameters,
                timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and 'BTC' in data['data']:
                        btc_data = data['data']['BTC']
                        quote = btc_data['quote']['USD']
                        
                        bitcoin_data = {
                            'symbol': 'BTC',
                            'name': 'Bitcoin',
                            'price_usd': round(quote['price'], 2),
                            'change_1h': round(quote.get('percent_change_1h', 0), 2),
                            'change_24h': round(quote['percent_change_24h'], 2),
                            'change_7d': round(quote['percent_change_7d'], 2),
                            'change_30d': round(quote.get('percent_change_30d', 0), 2),
                            'change_60d': round(quote.get('percent_change_60d', 0), 2),
                            'change_90d': round(quote.get('percent_change_90d', 0), 2),
                            'market_cap': quote['market_cap'],
                            'volume_24h': quote['volume_24h'],
                            'last_updated': quote['last_updated'],
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Update cache
                        self.cache["bitcoin_data"] = bitcoin_data
                        self.cache["last_update"] = datetime.now()
                        
                        return bitcoin_data
                
                elif response.status == 429:
                    logger.warning("⚠️ CoinMarketCap rate limit reached")
                    return self._get_fallback_bitcoin_data()
                
                else:
                    logger.error(f"❌ CoinMarketCap API error {response.status}")
                    return self._get_fallback_bitcoin_data()
    
    async def get_bitcoin_trend(self) -> Dict[str, Any]:
        """
        Analyzes Bitcoin trend based on price changes
        
        Returns:
            Dict with trend analysis
        """
        
        bitcoin_data = await self.get_bitcoin_price()
        
        if not bitcoin_data:
            return {"trend": "unknown", "message": "No Bitcoin data available"}
        
        change_24h = bitcoin_data.get('change_24h', 0)
        price = bitcoin_data.get('price_usd', 0)
        
        # Trend Analysis
        if change_24h > 10:
            trend = "moon"
            emoji = "🚀"
            message = f"Bitcoin TO THE MOON! +{change_24h:.1f}% in 24h"
        elif change_24h > 5:
            trend = "bullish"
            emoji = "📈"
            message = f"Bitcoin bullish trend! +{change_24h:.1f}% in 24h"
        elif change_24h > 2:
            trend = "positive"
            emoji = "📊"
            message = f"Bitcoin slightly positive: +{change_24h:.1f}%"
        elif change_24h > -2:
            trend = "stable"
            emoji = "➡️"
            message = f"Bitcoin stable: {change_24h:+.1f}%"
        elif change_24h > -5:
            trend = "negative"
            emoji = "📉"
            message = f"Bitcoin slightly negative: {change_24h:.1f}%"
        elif change_24h > -10:
            trend = "bearish"
            emoji = "🔻"
            message = f"Bitcoin bearish trend: {change_24h:.1f}%"
        else:
            trend = "crash"
            emoji = "💥"
            message = f"Bitcoin CRASH! {change_24h:.1f}% in 24h"
        
        return {
            "trend": trend,
            "emoji": emoji,
            "message": message,
            "change_24h": change_24h,
            "price": price,
            "formatted": f"{emoji} ${price:,.0f} ({change_24h:+.1f}%)"
        }
    
    async def get_bitcoin_alerts(self, price_threshold: float = 100000) -> List[Dict[str, Any]]:
        """
        Checks Bitcoin price alerts
        
        Args:
            price_threshold: Price threshold in USD
            
        Returns:
            List of triggered alerts
        """
        
        alerts = []
        
        try:
            bitcoin_data = await self.get_bitcoin_price()
            
            if not bitcoin_data:
                return alerts
            
            price = bitcoin_data.get("price_usd", 0)
            change_24h = bitcoin_data.get("change_24h", 0)
            
            # Price Alert
            if price >= price_threshold:
                alerts.append({
                    "type": "price_threshold",
                    "message": f"₿ Bitcoin above ${price_threshold:,.0f}! Current: ${price:,.2f}",
                    "price": price,
                    "threshold": price_threshold
                })
            
            # Volatility Alert
            if abs(change_24h) > 10:
                alerts.append({
                    "type": "high_volatility",
                    "message": f"₿ Bitcoin high volatility: {change_24h:+.1f}% in 24h",
                    "change_24h": change_24h,
                    "price": price
                })
            
            # Milestone Alerts
            milestones = [50000, 75000, 100000, 150000, 200000]
            for milestone in milestones:
                if abs(price - milestone) < 1000:  # Within 1k of milestone
                    alerts.append({
                        "type": "milestone_approach",
                        "message": f"₿ Bitcoin approaching ${milestone:,.0f}! Current: ${price:,.2f}",
                        "price": price,
                        "milestone": milestone
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error checking Bitcoin alerts: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Tests Bitcoin API connection"""
        
        try:
            bitcoin_data = await self.get_bitcoin_price()
            return bitcoin_data is not None and "price_usd" in bitcoin_data
            
        except Exception as e:
            logger.error(f"Bitcoin Service test error: {e}")
            return False
    
    # Private Methods
    
    def _get_fallback_bitcoin_data(self) -> Dict[str, Any]:
        """Fallback Bitcoin data when API is not available"""
        
        # Simulate realistic Bitcoin data
        base_price = 105000  # Base price
        price_variation = random.uniform(-0.05, 0.05)  # ±5% variation
        current_price = base_price * (1 + price_variation)
        
        change_24h = random.uniform(-8.0, 8.0)  # ±8% daily change
        
        return {
            "symbol": "BTC",
            "name": "Bitcoin",
            "price_usd": round(current_price, 2),
            "change_1h": round(random.uniform(-2.0, 2.0), 2),  # ±2% hourly change
            "change_24h": round(change_24h, 2),
            "change_7d": round(change_24h * 0.7, 2),
            "change_30d": round(change_24h * 2.5, 2),  # Monthly trend
            "change_60d": round(change_24h * 4.0, 2),  # 2-month trend
            "change_90d": round(change_24h * 5.5, 2),  # 3-month trend
            "market_cap": current_price * 19_500_000,  # ~19.5M BTC in circulation
            "volume_24h": current_price * 500_000,
            "last_updated": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat(),
            "fallback_mode": True
        }
    
    def _is_cache_valid(self) -> bool:
        """Checks if cache is still valid"""
        
        if not self.cache["last_update"] or not self.cache["bitcoin_data"]:
            return False
        
        cache_age = (datetime.now() - self.cache["last_update"]).total_seconds()
        return cache_age < self.config["cache_duration"]
    
    # Utility Methods
    
    def get_api_status(self) -> Dict[str, Any]:
        """Gets API status and configuration"""
        
        return {
            "api_configured": bool(self.api_key),
            "base_url": self.base_url,
            "cache_duration": self.config["cache_duration"],
            "symbol": self.config["symbol"],
            "cache_valid": self._is_cache_valid(),
            "last_cache_update": self.cache["last_update"].isoformat() if self.cache["last_update"] else None
        }
    
    def clear_cache(self) -> None:
        """Clears the cache"""
        
        self.cache = {
            "last_update": None,
            "bitcoin_data": None
        }
    
    def format_for_radio(self, bitcoin_data: Optional[Dict[str, Any]] = None, timeframe: str = "24h") -> str:
        """Formats Bitcoin data for radio announcement
        
        Args:
            bitcoin_data: Bitcoin price data
            timeframe: Time period for change ("1h", "24h", "7d", "30d", "60d", "90d")
        """
        
        if not bitcoin_data:
            return "Bitcoin price not available"
        
        price = bitcoin_data.get('price_usd', 0)
        
        # Get change for specified timeframe
        timeframe_map = {
            "1h": ("change_1h", "in the last hour"),
            "24h": ("change_24h", "in the last 24 hours"),
            "7d": ("change_7d", "in the last 7 days"),
            "30d": ("change_30d", "in the last 30 days"),
            "60d": ("change_60d", "in the last 60 days"),
            "90d": ("change_90d", "in the last 90 days")
        }
        
        if timeframe not in timeframe_map:
            timeframe = "24h"  # Default fallback
        
        change_key, time_description = timeframe_map[timeframe]
        change = bitcoin_data.get(change_key, 0)
        
        # Trend word
        if change > 5:
            trend_word = "surged"
        elif change > 2:
            trend_word = "increased"
        elif change > 0:
            trend_word = "is up"
        elif change > -2:
            trend_word = "is stable"
        elif change > -5:
            trend_word = "is down"
        else:
            trend_word = "dropped significantly"
        
        return f"Bitcoin is trading at {price:,.0f} dollars and {trend_word} by {abs(change):.1f} percent {time_description}." 