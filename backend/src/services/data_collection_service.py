#!/usr/bin/env python3

"""
Data Collection Service - NUR SHOW PRESET BASIERT
================================================

Zentraler Service für die Sammlung aller externen Daten:
- RSS News Feeds (Show Preset basiert)
- Twitter/X API
- Wetter-Daten
- Kryptowährung-Preise
- Weitere Datenquellen
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from .rss_service import RSSService
from .weather_service import WeatherService
from .bitcoin_service import BitcoinService
# Twitter service removed - no longer used


class DataCollectionService:
    """
    Zentraler Service für alle Datensammlung
    
    Koordiniert alle externen Datenquellen und stellt
    eine einheitliche API für Datensammlung bereit.
    
    NUR SHOW PRESET BASIERT - Keine Legacy Channel API mehr
    """
    
    def __init__(self):
        self.rss_service = RSSService()
        self.weather_service = WeatherService()
        self.crypto_service = BitcoinService()
        # self.twitter_service = TwitterService()  # Removed - no longer used
        
        # Konfiguration
        self.config = {
            "default_locations": ["Zürich", "Basel", "Bern"],
            "default_crypto_symbols": ["BTC", "ETH"],
            "data_freshness_hours": 1,
            "max_retries": 3,
            "timeout_seconds": 30
        }
    
    # ==================== SHOW PRESET BASIERTE API ====================
    
    async def collect_all_data_for_preset(
        self, 
        preset_name: str,
        max_news_age_hours: int = 1,
        include_twitter: bool = False
    ) -> Dict[str, Any]:
        """
        Sammelt alle verfügbaren Daten für einen Broadcast basierend auf Show Preset
        
        Args:
            preset_name: Show Preset Name (z.B. "bitcoin_focus", "tech_deep_dive")
            max_news_age_hours: Maximales Alter der News
            include_twitter: Ob Twitter-Daten gesammelt werden sollen
            
        Returns:
            Dict mit allen gesammelten Daten
        """
        
        logger.info("📊 Sammle alle Daten...")
        
        # Parallele Datensammlung für bessere Performance
        tasks = []
        
        # RSS News (Show Preset basiert)
        tasks.append(self._collect_news_for_preset_safe(preset_name, max_news_age_hours))
        
        # Wetter (immer Zürich als Standard)
        tasks.append(self._collect_weather_safe("Zürich"))
        
        # Crypto (immer)
        tasks.append(self._collect_crypto_safe())
        
        # Twitter (optional)
        if include_twitter:
            tasks.append(self._collect_twitter_safe())
        
        # Alle Tasks parallel ausführen
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse zusammenfassen
        data = {
            "news": results[0] if not isinstance(results[0], Exception) else [],
            "weather": results[1] if not isinstance(results[1], Exception) else None,
            "crypto": results[2] if not isinstance(results[2], Exception) else None,
            "twitter": results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None,
            "collection_timestamp": datetime.now().isoformat(),
            "preset_name": preset_name,
            "data_quality": self._assess_data_quality(results)
        }
        
        logger.info(f"✅ Datensammlung abgeschlossen: {len(data['news'])} News, Wetter: {'✅' if data['weather'] else '❌'}, Bitcoin: {'✅' if data['crypto'] else '❌'}")
        
        return data
    
    async def collect_news_data_for_preset(
        self, 
        preset_name: str,
        max_age_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Sammelt nur News-Daten basierend auf Show Preset
        """
        
        logger.info(f"📰 Sammle News-Daten für Show Preset '{preset_name}'")
        
        news = await self._collect_news_for_preset_safe(preset_name, max_age_hours)
        
        return {
            "news": news,
            "collection_timestamp": datetime.now().isoformat(),
            "preset_name": preset_name,
            "news_count": len(news)
        }

    # ==================== TESTING & MONITORING ====================
    
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
        
        # Test RSS Feeds (Show Preset)
        try:
            test_feeds = await self.rss_service.get_feeds_for_show_preset("zurich")
            results["rss_feeds_preset"] = len(test_feeds) > 0
        except Exception as e:
            logger.error(f"RSS Preset Test Fehler: {e}")
            results["rss_feeds_preset"] = False
        
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
        
        # Test Twitter Service - DISABLED (service removed)
        try:
            logger.info("🐦 Twitter Service deaktiviert")
            results["twitter_service"] = False
        except Exception as e:
            logger.error(f"Twitter Test Fehler: {e}")
            results["twitter_service"] = False
        
        logger.info(f"🔧 Verbindungstests abgeschlossen: {results}")
        return results
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _collect_news_for_preset_safe(self, preset_name: str, max_age_hours: int) -> List[Dict[str, Any]]:
        """
        Sammelt News für Show Preset mit Fehlerbehandlung
        """
        
        logger.info("📰 Sammle News für Show Preset...")
        
        try:
            # Verwende die korrekte RSS Service Methode
            news_items = await self.rss_service.get_recent_news_for_preset(preset_name, max_age_hours)
            
            if not news_items:
                logger.warning(f"⚠️ Keine News für Preset '{preset_name}' gefunden")
                return []
            
            logger.info(f"🔗 {len(news_items)} News gefunden")
            
            # Konvertiere RSSNewsItem zu Dict für Kompatibilität
            all_news = []
            for news_item in news_items:
                news_dict = {
                    "title": news_item.title,
                    "summary": news_item.summary,
                    "url": news_item.link,
                    "published": news_item.published.isoformat(),
                    "source_name": news_item.source,
                    "primary_category": news_item.category,
                    "priority": news_item.priority,
                    "weight": news_item.weight,
                    "relevance_score": news_item.relevance_score,
                    "tags": news_item.tags
                }
                all_news.append(news_dict)
            
            logger.info(f"✅ {len(all_news)} News gesammelt")
            return all_news
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Sammeln der News für Show Preset '{preset_name}': {e}")
            return []
    
    async def _collect_weather_safe(self, location: str) -> Optional[Dict[str, Any]]:
        """Sammelt Wetter-Daten mit Fehlerbehandlung"""
        logger.info("🌤️ Hole Wetter-Daten...")
        
        try:
            weather_data = await self.weather_service.get_current_weather(location)
            
            if weather_data:
                temp = weather_data.get('temperature', 'N/A')
                logger.info(f"✅ Wetter: {temp}°C")
                return weather_data
            else:
                logger.warning("⚠️ Keine Wetter-Daten verfügbar")
                return None
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Wetter-Sammlung: {e}")
            return None
    
    async def _collect_crypto_safe(self) -> Optional[Dict[str, Any]]:
        """Sammelt Crypto-Daten mit Fehlerbehandlung"""
        logger.info("₿ Hole Bitcoin-Daten...")
        
        try:
            crypto_data = await self.crypto_service.get_bitcoin_price()
            
            if crypto_data:
                price = crypto_data.get('price_usd', 'N/A')
                logger.info(f"✅ Bitcoin: ${price:,.0f}")
                return crypto_data
            else:
                logger.warning("⚠️ Keine Bitcoin-Daten verfügbar")
                return None
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Crypto-Sammlung: {e}")
            return None
    
    async def _collect_twitter_safe(self) -> Optional[List[Dict[str, Any]]]:
        """Sammelt Twitter-Daten mit Fehlerbehandlung - DISABLED"""
        try:
            logger.info("🐦 Twitter Service deaktiviert - keine Tweets gesammelt")
            return None
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Twitter-Sammlung: {e}")
            return None
    
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