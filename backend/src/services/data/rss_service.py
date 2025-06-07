#!/usr/bin/env python3

"""
RSS Service
===========

Service für das Sammeln und Verarbeiten von RSS Feed Daten.
Teil der Data Layer in der Clean Architecture.
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger

# Import Supabase Client
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database.supabase_client import get_db


@dataclass
class RSSNewsItem:
    """Einzelner RSS News Artikel"""
    title: str
    summary: str
    link: str
    published: datetime
    source: str
    category: str
    priority: int = 5
    weight: float = 1.0


class RSSService:
    """
    RSS Service für News-Sammlung
    
    Sammelt News von konfigurierten RSS Feeds aus der Datenbank.
    """
    
    def __init__(self):
        self.db = get_db()
        self.session = None
    
    async def get_all_active_feeds(self) -> List[Dict[str, Any]]:
        """
        Hole alle aktiven RSS Feeds aus der Datenbank
        
        Returns:
            Liste von Feed-Konfigurationen
        """
        
        try:
            response = self.db.client.table('rss_feed_preferences').select('*').eq('is_active', True).execute()
            
            if response.data:
                logger.info(f"✅ {len(response.data)} aktive RSS Feeds geladen")
                return response.data
            else:
                logger.warning("⚠️ Keine aktiven RSS Feeds gefunden")
                return []
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der RSS Feeds: {e}")
            return []
    
    async def get_all_recent_news(self, max_age_hours: int = 12) -> List[RSSNewsItem]:
        """
        Sammelt aktuelle News von allen aktiven RSS Feeds
        
        Args:
            max_age_hours: Maximales Alter der News in Stunden
            
        Returns:
            Liste von RSSNewsItem Objekten, sortiert nach Datum
        """
        
        logger.info(f"📡 Sammle News von allen Feeds (max {max_age_hours}h alt)")
        
        # Hole alle aktiven Feeds
        feeds = await self.get_all_active_feeds()
        
        if not feeds:
            logger.warning("⚠️ Keine Feeds verfügbar")
            return []
        
        # Sammle News von allen Feeds parallel
        all_news = []
        
        # HTTP Session erstellen
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'RadioX RSS Reader 1.0'}
        ) as session:
            self.session = session
            
            # Sammle von allen Feeds parallel
            tasks = []
            for feed in feeds:
                task = self._fetch_feed_news(feed, max_age_hours)
                tasks.append(task)
            
            # Warte auf alle Feeds
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sammle alle erfolgreichen Ergebnisse
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Feed {i+1} Fehler: {result}")
                elif isinstance(result, list):
                    all_news.extend(result)
        
        # Sortiere nach Datum (neueste zuerst)
        all_news.sort(key=lambda x: x.published, reverse=True)
        
        logger.info(f"✅ {len(all_news)} News gesammelt von {len(feeds)} Feeds")
        return all_news
    
    async def _fetch_feed_news(self, feed: Dict[str, Any], max_age_hours: int) -> List[RSSNewsItem]:
        """
        Sammelt News von einem einzelnen Feed
        
        Args:
            feed: Feed-Konfiguration aus der Datenbank
            max_age_hours: Maximales Alter der News
            
        Returns:
            Liste von RSSNewsItem Objekten
        """
        
        # Verwende die richtigen Feldnamen aus rss_feed_preferences
        feed_name = feed.get('source_name', 'Unknown')
        feed_url = feed.get('feed_url', '')
        feed_category = feed.get('feed_category', 'general')
        
        if not feed_url:
            logger.warning(f"⚠️ Feed {feed_name} hat keine URL")
            return []
    
        try:
            logger.debug(f"📡 Lade Feed: {feed_name}")
            
            # HTTP Request
            async with self.session.get(feed_url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Feed {feed_name} HTTP {response.status}")
                    return []
    
                content = await response.text()
            
            # Parse RSS/Atom Feed
            parsed_feed = feedparser.parse(content)
            
            if parsed_feed.bozo:
                logger.warning(f"⚠️ Feed {feed_name} hat Parse-Fehler: {parsed_feed.bozo_exception}")
            
            # Konvertiere Entries zu RSSNewsItem
            news_items = []
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            for entry in parsed_feed.entries:
                try:
                    # Parse Datum
                    published = self._parse_entry_date(entry)
                
                    # Prüfe Alter
                    if published < cutoff_time:
                        continue
                
                    # Erstelle News Item
                    news_item = RSSNewsItem(
                        title=entry.get('title', 'Kein Titel'),
                        summary=entry.get('summary', entry.get('description', 'Keine Beschreibung')),
                        link=entry.get('link', ''),
                        published=published,
                        source=self._extract_source_name(feed_name),
                        category=feed_category,
                        priority=feed.get('priority', 5),
                        weight=feed.get('weight', 1.0)
                    )
                
                    news_items.append(news_item)
            
                except Exception as e:
                    logger.warning(f"⚠️ Fehler bei Entry von {feed_name}: {e}")
                    continue
            
            logger.debug(f"✅ {feed_name}: {len(news_items)} News")
            return news_items
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Feed {feed_name}: {e}")
            return []
    
    def _parse_entry_date(self, entry: Dict[str, Any]) -> datetime:
        """Parse das Datum eines RSS Entry"""
        
        # Verschiedene Datum-Felder probieren
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])
                except:
                    continue
        
        # Fallback: String-Parsing
        date_strings = ['published', 'updated', 'created']
        for field in date_strings:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    from dateutil import parser
                    return parser.parse(getattr(entry, field))
                except:
                    continue
        
        # Letzter Fallback: Jetzt
        logger.warning("⚠️ Konnte Datum nicht parsen, verwende jetzt")
        return datetime.now()
    
    def _extract_source_name(self, feed_name: str) -> str:
        """Extrahiert einen sauberen Source-Namen"""
        
        # Entferne Präfixe und normalisiere
        clean_name = feed_name.lower()
        clean_name = clean_name.replace('_', ' ')
        clean_name = clean_name.replace('-', ' ')
        
        # Kapitalisiere ersten Buchstaben
        return clean_name.title()

    async def fetch_feed_items(self, feed_url: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Hole Items von einem einzelnen Feed (für Debug/Test)
        
        Args:
            feed_url: URL des RSS Feeds
            max_items: Maximale Anzahl Items
            
        Returns:
            Liste von Feed Items als Dictionaries
        """
        
        try:
            # HTTP Session erstellen falls nicht vorhanden
            if not self.session:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={'User-Agent': 'RadioX RSS Reader 1.0'}
                ) as session:
                    async with session.get(feed_url) as response:
                        if response.status != 200:
                            logger.warning(f"⚠️ Feed HTTP {response.status}: {feed_url}")
                            return []
                        
                        content = await response.text()
            else:
                async with self.session.get(feed_url) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ Feed HTTP {response.status}: {feed_url}")
                        return []
                    
                    content = await response.text()
            
            # Parse RSS/Atom Feed
            parsed_feed = feedparser.parse(content)
            
            if parsed_feed.bozo:
                logger.warning(f"⚠️ Feed Parse-Fehler: {parsed_feed.bozo_exception}")
            
            # Konvertiere zu Dictionary Format
            items = []
            for entry in parsed_feed.entries[:max_items]:
                item = {
                    'title': entry.get('title', 'Kein Titel'),
                    'summary': entry.get('summary', entry.get('description', 'Keine Beschreibung')),
                    'link': entry.get('link', ''),
                    'published': self._parse_entry_date(entry),
                    'source': feed_url
                }
                items.append(item)
            
            logger.debug(f"✅ {len(items)} Items von {feed_url}")
            return items
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Feed {feed_url}: {e}")
            return []

    async def test_connection(self) -> bool:
        """Testet die RSS Service Verbindung"""
        
        try:
            feeds = await self.get_all_active_feeds()
            return len(feeds) > 0
        except Exception as e:
            logger.error(f"❌ RSS Service Test Fehler: {e}")
            return False