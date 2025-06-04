#!/usr/bin/env python3

"""
Data Collection Service
======================

Zentraler Service für die Sammlung aller externen Daten:
- RSS News Feeds
- Twitter/X API
- Wetter-Daten
- Kryptowährung-Preise
- Weitere Datenquellen
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from .rss_feed_manager import RSSFeedManager
from .weather_service import WeatherService
from .crypto_service import CoinMarketCapService
from .twitter_service import TwitterService


class DataCollectionService:
    """
    Zentraler Service für alle Datensammlung
    
    Koordiniert alle externen Datenquellen und stellt
    eine einheitliche API für Datensammlung bereit.
    """
    
    def __init__(self):
        self.rss_manager = RSSFeedManager()
        self.weather_service = WeatherService()
        self.crypto_service = CoinMarketCapService()
        self.twitter_service = TwitterService()
        
        # Konfiguration
        self.config = {
            "default_locations": ["Zürich", "Basel", "Bern"],
            "default_crypto_symbols": ["BTC", "ETH"],
            "data_freshness_hours": 1,
            "max_retries": 3,
            "timeout_seconds": 30
        }
    
    async def collect_all_data(
        self, 
        channel: str = "zurich",
        max_news_age_hours: int = 1,
        include_twitter: bool = False
    ) -> Dict[str, Any]:
        """
        Sammelt alle verfügbaren Daten für einen Broadcast
        
        Args:
            channel: Radio-Kanal für spezifische Feeds
            max_news_age_hours: Maximales Alter der News
            include_twitter: Ob Twitter-Daten gesammelt werden sollen
            
        Returns:
            Dict mit allen gesammelten Daten
        """
        
        logger.info(f"📊 Sammle alle Daten für Kanal '{channel}'")
        
        # Parallele Datensammlung für bessere Performance
        tasks = []
        
        # RSS News (immer)
        tasks.append(self._collect_news_safe(channel, max_news_age_hours))
        
        # Wetter (immer)
        location = self._get_location_for_channel(channel)
        tasks.append(self._collect_weather_safe(location))
        
        # Crypto (immer)
        tasks.append(self._collect_crypto_safe())
        
        # Twitter (optional)
        if include_twitter:
            tasks.append(self._collect_twitter_safe(channel))
        
        # Alle Tasks parallel ausführen
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse zusammenfassen
        data = {
            "news": results[0] if not isinstance(results[0], Exception) else [],
            "weather": results[1] if not isinstance(results[1], Exception) else None,
            "crypto": results[2] if not isinstance(results[2], Exception) else None,
            "twitter": results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None,
            "collection_timestamp": datetime.now().isoformat(),
            "channel": channel,
            "data_quality": self._assess_data_quality(results)
        }
        
        logger.info(f"✅ Datensammlung abgeschlossen: {len(data['news'])} News, "
                   f"Wetter: {'✅' if data['weather'] else '❌'}, "
                   f"Crypto: {'✅' if data['crypto'] else '❌'}")
        
        return data
    
    async def collect_news_data(
        self, 
        channel: str = "zurich",
        max_age_hours: int = 1
    ) -> Dict[str, Any]:
        """Sammelt nur News-Daten"""
        
        logger.info(f"📰 Sammle News-Daten für Kanal '{channel}'")
        
        news = await self._collect_news_safe(channel, max_age_hours)
        
        return {
            "news": news,
            "collection_timestamp": datetime.now().isoformat(),
            "channel": channel,
            "news_count": len(news)
        }
    
    async def collect_context_data(self, location: str = "Zürich") -> Dict[str, Any]:
        """Sammelt nur Kontext-Daten (Wetter, Crypto)"""
        
        logger.info(f"🌍 Sammle Kontext-Daten für '{location}'")
        
        # Parallele Sammlung
        weather_task = self._collect_weather_safe(location)
        crypto_task = self._collect_crypto_safe()
        
        weather, crypto = await asyncio.gather(
            weather_task, crypto_task, return_exceptions=True
        )
        
        return {
            "weather": weather if not isinstance(weather, Exception) else None,
            "crypto": crypto if not isinstance(crypto, Exception) else None,
            "collection_timestamp": datetime.now().isoformat(),
            "location": location
        }
    
    async def test_connections(self) -> Dict[str, bool]:
        """Testet alle Datenquellen-Verbindungen"""
        
        logger.info("🔧 Teste alle Datenquellen-Verbindungen")
        
        results = {}
        
        # Test RSS Feeds
        try:
            test_feeds = await self.rss_manager.load_feed_configs("zurich")
            results["rss_feeds"] = len(test_feeds) > 0
        except Exception as e:
            logger.error(f"RSS Test Fehler: {e}")
            results["rss_feeds"] = False
        
        # Test Weather Service
        try:
            weather = await self.weather_service.get_current_weather("Zürich")
            results["weather_service"] = weather is not None
        except Exception as e:
            logger.error(f"Weather Test Fehler: {e}")
            results["weather_service"] = False
        
        # Test Crypto Service
        try:
            crypto = await self.crypto_service.get_bitcoin_price()
            results["crypto_service"] = crypto is not None
        except Exception as e:
            logger.error(f"Crypto Test Fehler: {e}")
            results["crypto_service"] = False
        
        # Test Twitter Service
        try:
            twitter_status = await self.twitter_service.test_connection()
            results["twitter_service"] = twitter_status
        except Exception as e:
            logger.error(f"Twitter Test Fehler: {e}")
            results["twitter_service"] = False
        
        logger.info(f"🔧 Verbindungstests abgeschlossen: {results}")
        return results
    
    # Private Helper Methods
    
    async def _collect_news_safe(self, channel: str, max_age_hours: int) -> List[Dict[str, Any]]:
        """Sammelt News mit Fehlerbehandlung"""
        try:
            # Lade Feed-Konfigurationen
            feed_configs = await self.rss_manager.load_feed_configs(channel)
            
            if not feed_configs:
                logger.warning(f"⚠️ Keine RSS-Feeds für Kanal '{channel}' gefunden")
                return []
            
            # Sammle News von allen Feeds
            all_news = []
            for config in feed_configs:
                if config.get("is_active", True):
                    try:
                        feed_news = await self.rss_manager.fetch_feed_news(
                            config["feed_url"],
                            max_age_hours=max_age_hours
                        )
                        
                        # Füge Metadaten hinzu
                        for news in feed_news:
                            news.update({
                                "source_name": config["source_name"],
                                "feed_category": config["feed_category"],
                                "priority": config.get("priority", 5),
                                "weight": config.get("weight", 1.0)
                            })
                        
                        all_news.extend(feed_news)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Fehler bei Feed {config['source_name']}: {e}")
                        continue
            
            logger.info(f"📰 {len(all_news)} News von {len(feed_configs)} Feeds gesammelt")
            return all_news
            
        except Exception as e:
            logger.error(f"❌ Fehler bei News-Sammlung: {e}")
            return []
    
    async def _collect_weather_safe(self, location: str) -> Optional[Dict[str, Any]]:
        """Sammelt Wetter-Daten mit Fehlerbehandlung"""
        try:
            weather = await self.weather_service.get_current_weather(location)
            
            if weather and hasattr(weather, '__dict__'):
                weather_dict = weather.__dict__.copy()
                
                # Konvertiere datetime-Objekte
                for key, value in weather_dict.items():
                    if isinstance(value, datetime):
                        weather_dict[key] = value.isoformat()
                
                logger.info(f"🌡️ Wetter für {location}: {weather_dict.get('temperature', '?')}°C")
                return weather_dict
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Wetter-Sammlung: {e}")
            return None
    
    async def _collect_crypto_safe(self) -> Optional[Dict[str, Any]]:
        """Sammelt Crypto-Daten mit Fehlerbehandlung"""
        try:
            crypto = await self.crypto_service.get_bitcoin_price()
            
            if crypto:
                # Konvertiere datetime-Objekte falls vorhanden
                crypto_dict = crypto.copy()
                for key, value in crypto_dict.items():
                    if isinstance(value, datetime):
                        crypto_dict[key] = value.isoformat()
                
                logger.info(f"₿ Bitcoin: ${crypto_dict.get('price', 0):,.0f}")
                return crypto_dict
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Crypto-Sammlung: {e}")
            return None
    
    async def _collect_twitter_safe(self, channel: str) -> Optional[List[Dict[str, Any]]]:
        """Sammelt Twitter-Daten mit Fehlerbehandlung"""
        try:
            # Definiere Suchbegriffe basierend auf Kanal
            search_terms = self._get_twitter_terms_for_channel(channel)
            
            tweets = await self.twitter_service.search_tweets(
                query=" OR ".join(search_terms),
                max_results=10
            )
            
            logger.info(f"🐦 {len(tweets) if tweets else 0} Tweets gesammelt")
            return tweets
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Twitter-Sammlung: {e}")
            return None
    
    def _get_location_for_channel(self, channel: str) -> str:
        """Bestimmt Standort basierend auf Kanal"""
        location_map = {
            "zurich": "Zürich",
            "basel": "Basel", 
            "bern": "Bern"
        }
        return location_map.get(channel, "Zürich")
    
    def _get_twitter_terms_for_channel(self, channel: str) -> List[str]:
        """Bestimmt Twitter-Suchbegriffe basierend auf Kanal"""
        base_terms = ["Schweiz", "Switzerland"]
        
        channel_terms = {
            "zurich": ["Zürich", "Zurich"],
            "basel": ["Basel"],
            "bern": ["Bern"]
        }
        
        return base_terms + channel_terms.get(channel, [])
    
    def _assess_data_quality(self, results: List[Any]) -> Dict[str, Any]:
        """Bewertet die Qualität der gesammelten Daten"""
        
        successful_sources = sum(1 for r in results if not isinstance(r, Exception))
        total_sources = len(results)
        
        quality_score = successful_sources / total_sources if total_sources > 0 else 0
        
        return {
            "successful_sources": successful_sources,
            "total_sources": total_sources,
            "quality_score": quality_score,
            "quality_level": (
                "excellent" if quality_score >= 0.8 else
                "good" if quality_score >= 0.6 else
                "fair" if quality_score >= 0.4 else
                "poor"
            )
        } 