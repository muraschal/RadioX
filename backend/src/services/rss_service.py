"""
RadioX RSS Service - KONSOLIDIERT
================================

Ultimativer RSS Service der alle Features vereint:
- Supabase Database Integration
- 25+ RSS Feeds (Schweizer + International)
- Channel-basierte News-Sammlung
- Automatische Kategorisierung & Prioritätsbewertung
- Duplikat-Erkennung
- Parallel Processing
"""

import asyncio
import aiohttp
import feedparser
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
import re
import sys
import os
from urllib.parse import urlparse
import html

# Backend-Pfad hinzufügen für relative Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import get_settings
from database.supabase_client import SupabaseClient


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
    weight: float = 1.0
    relevance_score: float = 0.5


class RSSService:
    """Ultimativer RSS Service für RadioX"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase = SupabaseClient()
        
        # MASSIVE RSS FEED SAMMLUNG - 25+ QUELLEN!
        self.rss_feeds = {
            # === SCHWEIZER MEDIEN ===
            "nzz": {
                "base_url": "https://www.nzz.ch",
                "feeds": {
                    "schweiz": "https://www.nzz.ch/schweiz.rss",
                    "wirtschaft": "https://www.nzz.ch/wirtschaft.rss",
                    "international": "https://www.nzz.ch/international.rss",
                    "technologie": "https://www.nzz.ch/technologie.rss",
                    "zurich": "https://www.nzz.ch/zuerich.rss"
                },
                "priority": 9,
                "weight": 1.2
            },
            "srf": {
                "base_url": "https://www.srf.ch",
                "feeds": {
                    "news": "https://www.srf.ch/news/bnf/rss/19032223",
                    "schweiz": "https://www.srf.ch/news/bnf/rss/1926",
                    "international": "https://www.srf.ch/bnf/rss/19920122",
                    "wirtschaft": "https://www.srf.ch/news/bnf/rss/1646",
                    "sport": "https://www.srf.ch/sport/bnf/rss/1948"
                },
                "priority": 8,
                "weight": 1.1
            },
            "tagesanzeiger": {
                "base_url": "https://www.tagesanzeiger.ch",
                "feeds": {
                    "zurich": "https://www.tagesanzeiger.ch/zuerich/rss.html",
                    "schweiz": "https://www.tagesanzeiger.ch/schweiz/rss.html",
                    "wirtschaft": "https://www.tagesanzeiger.ch/wirtschaft/rss.html"
                },
                "priority": 7,
                "weight": 1.0
            },
            "telezueri": {
                "base_url": "https://www.telezueri.ch",
                "feeds": {
                    "zurich": "https://www.telezueri.ch/rss.xml"
                },
                "priority": 6,
                "weight": 1.1
            },
            "zueritoday": {
                "base_url": "https://www.zueritoday.ch",
                "feeds": {
                    "zurich": "https://www.zueritoday.ch/rss.xml"
                },
                "priority": 6,
                "weight": 1.0
            },
            
            # === SCHWEIZER FINANZ ===
            "cash": {
                "base_url": "https://www.cash.ch",
                "feeds": {
                    "top_news": "https://www.cash.ch/feeds/latest/top-news",
                    "boerse": "https://www.cash.ch/rss/450.xml",
                    "alle_news": "https://www.cash.ch/feeds/latest/news"
                },
                "priority": 7,
                "weight": 1.0
            },
            "insideparadeplatz": {
                "base_url": "https://insideparadeplatz.ch",
                "feeds": {
                    "finanz": "https://insideparadeplatz.ch/feed/"
                },
                "priority": 6,
                "weight": 0.9
            },
            
            # === INTERNATIONALE BREAKING NEWS ===
            "reuters": {
                "base_url": "https://www.reuters.com",
                "feeds": {
                    "breaking": "https://feeds.reuters.com/reuters/breakingviews",
                    "world": "https://feeds.reuters.com/Reuters/worldNews",
                    "business": "https://feeds.reuters.com/reuters/businessNews",
                    "technology": "https://feeds.reuters.com/reuters/technologyNews"
                },
                "priority": 8,
                "weight": 1.1
            },
            "bbc": {
                "base_url": "https://www.bbc.com",
                "feeds": {
                    "world": "http://feeds.bbci.co.uk/news/world/rss.xml",
                    "business": "http://feeds.bbci.co.uk/news/business/rss.xml",
                    "technology": "http://feeds.bbci.co.uk/news/technology/rss.xml"
                },
                "priority": 8,
                "weight": 1.0
            },
            "guardian": {
                "base_url": "https://www.theguardian.com",
                "feeds": {
                    "world": "https://www.theguardian.com/world/rss",
                    "business": "https://www.theguardian.com/business/rss",
                    "technology": "https://www.theguardian.com/technology/rss"
                },
                "priority": 7,
                "weight": 1.0
            },
            "cnn": {
                "base_url": "https://www.cnn.com",
                "feeds": {
                    "world": "http://rss.cnn.com/rss/edition.rss",
                    "business": "http://rss.cnn.com/rss/money_latest.rss",
                    "tech": "http://rss.cnn.com/rss/edition_technology.rss"
                },
                "priority": 7,
                "weight": 1.0
            },
            
            # === DEUTSCHE MEDIEN ===
            "spiegel": {
                "base_url": "https://www.spiegel.de",
                "feeds": {
                    "schlagzeilen": "https://www.spiegel.de/schlagzeilen/index.rss",
                    "wirtschaft": "https://www.spiegel.de/wirtschaft/index.rss",
                    "netzwelt": "https://www.spiegel.de/netzwelt/index.rss"
                },
                "priority": 7,
                "weight": 1.0
            },
            "heise": {
                "base_url": "https://www.heise.de",
                "feeds": {
                    "news": "https://www.heise.de/rss/heise.rdf",
                    "security": "https://www.heise.de/security/rss/news-atom.xml"
                },
                "priority": 6,
                "weight": 0.9
            },
            
            # === TECH NEWS GIGANTEN ===
            "techcrunch": {
                "base_url": "https://techcrunch.com",
                "feeds": {
                    "latest": "https://techcrunch.com/feed/",
                    "startups": "https://techcrunch.com/category/startups/feed/",
                    "ai": "https://techcrunch.com/category/artificial-intelligence/feed/"
                },
                "priority": 8,
                "weight": 1.1
            },
            "theverge": {
                "base_url": "https://www.theverge.com",
                "feeds": {
                    "tech": "https://www.theverge.com/rss/index.xml"
                },
                "priority": 7,
                "weight": 1.0
            },
            "arstechnica": {
                "base_url": "https://arstechnica.com",
                "feeds": {
                    "tech": "https://feeds.arstechnica.com/arstechnica/index"
                },
                "priority": 7,
                "weight": 1.0
            },
            "wired": {
                "base_url": "https://www.wired.com",
                "feeds": {
                    "latest": "https://www.wired.com/feed/rss"
                },
                "priority": 7,
                "weight": 1.0
            },
            "engadget": {
                "base_url": "https://www.engadget.com",
                "feeds": {
                    "tech": "https://www.engadget.com/rss.xml"
                },
                "priority": 6,
                "weight": 0.9
            },
            "mashable": {
                "base_url": "https://mashable.com",
                "feeds": {
                    "tech": "https://mashable.com/feeds/rss/all"
                },
                "priority": 6,
                "weight": 0.9
            },
            
            # === BITCOIN/CRYPTO KINGDOM ===
            "cointelegraph": {
                "base_url": "https://cointelegraph.com",
                "feeds": {
                    "bitcoin": "https://de.cointelegraph.com/rss/tag/bitcoin",
                    "latest": "https://cointelegraph.com/rss"
                },
                "priority": 9,
                "weight": 1.3
            },
            "coindesk": {
                "base_url": "https://www.coindesk.com",
                "feeds": {
                    "bitcoin": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                    "markets": "https://www.coindesk.com/arc/outboundfeeds/rss/"
                },
                "priority": 8,
                "weight": 1.2
            }
        }
        
        # KATEGORIE-KEYWORDS für intelligente Klassifizierung
        self.category_keywords = {
            "bitcoin_crypto": ["bitcoin", "btc", "krypto", "blockchain", "ethereum", "crypto", "defi", "nft", "satoshi", "mining", "hodl"],
            "wirtschaft": ["wirtschaft", "börse", "aktien", "unternehmen", "bank", "snb", "inflation", "finanz", "zinsen", "rezession"],
            "technologie": ["technologie", "tech", "ki", "ai", "software", "digital", "startup", "apple", "google", "meta", "tesla"],
            "weltpolitik": ["politik", "regierung", "parlament", "wahlen", "international", "trump", "biden", "putin", "china"],
            "sport": ["sport", "fussball", "tennis", "ski", "olympia", "wm", "em", "bundesliga", "champions league"],
            "lokale_news_schweiz": ["schweiz", "zürich", "zurich", "basel", "bern", "genf", "lausanne", "stadt zürich", "kanton zürich", "zürcher", "züri", "limmat", "see", "hb zürich", "hauptbahnhof", "tram", "vbz", "stadtrat", "gemeinderat", "snb", "chf"],
            "wissenschaft": ["wissenschaft", "forschung", "studie", "universität", "medizin", "gesundheit", "klima", "umwelt"],
            "entertainment": ["kultur", "film", "musik", "theater", "festival", "promi", "celebrity", "netflix", "streaming"]
        }
        
        # PRIORITÄTS-KEYWORDS (höhere Priorität)
        self.priority_keywords = {
            "breaking": ["eilmeldung", "breaking", "urgent", "sofort", "jetzt", "live", "flash"],
            "high": ["wichtig", "bedeutend", "gross", "major", "kritisch", "skandal", "sensation"],
            "bitcoin": ["bitcoin", "btc", "100k", "allzeithoch", "rekord", "crash", "moon", "bullrun"],
            "economy": ["snb", "leitzins", "inflation", "rezession", "börsencrash", "wirtschaftskrise", "crash"]
        }
        
        # KANAL -> KATEGORIE MAPPING
        self.channel_categories = {
            'zurich': ['lokale_news_schweiz', 'wirtschaft', 'technologie', 'bitcoin_crypto'],
            'basel': ['lokale_news_schweiz', 'wirtschaft', 'weltpolitik'],
            'bern': ['lokale_news_schweiz', 'weltpolitik', 'wirtschaft']
        }
        
        # KANAL -> QUELLEN MAPPING
        self.channel_sources = {
            'zurich': ['nzz', 'srf', 'tagesanzeiger', 'telezueri', 'zueritoday', 'cash', 'cointelegraph', 'techcrunch'],
            'basel': ['nzz', 'srf', 'tagesanzeiger', 'cash', 'reuters', 'bbc'],
            'bern': ['nzz', 'srf', 'tagesanzeiger', 'reuters', 'guardian', 'spiegel']
        }
    
    # ==================== API-METHODEN FÜR DATA_COLLECTION_SERVICE ====================
    
    async def get_feeds_for_channel(self, channel: str) -> List[Dict]:
        """
        Holt Feed-Konfigurationen für einen Kanal
        -> REQUIRED by data_collection_service.py
        """
        try:
            sources = self.channel_sources.get(channel, ['nzz', 'srf'])
            
            feeds = []
            for source_name in sources:
                if source_name in self.rss_feeds:
                    source_config = self.rss_feeds[source_name]
                    
                    for category, feed_url in source_config["feeds"].items():
                        feed_config = {
                            "id": f"{source_name}_{category}",
                            "source_name": source_name,
                            "feed_category": category,
                            "feed_url": feed_url,
                            "priority": source_config["priority"],
                            "weight": source_config["weight"],
                            "is_active": True
                        }
                        feeds.append(feed_config)
            
            logger.info(f"{len(feeds)} RSS-Feeds für Kanal '{channel}' gefunden")
            return feeds
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Feeds für Kanal {channel}: {e}")
            return []
    
    async def get_recent_news(self, channel: str, max_age_hours: int = 1) -> List[RSSNewsItem]:
        """
        Sammelt aktuelle News für einen Kanal
        -> REQUIRED by data_collection_service.py
        """
        try:
            logger.info(f"📰 Sammle News für Kanal '{channel}' (max {max_age_hours}h alt)")
            
            # Kanal-spezifische Quellen
            sources = self.channel_sources.get(channel, ['nzz', 'srf'])
            categories = self.channel_categories.get(channel, ['lokale_news_schweiz'])
            
            # Sammle News von allen Quellen
            all_news = await self.get_latest_news(
                sources=sources,
                categories=categories,
                max_items=20
            )
            
            # Filter nach Alter
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            recent_news = [
                news for news in all_news 
                if news.published > cutoff_time
            ]
            
            logger.info(f"✅ {len(recent_news)} aktuelle News für Kanal '{channel}' gesammelt")
            return recent_news
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Sammeln aktueller News für {channel}: {e}")
            return []
    
    # ==================== CORE RSS PROCESSING ====================
    
    async def fetch_rss_feed(self, url: str, source: str, category: str, priority: int, weight: float) -> List[RSSNewsItem]:
        """Lädt RSS Feed und parst News Items"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_rss_content(content, source, category, priority, weight)
                    else:
                        logger.warning(f"RSS Feed Error {response.status}: {url}")
                        return []
        except Exception as e:
            logger.error(f"Fehler beim Laden von RSS Feed {url}: {e}")
            return []
    
    def _parse_rss_content(self, content: str, source: str, feed_category: str, base_priority: int, weight: float) -> List[RSSNewsItem]:
        """Parst RSS Content zu News Items"""
        try:
            feed = feedparser.parse(content)
            news_items = []
            
            for entry in feed.entries[:10]:  # Top 10 pro Feed
                # Datum parsen
                published = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                
                # Nur News der letzten 24 Stunden
                if published < datetime.now() - timedelta(hours=24):
                    continue
                
                # Text bereinigen
                title = entry.title
                summary = self._clean_html(getattr(entry, 'summary', entry.title)[:300])
                text_for_analysis = f"{title} {summary}"
                
                # Automatische Kategorisierung
                detected_category = self._detect_category(text_for_analysis, feed_category)
                
                # Priorität berechnen
                priority = self._calculate_priority(text_for_analysis, detected_category, base_priority)
                
                # Relevance Score berechnen
                relevance_score = self._calculate_relevance_score(text_for_analysis, detected_category)
                
                # Tags extrahieren
                tags = self._extract_tags(text_for_analysis)
                
                news_item = RSSNewsItem(
                    title=title,
                    summary=summary,
                    link=getattr(entry, 'link', ''),
                    published=published,
                    source=source,
                    category=detected_category,
                    priority=priority,
                    tags=tags,
                    weight=weight,
                    relevance_score=relevance_score
                )
                
                news_items.append(news_item)
            
            logger.info(f"   📰 {len(news_items)} News von {source} ({feed_category}) geparst")
            return news_items
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen von RSS Content: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Entfernt HTML Tags aus Text"""
        if not text:
            return ""
        
        # HTML Tags entfernen
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # HTML Entities dekodieren
        clean_text = html.unescape(clean_text)
        
        # Mehrfache Leerzeichen entfernen
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
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
                "schweiz": "lokale_news_schweiz",
                "zurich": "lokale_news_schweiz",
                "wirtschaft": "wirtschaft", 
                "business": "wirtschaft",
                "sport": "sport",
                "digital": "technologie",
                "technologie": "technologie",
                "technology": "technologie",
                "tech": "technologie",
                "international": "weltpolitik",
                "world": "weltpolitik",
                "news": "lokale_news_schweiz",
                "bitcoin": "bitcoin_crypto",
                "latest": "lokale_news_schweiz"
            }
            return category_mapping.get(feed_category, "lokale_news_schweiz")
        
        return best_category[0]
    
    def _calculate_priority(self, text: str, category: str, base_priority: int) -> int:
        """Berechnet Priorität basierend auf Keywords und Kategorie"""
        text_lower = text.lower()
        priority = base_priority  # Basis-Priorität aus Feed-Konfiguration
        
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
        
        # Bitcoin Keywords (wichtig für RadioX)
        for keyword in self.priority_keywords["bitcoin"]:
            if keyword in text_lower:
                priority += 2
                break
        
        # Economy Keywords
        for keyword in self.priority_keywords["economy"]:
            if keyword in text_lower:
                priority += 1
                break
        
        # Kategorie-basierte Priorität
        category_priority = {
            "bitcoin_crypto": 3,
            "wirtschaft": 2,
            "lokale_news_schweiz": 2,
            "weltpolitik": 1,
            "technologie": 1,
            "wissenschaft": 0,
            "sport": -1,
            "entertainment": -2
        }
        
        priority += category_priority.get(category, 0)
        
        # Priorität zwischen 1-10 begrenzen
        return max(1, min(10, priority))
    
    def _calculate_relevance_score(self, text: str, category: str) -> float:
        """Berechnet Relevance Score für News Item"""
        score = 0.5  # Basis-Score
        
        text_lower = text.lower()
        
        # Kategorie-spezifisches Scoring
        if category in self.category_keywords:
            keywords = self.category_keywords[category]
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
            if keyword_matches > 0:
                score += min(0.3, keyword_matches * 0.05)
        
        # Schweizer Boost
        swiss_terms = ['schweiz', 'zürich', 'basel', 'bern', 'snb', 'chf']
        swiss_matches = sum(1 for term in swiss_terms if term in text_lower)
        if swiss_matches > 0:
            score += min(0.2, swiss_matches * 0.05)
        
        return min(1.0, round(score, 2))
    
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
        sources: List[str] = None,
        categories: List[str] = None,
        max_items: int = 20
    ) -> List[RSSNewsItem]:
        """Sammelt aktuelle News von konfigurierten Quellen"""
        
        if not sources:
            sources = ["nzz", "srf", "cointelegraph", "techcrunch", "bbc"]
        
        logger.info(f"📰 Sammle News von {len(sources)} Quellen...")
        
        all_news = []
        tasks = []
        
        # Alle RSS Feeds parallel laden
        for source in sources:
            if source in self.rss_feeds:
                source_config = self.rss_feeds[source]
                source_feeds = source_config["feeds"]
                
                for feed_category, feed_url in source_feeds.items():
                    if not categories or feed_category in categories:
                        task = self.fetch_rss_feed(
                            feed_url, 
                            source, 
                            feed_category,
                            source_config["priority"],
                            source_config["weight"]
                        )
                        tasks.append(task)
        
        # Alle Feeds parallel verarbeiten
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse sammeln
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"RSS Feed Fehler: {result}")
        
        # Nach Priorität, Relevanz und Datum sortieren
        all_news.sort(key=lambda x: (
            x.priority * x.weight,
            x.relevance_score,
            x.published.timestamp()
        ), reverse=True)
        
        # Duplikate entfernen
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
                if len(title_words) > 0 and len(title_words | seen_words) > 0:
                    if len(title_words & seen_words) / len(title_words | seen_words) > 0.7:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_news.append(item)
                seen_titles.add(simple_title)
        
        return unique_news


# ==================== CONVENIENCE FUNCTIONS ====================

async def get_zurich_news(max_items: int = 20) -> List[RSSNewsItem]:
    """Holt aktuelle News für Zürich Radio-Kanal"""
    service = RSSService()
    return await service.get_recent_news("zurich", max_age_hours=2)

async def get_breaking_news() -> List[RSSNewsItem]:
    """Holt Breaking News von allen Quellen"""
    service = RSSService()
    news = await service.get_latest_news(
        sources=["nzz", "srf", "reuters", "bbc", "cointelegraph"],
        max_items=15
    )
    # Nur hohe Priorität
    return [item for item in news if item.priority >= 7]

async def get_crypto_news() -> List[RSSNewsItem]:
    """Holt Bitcoin/Crypto News"""
    service = RSSService()
    return await service.get_latest_news(
        sources=["cointelegraph", "coindesk"],
        categories=["bitcoin", "latest"],
        max_items=10
    )

async def get_tech_news() -> List[RSSNewsItem]:
    """Holt Tech News"""
    service = RSSService()
    return await service.get_latest_news(
        sources=["techcrunch", "theverge", "arstechnica", "wired"],
        categories=["tech", "latest", "ai"],
        max_items=10
    )

# ============================================================
# STANDALONE CLI INTERFACE
# ============================================================

async def main():
    """CLI Interface für RSS Service"""
    import argparse
    import sys
    import os
    
    # Standalone Mode: Add backend to path for settings
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    parser = argparse.ArgumentParser(description="🔗 RadioX RSS Service")
    parser.add_argument("--action", required=True, choices=[
        "test", "feeds", "news", "channel-feeds", "recent", "crypto", "tech"
    ], help="Aktion")
    parser.add_argument("--channel", default="zurich", help="Kanal (zurich, basel, bern)")
    parser.add_argument("--hours", type=int, default=24, help="Stunden zurück")
    parser.add_argument("--limit", type=int, default=10, help="Max. Anzahl")
    
    args = parser.parse_args()
    
    print("🔗 RSS SERVICE")
    print("=" * 50)
    
    service = RSSService()
    
    if args.action == "test":
        print("🧪 Teste RSS Service...")
        success = await service.test_rss_feeds()
        print(f"✅ Test {'erfolgreich' if success else 'fehlgeschlagen'}")
        
    elif args.action == "feeds":
        print("📡 Alle RSS Feeds:")
        for source_name, config in service.rss_feeds.items():
            print(f"\n📰 {source_name.upper()} (Priorität: {config['priority']})")
            for category, url in config['feeds'].items():
                print(f"  • {category}: {url[:50]}...")
                
    elif args.action == "channel-feeds":
        print(f"📡 RSS Feeds für Kanal '{args.channel}':")
        feeds = await service.get_feeds_for_channel(args.channel)
        for i, feed in enumerate(feeds, 1):
            print(f"{i:2d}. {feed['source_name']} ({feed['feed_category']})")
            print(f"    🔗 {feed['feed_url'][:60]}...")
            print(f"    📊 Priorität: {feed['priority']}, Gewicht: {feed['weight']}")
            
    elif args.action == "news":
        print(f"📰 Sammle News für Kanal '{args.channel}'...")
        news = await service.get_recent_news(args.channel, args.hours)
        print(f"✅ {len(news)} News gefunden:")
        
        for i, article in enumerate(news[:args.limit], 1):
            hours_old = int((datetime.now() - article.published).total_seconds() / 3600)
            print(f"\n{i:2d}. [{article.category}] {article.title}")
            print(f"    📰 {article.source} | ⏰ {hours_old}h alt | 🎯 P{article.priority}")
            print(f"    📝 {article.summary[:80]}...")
            
    elif args.action == "recent":
        print(f"📰 Neueste News (letzte {args.hours}h)...")
        news = await service.get_latest_news(max_items=args.limit)
        
        print(f"✅ {len(news)} News gefunden:")
        for i, article in enumerate(news, 1):
            hours_old = int((datetime.now() - article.published).total_seconds() / 3600)
            print(f"{i:2d}. [{article.source}] {article.title}")
            print(f"    ⏰ {hours_old}h alt | 🎯 P{article.priority} | ⭐ {article.relevance_score}")
            
    elif args.action == "crypto":
        print("₿ Bitcoin/Crypto News...")
        news = await get_crypto_news()
        for i, article in enumerate(news, 1):
            hours_old = int((datetime.now() - article.published).total_seconds() / 3600)
            print(f"{i:2d}. {article.title}")
            print(f"    📰 {article.source} | ⏰ {hours_old}h alt")
            
    elif args.action == "tech":
        print("💻 Tech News...")
        news = await get_tech_news()
        for i, article in enumerate(news, 1):
            hours_old = int((datetime.now() - article.published).total_seconds() / 3600)
            print(f"{i:2d}. {article.title}")
            print(f"    📰 {article.source} | ⏰ {hours_old}h alt")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 