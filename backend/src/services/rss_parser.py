"""
RadioX RSS Parser - Echte News von 20min, NZZ und anderen Schweizer Medien
"""

import asyncio
import aiohttp
import feedparser
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
import re
from urllib.parse import urljoin


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


class RSSParser:
    """RSS Parser für Schweizer News-Quellen"""
    
    def __init__(self):
        # Schweizer News RSS Feeds - KORRIGIERT UND ERWEITERT!
        self.rss_feeds = {
            # 20min RSS-Feeds sind aktuell nicht verfügbar (404 Fehler)
            # "20min": {
            #     "base_url": "https://www.20min.ch",
            #     "feeds": {
            #         "schweiz": "https://www.20min.ch/rss/rss.tmpl?type=channel&get=5",
            #         "wirtschaft": "https://www.20min.ch/rss/rss.tmpl?type=channel&get=3", 
            #         "sport": "https://www.20min.ch/rss/rss.tmpl?type=channel&get=6",
            #         "digital": "https://www.20min.ch/rss/rss.tmpl?type=channel&get=54",
            #         "zurich": "https://www.20min.ch/rss/rss.tmpl?type=channel&get=10"
            #     }
            # },
            "nzz": {
                "base_url": "https://www.nzz.ch",
                "feeds": {
                    "schweiz": "https://www.nzz.ch/schweiz.rss",
                    "wirtschaft": "https://www.nzz.ch/wirtschaft.rss",
                    "international": "https://www.nzz.ch/international.rss",
                    "technologie": "https://www.nzz.ch/technologie.rss",
                    "zurich": "https://www.nzz.ch/zuerich.rss"
                }
            },
            # SRF - KORRIGIERTE FUNKTIONIERENDE FEEDS!
            "srf": {
                "base_url": "https://www.srf.ch",
                "feeds": {
                    "news": "https://www.srf.ch/news/bnf/rss/19032223",  # Das Neueste - FUNKTIONIERT!
                    "schweiz": "https://www.srf.ch/news/bnf/rss/1926",  # Schweiz News
                    "international": "https://www.srf.ch/bnf/rss/19920122",  # International
                    "wirtschaft": "https://www.srf.ch/news/bnf/rss/1646",  # Wirtschaft
                    "sport": "https://www.srf.ch/sport/bnf/rss/1948"  # Sport
                }
            },
            "tagesanzeiger": {
                "base_url": "https://www.tagesanzeiger.ch",
                "feeds": {
                    "zurich": "https://www.tagesanzeiger.ch/zuerich/rss.html",
                    "schweiz": "https://www.tagesanzeiger.ch/schweiz/rss.html",
                    "wirtschaft": "https://www.tagesanzeiger.ch/wirtschaft/rss.html"
                }
            },
            "telezueri": {
                "base_url": "https://www.telezueri.ch",
                "feeds": {
                    "zurich": "https://www.telezueri.ch/rss.xml"
                }
            },
            "zueritoday": {
                "base_url": "https://www.zueritoday.ch",
                "feeds": {
                    "zurich": "https://www.zueritoday.ch/rss.xml"
                }
            },
            # INTERNATIONALE BREAKING NEWS QUELLEN - ERWEITERT!
            "reuters": {
                "base_url": "https://www.reuters.com",
                "feeds": {
                    "breaking": "https://feeds.reuters.com/reuters/breakingviews",
                    "world": "https://feeds.reuters.com/Reuters/worldNews",
                    "business": "https://feeds.reuters.com/reuters/businessNews",
                    "technology": "https://feeds.reuters.com/reuters/technologyNews"
                }
            },
            "bbc": {
                "base_url": "https://www.bbc.com",
                "feeds": {
                    "world": "http://feeds.bbci.co.uk/news/world/rss.xml",
                    "business": "http://feeds.bbci.co.uk/news/business/rss.xml",
                    "technology": "http://feeds.bbci.co.uk/news/technology/rss.xml"
                }
            },
            "dw": {
                "base_url": "https://www.dw.com",
                "feeds": {
                    "top": "https://rss.dw.com/rdf/rss-en-top",
                    "business": "https://rss.dw.com/rdf/rss-en-bus",
                    "science": "https://rss.dw.com/rdf/rss-en-sci"
                }
            },
            # TECH NEWS QUELLEN - MASSIV ERWEITERT!
            "techcrunch": {
                "base_url": "https://techcrunch.com",
                "feeds": {
                    "latest": "https://techcrunch.com/feed/",
                    "startups": "https://techcrunch.com/category/startups/feed/",
                    "ai": "https://techcrunch.com/category/artificial-intelligence/feed/"
                }
            },
            "theverge": {
                "base_url": "https://www.theverge.com",
                "feeds": {
                    "tech": "https://www.theverge.com/rss/index.xml"
                }
            },
            "arstechnica": {
                "base_url": "https://arstechnica.com",
                "feeds": {
                    "tech": "https://feeds.arstechnica.com/arstechnica/index"
                }
            },
            "heise": {
                "base_url": "https://www.heise.de",
                "feeds": {
                    "news": "https://www.heise.de/rss/heise.rdf",
                    "security": "https://www.heise.de/security/rss/news-atom.xml"
                }
            },
            # NEUE TECH-QUELLEN!
            "wired": {
                "base_url": "https://www.wired.com",
                "feeds": {
                    "latest": "https://www.wired.com/feed/rss"
                }
            },
            "engadget": {
                "base_url": "https://www.engadget.com",
                "feeds": {
                    "tech": "https://www.engadget.com/rss.xml"
                }
            },
            "mashable": {
                "base_url": "https://mashable.com",
                "feeds": {
                    "tech": "https://mashable.com/feeds/rss/all"
                }
            },
            # BITCOIN/CRYPTO QUELLEN
            "cointelegraph": {
                "base_url": "https://cointelegraph.com",
                "feeds": {
                    "bitcoin": "https://de.cointelegraph.com/rss/tag/bitcoin",  # FUNKTIONIERT! Deutsche Version
                    "latest": "https://cointelegraph.com/rss"
                }
            },
            "coindesk": {
                "base_url": "https://www.coindesk.com",
                "feeds": {
                    "bitcoin": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                    "markets": "https://www.coindesk.com/arc/outboundfeeds/rss/"
                }
            },
            # SCHWEIZER FINANZ
            "cash": {
                "base_url": "https://www.cash.ch",
                "feeds": {
                    "top_news": "https://www.cash.ch/feeds/latest/top-news",
                    "boerse": "https://www.cash.ch/rss/450.xml",
                    "alle_news": "https://www.cash.ch/feeds/latest/news"
                }
            },
            "insideparadeplatz": {
                "base_url": "https://insideparadeplatz.ch",
                "feeds": {
                    "finanz": "https://insideparadeplatz.ch/feed/"
                }
            },
            # NEUE INTERNATIONALE QUELLEN!
            "cnn": {
                "base_url": "https://www.cnn.com",
                "feeds": {
                    "world": "http://rss.cnn.com/rss/edition.rss",
                    "business": "http://rss.cnn.com/rss/money_latest.rss",
                    "tech": "http://rss.cnn.com/rss/edition_technology.rss"
                }
            },
            "guardian": {
                "base_url": "https://www.theguardian.com",
                "feeds": {
                    "world": "https://www.theguardian.com/world/rss",
                    "business": "https://www.theguardian.com/business/rss",
                    "technology": "https://www.theguardian.com/technology/rss"
                }
            },
            "spiegel": {
                "base_url": "https://www.spiegel.de",
                "feeds": {
                    "schlagzeilen": "https://www.spiegel.de/schlagzeilen/index.rss",
                    "wirtschaft": "https://www.spiegel.de/wirtschaft/index.rss",
                    "netzwelt": "https://www.spiegel.de/netzwelt/index.rss"
                }
            }
        }
        
        # Kategorie-Keywords für automatische Klassifizierung
        self.category_keywords = {
            "bitcoin": ["bitcoin", "btc", "krypto", "blockchain", "ethereum", "crypto"],
            "wirtschaft": ["wirtschaft", "börse", "aktien", "unternehmen", "bank", "snb", "inflation"],
            "technologie": ["technologie", "tech", "ki", "ai", "software", "digital", "startup"],
            "weltpolitik": ["politik", "regierung", "parlament", "wahlen", "international"],
            "sport": ["sport", "fussball", "tennis", "ski", "olympia", "wm", "em"],
            "lokale_news_schweiz": ["schweiz", "zürich", "zurich", "basel", "bern", "genf", "lausanne", "stadt zürich", "kanton zürich", "zürcher", "züri", "limmat", "see", "hb zürich", "hauptbahnhof", "tram", "vbz", "stadtrat", "gemeinderat"],
            "wissenschaft": ["wissenschaft", "forschung", "studie", "universität", "medizin"],
            "entertainment": ["kultur", "film", "musik", "theater", "festival", "promi"]
        }
        
        # Prioritäts-Keywords (höhere Priorität)
        self.priority_keywords = {
            "breaking": ["eilmeldung", "breaking", "urgent", "sofort", "jetzt"],
            "high": ["wichtig", "bedeutend", "gross", "major", "kritisch"],
            "bitcoin": ["bitcoin", "btc", "100k", "allzeithoch", "rekord"],
            "economy": ["snb", "leitzins", "inflation", "rezession", "börsencrash"]
        }
    
    async def fetch_rss_feed(self, url: str, source: str, category: str) -> List[RSSNewsItem]:
        """Lädt RSS Feed und parst News Items"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_rss_content(content, source, category)
                    else:
                        logger.warning(f"RSS Feed Error {response.status}: {url}")
                        return []
        except Exception as e:
            logger.error(f"Fehler beim Laden von RSS Feed {url}: {e}")
            return []
    
    def _parse_rss_content(self, content: str, source: str, feed_category: str) -> List[RSSNewsItem]:
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
                detected_category = self._detect_category(text_for_analysis, feed_category)
                
                # Priorität bestimmen
                priority = self._calculate_priority(text_for_analysis, detected_category)
                
                # Tags extrahieren
                tags = self._extract_tags(text_for_analysis)
                
                news_item = RSSNewsItem(
                    title=entry.title,
                    summary=getattr(entry, 'summary', entry.title)[:200],
                    link=getattr(entry, 'link', ''),
                    published=published,
                    source=source,
                    category=detected_category,
                    priority=priority,
                    tags=tags
                )
                
                news_items.append(news_item)
            
            logger.info(f"   📰 {len(news_items)} News von {source} ({feed_category}) geparst")
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
                "schweiz": "lokale_news_schweiz",
                "wirtschaft": "wirtschaft", 
                "sport": "sport",
                "digital": "technologie",
                "technologie": "technologie",
                "international": "weltpolitik",
                "news": "lokale_news_schweiz"
            }
            return category_mapping.get(feed_category, "lokale_news_schweiz")
        
        return best_category[0]
    
    def _calculate_priority(self, text: str, category: str) -> int:
        """Berechnet Priorität basierend auf Keywords und Kategorie"""
        text_lower = text.lower()
        priority = 5  # Base priority
        
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
            "bitcoin": 2,
            "wirtschaft": 1,
            "weltpolitik": 1,
            "technologie": 1,
            "lokale_news_schweiz": 0,
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
            "börse", "aktien", "inflation", "tech", "startup", "ki", "ai"
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
        """Sammelt aktuelle News von allen konfigurierten Quellen"""
        
        if not sources:
            sources = ["nzz", "srf", "tagesanzeiger", "bbc", "cointelegraph", "techcrunch"]  # Bitcoin/Crypto + Tech hinzugefügt, Reuters entfernt
        
        logger.info(f"📰 Sammle News von {len(sources)} Quellen...")
        
        all_news = []
        tasks = []
        
        # Alle RSS Feeds parallel laden
        for source in sources:
            if source in self.rss_feeds:
                source_feeds = self.rss_feeds[source]["feeds"]
                
                for category, feed_url in source_feeds.items():
                    if not categories or category in categories:
                        task = self.fetch_rss_feed(feed_url, source, category)
                        tasks.append(task)
        
        # Alle Feeds parallel verarbeiten
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse sammeln
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"RSS Feed Fehler: {result}")
        
        # Nach Priorität und Datum sortieren
        all_news.sort(key=lambda x: (x.priority, x.published), reverse=True)
        
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
    
    async def get_breaking_news_feed(self) -> List[RSSNewsItem]:
        """Spezielle Funktion für Breaking News Station"""
        
        # Fokus auf wichtige Kategorien für Breaking News
        priority_categories = ["wirtschaft", "schweiz", "international"]
        
        news = await self.get_latest_news(
            sources=["20min", "nzz", "srf"],
            categories=priority_categories,
            max_items=15
        )
        
        # Nur hohe Priorität für Breaking News
        breaking_news = [item for item in news if item.priority >= 6]
        
        logger.info(f"🚨 {len(breaking_news)} Breaking News Items gefiltert")
        
        return breaking_news[:8]  # Top 8 für eine Stunde

    async def get_zueri_style_feed(self) -> List[RSSNewsItem]:
        """Spezielle Funktion für Züri Style Station - Fokus auf Zürich-News"""
        
        logger.info("🏔️ Sammle Zürich-fokussierte News für Züri Style...")
        
        # Zürich-spezifische Quellen priorisieren
        zurich_sources = ["20min", "nzz", "tagesanzeiger", "telezueri", "zueritoday"]
        
        # Zürich-relevante Kategorien
        zurich_categories = ["zurich", "schweiz", "wirtschaft"]
        
        news = await self.get_latest_news(
            sources=zurich_sources,
            categories=zurich_categories,
            max_items=20
        )
        
        # Zürich-News extra boosten
        zurich_boosted_news = []
        for item in news:
            # Zürich-Boost für lokale News
            if any(keyword in item.title.lower() or keyword in item.summary.lower() 
                   for keyword in ["zürich", "zurich", "züri", "stadt zürich", "kanton zürich", "zürcher"]):
                item.priority += 2  # Zürich-Boost
                item.category = "lokale_news_schweiz"  # Sicherstellen dass es als lokal kategorisiert wird
            
            zurich_boosted_news.append(item)
        
        # Nach Priorität sortieren (Zürich-News haben jetzt höhere Priorität)
        zurich_boosted_news.sort(key=lambda x: (x.priority, x.published), reverse=True)
        
        logger.info(f"🏔️ {len(zurich_boosted_news)} Zürich-fokussierte News Items gesammelt")
        
        return zurich_boosted_news[:12]  # Top 12 für Züri Style


# Convenience Functions
async def get_swiss_news(max_items: int = 10) -> List[RSSNewsItem]:
    """Holt aktuelle Schweizer News"""
    parser = RSSParser()
    return await parser.get_latest_news(max_items=max_items)

async def get_breaking_news() -> List[RSSNewsItem]:
    """Holt Breaking News für Radio Station"""
    parser = RSSParser()
    return await parser.get_breaking_news_feed() 