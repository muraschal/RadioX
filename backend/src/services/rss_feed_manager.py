"""
RSS Feed Manager - Lädt Feed-Konfigurationen aus Supabase
"""

import asyncio
import aiohttp
import feedparser
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
import re
from urllib.parse import urljoin
from .supabase_service import SupabaseService


@dataclass
class RSSFeedConfig:
    """RSS Feed Konfiguration aus der Datenbank"""
    id: str
    radio_channel: str
    source_name: str
    feed_category: str
    feed_url: str
    priority: int
    weight: float
    is_active: bool
    description: str


@dataclass
class RSSNewsItem:
    """RSS News Item"""
    title: str
    summary: str
    link: str
    published: datetime
    source: str
    category: str
    priority: int
    tags: List[str]
    weight: float


class RSSFeedManager:
    """RSS Feed Manager mit Datenbank-basierter Konfiguration"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        
        # Kategorie-Keywords für automatische Klassifizierung
        self.category_keywords = {
            "bitcoin_crypto": ["bitcoin", "btc", "krypto", "blockchain", "ethereum", "crypto", "defi", "nft"],
            "wirtschaft": ["wirtschaft", "börse", "aktien", "unternehmen", "bank", "snb", "inflation", "finanz"],
            "technologie": ["technologie", "tech", "ki", "ai", "software", "digital", "startup", "apple", "google"],
            "weltpolitik": ["politik", "regierung", "parlament", "wahlen", "international", "trump", "biden"],
            "sport": ["sport", "fussball", "tennis", "ski", "olympia", "wm", "em", "bundesliga"],
            "local_zurich": ["schweiz", "zürich", "zurich", "basel", "bern", "genf", "lausanne", "stadt zürich", "kanton zürich", "zürcher", "züri", "limmat", "see", "hb zürich", "hauptbahnhof", "tram", "vbz", "stadtrat", "gemeinderat"],
            "wissenschaft": ["wissenschaft", "forschung", "studie", "universität", "medizin", "gesundheit"],
            "entertainment": ["kultur", "film", "musik", "theater", "festival", "promi", "celebrity"]
        }
        
        # Prioritäts-Keywords (höhere Priorität)
        self.priority_keywords = {
            "breaking": ["eilmeldung", "breaking", "urgent", "sofort", "jetzt", "live"],
            "high": ["wichtig", "bedeutend", "gross", "major", "kritisch", "skandal"],
            "bitcoin": ["bitcoin", "btc", "100k", "allzeithoch", "rekord", "crash"],
            "economy": ["snb", "leitzins", "inflation", "rezession", "börsencrash", "wirtschaftskrise"]
        }
    
    async def load_feed_configs(self, radio_channel: str = "zurich") -> List[RSSFeedConfig]:
        """Lädt RSS Feed Konfigurationen aus der Datenbank"""
        try:
            logger.info(f"📡 Lade RSS Feed Konfigurationen für Kanal: {radio_channel}")
            
            # Feeds aus Datenbank laden
            response = self.supabase.client.table('rss_feed_preferences').select('*').eq('radio_channel', radio_channel).eq('is_active', True).order('priority', desc=True).execute()
            
            if not response.data:
                logger.warning(f"⚠️ Keine RSS Feed Konfigurationen für Kanal '{radio_channel}' gefunden!")
                return []
            
            configs = []
            for row in response.data:
                config = RSSFeedConfig(
                    id=row['id'],
                    radio_channel=row['radio_channel'],
                    source_name=row['source_name'],
                    feed_category=row['feed_category'],
                    feed_url=row['feed_url'],
                    priority=row['priority'],
                    weight=float(row['weight']),
                    is_active=row['is_active'],
                    description=row['description']
                )
                configs.append(config)
            
            logger.info(f"✅ {len(configs)} RSS Feed Konfigurationen geladen")
            
            # Gruppiere nach Quelle für bessere Übersicht
            sources = {}
            for config in configs:
                if config.source_name not in sources:
                    sources[config.source_name] = []
                sources[config.source_name].append(config)
            
            logger.info(f"📊 Quellen: {', '.join(sources.keys())}")
            
            return configs
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der RSS Feed Konfigurationen: {e}")
            return []
    
    async def fetch_rss_feed(self, config: RSSFeedConfig) -> List[RSSNewsItem]:
        """Lädt RSS Feed und parst News Items"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.feed_url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_rss_content(content, config)
                    else:
                        logger.warning(f"RSS Feed Error {response.status}: {config.feed_url} ({config.source_name})")
                        return []
        except Exception as e:
            logger.error(f"Fehler beim Laden von RSS Feed {config.feed_url}: {e}")
            return []
    
    def _parse_rss_content(self, content: str, config: RSSFeedConfig) -> List[RSSNewsItem]:
        """Parst RSS Content zu News Items"""
        try:
            feed = feedparser.parse(content)
            news_items = []
            
            for entry in feed.entries[:10]:  # Top 10 pro Feed
                # Datum parsen
                published = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                # Nur News der letzten 24 Stunden
                if published < datetime.now() - timedelta(hours=24):
                    continue
                
                # Text für Kategorisierung
                text_for_analysis = f"{entry.title} {getattr(entry, 'summary', '')}"
                
                # Automatische Kategorisierung
                detected_category = self._detect_category(text_for_analysis, config.feed_category)
                
                # Priorität bestimmen (Basis-Priorität aus DB + Keywords)
                priority = self._calculate_priority(text_for_analysis, detected_category, config.priority)
                
                # Tags extrahieren
                tags = self._extract_tags(text_for_analysis)
                
                news_item = RSSNewsItem(
                    title=entry.title,
                    summary=getattr(entry, 'summary', entry.title)[:200],
                    link=getattr(entry, 'link', ''),
                    published=published,
                    source=config.source_name,
                    category=detected_category,
                    priority=priority,
                    tags=tags,
                    weight=config.weight
                )
                
                news_items.append(news_item)
            
            logger.info(f"   📰 {len(news_items)} News von {config.source_name} ({config.feed_category}) geparst")
            return news_items
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen von RSS Content: {e}")
            return []
    
    def _detect_category(self, text: str, feed_category: str) -> str:
        """Erkennt Kategorie basierend auf Keywords"""
        text_lower = text.lower()
        
        # Scoring für jede Kategorie
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            category_scores[category] = score
        
        # Beste Kategorie finden
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        # Fallback auf Feed-Kategorie wenn kein Match
        if best_category[1] == 0:
            category_mapping = {
                "schweiz": "local_zurich",
                "zurich": "local_zurich",
                "wirtschaft": "wirtschaft", 
                "sport": "sport",
                "digital": "technologie",
                "technologie": "technologie",
                "technology": "technologie",
                "international": "weltpolitik",
                "world": "weltpolitik",
                "business": "wirtschaft",
                "news": "local_zurich",
                "bitcoin": "bitcoin_crypto",
                "latest": "general"
            }
            return category_mapping.get(feed_category, "general")
        
        return best_category[0]
    
    def _calculate_priority(self, text: str, category: str, base_priority: int) -> int:
        """Berechnet Priorität basierend auf Keywords und Kategorie"""
        text_lower = text.lower()
        priority = base_priority  # Basis-Priorität aus Datenbank
        
        # Breaking News Keywords
        for keyword in self.priority_keywords["breaking"]:
            if keyword in text_lower:
                priority += 3
                break
        
        # High Priority Keywords
        for keyword in self.priority_keywords["high"]:
            if keyword in text_lower:
                priority += 2
                break
        
        # Bitcoin Keywords (für Breaking News Station relevant)
        for keyword in self.priority_keywords["bitcoin"]:
            if keyword in text_lower:
                priority += 2
                break
        
        # Economy Keywords
        for keyword in self.priority_keywords["economy"]:
            if keyword in text_lower:
                priority += 1
                break
        
        # Kategorie-basierte Priorität für Breaking News Station
        category_priority = {
            "bitcoin_crypto": 2,
            "wirtschaft": 1,
            "weltpolitik": 1,
            "technologie": 1,
            "local_zurich": 2,  # Zürich-News sind wichtig für lokalen Kanal
            "sport": -1,
            "entertainment": -2,
            "wissenschaft": 0
        }
        
        priority += category_priority.get(category, 0)
        
        # Priorität zwischen 1-10 begrenzen
        return max(1, min(10, priority))
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extrahiert relevante Tags aus dem Text"""
        text_lower = text.lower()
        tags = []
        
        # Wichtige Keywords als Tags
        important_keywords = [
            "bitcoin", "snb", "zürich", "schweiz", "breaking", "eilmeldung",
            "börse", "aktien", "inflation", "tech", "startup", "ki", "ai",
            "trump", "biden", "ukraine", "china", "usa", "europa"
        ]
        
        for keyword in important_keywords:
            if keyword in text_lower:
                tags.append(keyword)
        
        return tags[:5]  # Max 5 Tags
    
    async def get_latest_news(
        self, 
        radio_channel: str = "zurich",
        max_items: int = 20,
        source_filter: List[str] = None,
        category_filter: List[str] = None
    ) -> List[RSSNewsItem]:
        """Sammelt aktuelle News basierend auf Datenbank-Konfiguration"""
        
        logger.info(f"📰 Sammle News für Radio-Kanal: {radio_channel}")
        
        # Feed-Konfigurationen aus Datenbank laden
        configs = await self.load_feed_configs(radio_channel)
        
        if not configs:
            logger.error(f"❌ Keine Feed-Konfigurationen für Kanal '{radio_channel}' gefunden!")
            return []
        
        # Filter anwenden
        if source_filter:
            configs = [c for c in configs if c.source_name in source_filter]
        
        if category_filter:
            configs = [c for c in configs if c.feed_category in category_filter]
        
        logger.info(f"📡 Verwende {len(configs)} Feed-Konfigurationen...")
        
        all_news = []
        tasks = []
        
        # Alle RSS Feeds parallel laden
        for config in configs:
            task = self.fetch_rss_feed(config)
            tasks.append(task)
        
        # Alle Feeds parallel verarbeiten
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse sammeln
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"RSS Feed Fehler: {result}")
        
        # Nach Priorität, Gewichtung und Datum sortieren
        all_news.sort(key=lambda x: (x.priority * x.weight, x.published), reverse=True)
        
        # Duplikate entfernen (ähnliche Titel)
        unique_news = self._remove_duplicates(all_news)
        
        logger.info(f"✅ {len(unique_news)} einzigartige News gesammelt (von {len(all_news)} total)")
        
        return unique_news[:max_items]
    
    def _remove_duplicates(self, news_items: List[RSSNewsItem]) -> List[RSSNewsItem]:
        """Entfernt ähnliche News Items"""
        unique_news = []
        seen_titles = set()
        
        for item in news_items:
            # Vereinfachter Titel für Duplikat-Erkennung
            simple_title = re.sub(r'[^\w\s]', '', item.title.lower())
            title_words = set(simple_title.split())
            
            # Prüfe auf ähnliche Titel
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                # Wenn 70% der Wörter übereinstimmen = Duplikat
                if len(title_words & seen_words) / len(title_words | seen_words) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(item)
                seen_titles.add(simple_title)
        
        return unique_news


# Convenience Functions
async def get_zurich_news(max_items: int = 20) -> List[RSSNewsItem]:
    """Holt aktuelle News für Zürich Radio-Kanal"""
    manager = RSSFeedManager()
    return await manager.get_latest_news("zurich", max_items=max_items)

async def get_news_by_channel(channel: str, max_items: int = 20) -> List[RSSNewsItem]:
    """Holt News für spezifischen Radio-Kanal"""
    manager = RSSFeedManager()
    return await manager.get_latest_news(channel, max_items=max_items) 