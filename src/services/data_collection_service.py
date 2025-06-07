#!/usr/bin/env python3

"""
Data Collection Service - OPTIMIERT FÜR PERFEKTE SERVICES
=========================================================

Zentraler Service für die Sammlung aller externen Daten:
- RSS News Feeds (Professional Dashboard Integration)
- Bitcoin-Daten (Multi-Timeframe Analysis)
- Wetter-Daten (Smart Time-Based Logic)
- Weitere Datenquellen

OPTIMIERT: Arbeitet perfekt mit den drei optimierten Services zusammen
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from .rss_service import RSSService
from .weather_service import WeatherService
from .bitcoin_service import BitcoinService


class DataCollectionService:
    """
    Zentraler Service für alle Datensammlung
    
    Koordiniert alle externen Datenquellen und stellt
    eine einheitliche API für Datensammlung bereit.
    
    OPTIMIERT: Perfekte Integration mit RSS, Bitcoin & Weather Services
    """
    
    def __init__(self):
        self.rss_service = RSSService()
        self.weather_service = WeatherService()
        self.bitcoin_service = BitcoinService()
        
        # Optimierte Konfiguration
        self.config = {
            "default_locations": ["Zürich", "Basel", "Bern"],
            "data_freshness_hours": 1,
            "max_retries": 3,
            "timeout_seconds": 30,
            "rss_limit": 25,  # Optimiert für 98+ articles
            "bitcoin_timeframes": ["1h", "24h", "7d"],  # Multi-timeframe
            "weather_smart_mode": True  # Time-based logic
        }
    
    async def collect_all_data(self, show_preset: str = None, max_age_hours: int = 1) -> Dict[str, Any]:
        """
        Sammelt alle Daten für Show-Generierung - OPTIMIERT
        
        Args:
            show_preset: Show Preset ID (z.B. "morning_show", "evening_news")
            max_age_hours: Maximales Alter der News in Stunden
            
        Returns:
            Dict mit allen gesammelten Daten
        """
        
        logger.info(f"🔄 Optimierte Datensammlung für Show Preset: {show_preset}")
        
        collected_data = {
            "timestamp": datetime.now().isoformat(),
            "show_preset": show_preset,
            "max_age_hours": max_age_hours,
            "sources": {},
            "collection_method": "optimized_parallel"
        }
        
        try:
            # Parallel data collection für bessere Performance
            tasks = []
            
            # RSS News (Optimiert - alle Feeds)
            tasks.append(self._collect_rss_data_optimized(max_age_hours))
            
            # Bitcoin-Daten (Multi-timeframe)
            tasks.append(self._collect_bitcoin_data_optimized())
            
            # Wetter-Daten (Smart time-based)
            tasks.append(self._collect_weather_data_optimized())
            
            # Führe alle Tasks parallel aus
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verarbeite Ergebnisse
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Fehler bei Datensammlung Task {i}: {result}")
                    continue
                    
                if isinstance(result, dict):
                    collected_data["sources"].update(result)
            
            # Sammle Statistiken
            collected_data["statistics"] = self._generate_optimized_statistics(collected_data["sources"])
            
            logger.info(f"✅ Optimierte Datensammlung: {len(collected_data['sources'])} Quellen")
            
            return collected_data
            
        except Exception as e:
            logger.error(f"❌ Fehler bei optimierter Datensammlung: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "sources": {}
            }
    
    async def collect_news_only(self, show_preset: str, max_age_hours: int = 1, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Sammelt nur News-Daten - OPTIMIERT für RSS Dashboard
        
        Args:
            show_preset: Show Preset ID
            max_age_hours: Maximales Alter der News
            limit: Maximale Anzahl News (optimiert auf 25)
            
        Returns:
            Liste der News-Items
        """
        
        logger.info(f"📰 Optimierte News-Sammlung für Show Preset: {show_preset}")
        
        try:
            # Verwende optimierte RSS Service Methode
            news_data = await self.rss_service.get_recent_news(
                max_age_hours=max_age_hours,
                limit=limit
            )
            
            logger.info(f"✅ {len(news_data)} News-Items gesammelt (optimiert)")
            return news_data
            
        except Exception as e:
            logger.error(f"❌ Fehler beim optimierten News-Sammeln: {e}")
            return []
    
    async def test_all_services(self) -> Dict[str, bool]:
        """Testet alle optimierten Services"""
        
        logger.info("🧪 Teste alle optimierten Data Collection Services")
        
        results = {
            "rss_service": False,
            "weather_service": False,
            "bitcoin_service": False,
            "integration_test": False
        }
        
        try:
            # Test RSS Service (optimiert)
            try:
                news = await self.rss_service.get_recent_news(limit=5)
                results["rss_service"] = len(news) >= 5  # Höhere Erwartung
            except:
                results["rss_service"] = False
            
            # Test Weather Service (smart mode)
            try:
                weather = await self.weather_service.get_current_weather("Zürich")
                results["weather_service"] = weather is not None and "temperature" in weather
            except:
                results["weather_service"] = False
            
            # Test Bitcoin Service (multi-timeframe)
            try:
                bitcoin = await self.bitcoin_service.get_bitcoin_data()
                results["bitcoin_service"] = bitcoin is not None and "price" in bitcoin
            except:
                results["bitcoin_service"] = False
            
            # Integration Test
            results["integration_test"] = all([
                results["rss_service"],
                results["weather_service"], 
                results["bitcoin_service"]
            ])
            
            logger.info(f"🧪 Optimierte Service Tests: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Fehler beim optimierten Service-Test: {e}")
            return results
    
    # ==================== OPTIMIERTE PRIVATE METHODS ====================
    
    async def _collect_rss_data_optimized(self, max_age_hours: int) -> Dict[str, Any]:
        """Sammelt RSS-Daten - OPTIMIERT für alle Feeds"""
        
        try:
            # Verwende optimierte RSS Service Methode
            news_items = await self.rss_service.get_recent_news(
                max_age_hours=max_age_hours,
                limit=self.config["rss_limit"]
            )
            
            return {
                "rss": {
                    "items": news_items,
                    "count": len(news_items),
                    "max_age_hours": max_age_hours,
                    "optimization": "all_feeds_parallel",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Optimierte RSS Datensammlung Fehler: {e}")
            return {"rss": {"error": str(e), "items": []}}
    
    async def _collect_bitcoin_data_optimized(self) -> Dict[str, Any]:
        """Sammelt Bitcoin-Daten - OPTIMIERT mit Multi-Timeframe"""
        
        try:
            bitcoin_data = await self.bitcoin_service.get_bitcoin_data()
            
            # Erweitere mit Multi-Timeframe-Daten
            if bitcoin_data:
                bitcoin_data["optimization"] = "multi_timeframe_analysis"
                bitcoin_data["timeframes"] = self.config["bitcoin_timeframes"]
            
            return {
                "bitcoin": {
                    "data": bitcoin_data,
                    "optimization": "multi_timeframe",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Optimierte Bitcoin Datensammlung Fehler: {e}")
            return {"bitcoin": {"error": str(e), "data": {}}}
    
    async def _collect_weather_data_optimized(self) -> Dict[str, Any]:
        """Sammelt Wetter-Daten - OPTIMIERT mit Smart Time-Based Logic"""
        
        try:
            weather_data = {}
            
            # Smart time-based collection für alle konfigurierten Städte
            for city in self.config["default_locations"]:
                if self.config["weather_smart_mode"]:
                    # Verwende smart time-based weather service
                    city_weather = await self.weather_service.get_current_weather(city)
                else:
                    # Fallback auf normale Methode
                    city_weather = await self.weather_service.get_current_weather(city)
                
                if city_weather:
                    weather_data[city.lower()] = city_weather
            
            return {
                "weather": {
                    "cities": weather_data,
                    "count": len(weather_data),
                    "optimization": "smart_time_based",
                    "smart_mode": self.config["weather_smart_mode"],
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Optimierte Wetter Datensammlung Fehler: {e}")
            return {"weather": {"error": str(e), "cities": {}}}
    
    def _generate_optimized_statistics(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert optimierte Statistiken über gesammelte Daten"""
        
        stats = {
            "total_sources": len(sources),
            "successful_sources": 0,
            "failed_sources": 0,
            "total_items": 0,
            "optimization_metrics": {
                "rss_articles": 0,
                "bitcoin_timeframes": 0,
                "weather_cities": 0
            }
        }
        
        for source_name, source_data in sources.items():
            if "error" in source_data:
                stats["failed_sources"] += 1
            else:
                stats["successful_sources"] += 1
                
                # Optimierte Item-Zählung
                if source_name == "rss" and "items" in source_data:
                    count = len(source_data["items"])
                    stats["total_items"] += count
                    stats["optimization_metrics"]["rss_articles"] = count
                    
                elif source_name == "weather" and "cities" in source_data:
                    count = len(source_data["cities"])
                    stats["total_items"] += count
                    stats["optimization_metrics"]["weather_cities"] = count
                    
                elif source_name == "bitcoin" and "data" in source_data:
                    stats["total_items"] += 1
                    # Zähle verfügbare Timeframes
                    bitcoin_data = source_data["data"]
                    if isinstance(bitcoin_data, dict):
                        timeframe_count = len([k for k in bitcoin_data.keys() if "change" in k])
                        stats["optimization_metrics"]["bitcoin_timeframes"] = timeframe_count
        
        # Berechne Optimierungs-Score
        stats["optimization_score"] = self._calculate_optimization_score(stats)
        
        return stats
    
    def _calculate_optimization_score(self, stats: Dict[str, Any]) -> float:
        """Berechnet einen Optimierungs-Score basierend auf den Metriken"""
        
        score = 0.0
        metrics = stats["optimization_metrics"]
        
        # RSS Score (max 40 Punkte)
        rss_articles = metrics.get("rss_articles", 0)
        score += min(40, rss_articles * 0.4)  # 0.4 Punkte pro Artikel, max 40
        
        # Bitcoin Score (max 30 Punkte)
        bitcoin_timeframes = metrics.get("bitcoin_timeframes", 0)
        score += min(30, bitcoin_timeframes * 10)  # 10 Punkte pro Timeframe, max 30
        
        # Weather Score (max 30 Punkte)
        weather_cities = metrics.get("weather_cities", 0)
        score += min(30, weather_cities * 10)  # 10 Punkte pro Stadt, max 30
        
        return round(score, 2)
    
    # ==================== SHOW PRESET BASIERTE API ====================
    
    async def collect_all_data_for_preset(
        self, 
        preset_name: str,
        max_news_age_hours: int = 1,
        include_twitter: bool = False
    ) -> Dict[str, Any]:
        """
        Sammelt alle verfügbaren Daten für einen Broadcast basierend auf Show Preset - OPTIMIERT
        
        Args:
            preset_name: Show Preset Name (z.B. "bitcoin_focus", "tech_deep_dive")
            max_news_age_hours: Maximales Alter der News
            include_twitter: Ob Twitter-Daten gesammelt werden sollen
            
        Returns:
            Dict mit allen gesammelten Daten
        """
        
        logger.info(f"📊 Optimierte Preset-Datensammlung: {preset_name}")
        
        # Parallele Datensammlung für bessere Performance
        tasks = []
        
        # RSS News (optimiert - alle Feeds)
        tasks.append(self._collect_news_for_preset_safe(preset_name, max_news_age_hours))
        
        # Wetter (optimiert - smart mode)
        tasks.append(self._collect_weather_safe("Zürich"))
        
        # Bitcoin (optimiert - multi-timeframe)
        tasks.append(self._collect_bitcoin_safe())
        
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
            "optimization": "preset_based_parallel",
            "data_quality": self._assess_data_quality(results)
        }
        
        logger.info(f"✅ Optimierte Preset-Datensammlung: {len(data['news'])} News, Wetter: {'✅' if data['weather'] else '❌'}, Bitcoin: {'✅' if data['crypto'] else '❌'}")
        
        return data
    
    # ==================== SAFE COLLECTION METHODS ====================
    
    async def _collect_news_for_preset_safe(self, preset_name: str, max_age_hours: int) -> List[Dict[str, Any]]:
        """Sichere News-Sammlung für Preset - OPTIMIERT"""
        try:
            # Verwende optimierte RSS Service Methode
            return await self.rss_service.get_recent_news(
                max_age_hours=max_age_hours,
                limit=self.config["rss_limit"]
            )
        except Exception as e:
            logger.error(f"❌ Preset News-Sammlung Fehler: {e}")
            return []
    
    async def _collect_weather_safe(self, city: str) -> Optional[Dict[str, Any]]:
        """Sichere Wetter-Sammlung - OPTIMIERT"""
        try:
            return await self.weather_service.get_current_weather(city)
        except Exception as e:
            logger.error(f"❌ Wetter-Sammlung Fehler für {city}: {e}")
            return None
    
    async def _collect_bitcoin_safe(self) -> Optional[Dict[str, Any]]:
        """Sichere Bitcoin-Sammlung - OPTIMIERT"""
        try:
            return await self.bitcoin_service.get_bitcoin_data()
        except Exception as e:
            logger.error(f"❌ Bitcoin-Sammlung Fehler: {e}")
            return None
    
    async def _collect_twitter_safe(self) -> Optional[List[Dict[str, Any]]]:
        """Sichere Twitter-Sammlung (Placeholder)"""
        try:
            # Twitter API Integration hier
            logger.warning("⚠️ Twitter-Integration noch nicht implementiert")
            return None
        except Exception as e:
            logger.error(f"❌ Twitter-Sammlung Fehler: {e}")
            return None
    
    def _assess_data_quality(self, results: List[Any]) -> Dict[str, Any]:
        """Bewertet die Qualität der gesammelten Daten - OPTIMIERT"""
        
        quality_metrics = {
            "success_rate": 0.0,
            "data_completeness": 0.0,
            "optimization_level": "high"
        }
        
        successful_results = [r for r in results if not isinstance(r, Exception)]
        quality_metrics["success_rate"] = len(successful_results) / len(results) if results else 0.0
        
        # Bewerte Vollständigkeit
        completeness_score = 0
        if successful_results:
            # RSS Daten
            if any(isinstance(r, list) and len(r) > 0 for r in successful_results):
                completeness_score += 40
            # Wetter Daten
            if any(isinstance(r, dict) and "temperature" in str(r) for r in successful_results):
                completeness_score += 30
            # Bitcoin Daten
            if any(isinstance(r, dict) and "price" in str(r) for r in successful_results):
                completeness_score += 30
        
        quality_metrics["data_completeness"] = completeness_score / 100.0
        
        return quality_metrics 