"""
RSS Feed Service für RadioX
Sammelt News von RSS Feeds verschiedener Kategorien
"""

import feedparser
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import sys
import os
import re
from urllib.parse import urlparse

# Backend-Pfad hinzufügen für relative Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import get_settings
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class RSSService:
    """Service für RSS Feed Integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase = SupabaseClient()
    
    async def fetch_rss_feed(self, url: str, max_entries: int = 10) -> List[Dict]:
        """
        Holt RSS Feed Einträge
        
        Args:
            url: RSS Feed URL
            max_entries: Maximale Anzahl Einträge
            
        Returns:
            Liste von RSS Entry Dictionaries
        """
        try:
            # RSS Feed parsen
            feed = feedparser.parse(url)
            
            if feed.bozo:
                logger.warning(f"RSS Feed möglicherweise fehlerhaft: {url}")
            
            entries = []
            
            for entry in feed.entries[:max_entries]:
                # Datum parsen
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])
                else:
                    published_date = datetime.now()
                
                # Nur Artikel der letzten 24h
                if published_date < datetime.now() - timedelta(hours=24):
                    continue
                
                # Entry formatieren
                formatted_entry = {
                    'id': entry.get('id', entry.get('link', '')),
                    'title': entry.get('title', ''),
                    'summary': self._clean_html(entry.get('summary', entry.get('description', ''))),
                    'link': entry.get('link', ''),
                    'published_date': published_date,
                    'author': entry.get('author', ''),
                    'source_name': feed.feed.get('title', urlparse(url).netloc),
                    'tags': [tag.term for tag in entry.get('tags', [])],
                    'content_type': 'rss'
                }
                
                entries.append(formatted_entry)
            
            logger.info(f"{len(entries)} RSS Einträge von {url} abgerufen")
            return entries
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des RSS Feeds {url}: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Entfernt HTML Tags aus Text"""
        if not text:
            return ""
        
        # HTML Tags entfernen
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # HTML Entities dekodieren
        import html
        clean_text = html.unescape(clean_text)
        
        # Mehrfache Leerzeichen entfernen
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    async def collect_rss_for_category(self, category_slug: str) -> List[Dict]:
        """
        Sammelt RSS Feeds für eine bestimmte Kategorie
        
        Args:
            category_slug: Kategorie (bitcoin, wirtschaft, etc.)
            
        Returns:
            Liste aller RSS Einträge der Kategorie
        """
        try:
            # RSS Sources für Kategorie abrufen
            sources = await self.supabase.get_content_sources_by_category(
                category_slug=category_slug,
                source_type='rss',
                active_only=True
            )
            
            if not sources:
                logger.info(f"Keine RSS Sources für Kategorie {category_slug} gefunden")
                return []
            
            all_entries = []
            
            # RSS Feeds von allen Sources sammeln
            for source in sources:
                feed_url = source['identifier']
                entries = await self.fetch_rss_feed(feed_url, max_entries=5)
                
                # Source-Info zu jedem Entry hinzufügen
                for entry in entries:
                    entry['source_id'] = source['id']
                    entry['category_slug'] = category_slug
                    entry['priority_level'] = source['priority_level']
                    entry['relevance_score'] = self._calculate_relevance_score(entry, category_slug)
                
                all_entries.extend(entries)
            
            # Nach Relevanz und Priorität sortieren
            all_entries.sort(key=lambda x: (
                -x['priority_level'],
                -x['relevance_score'],
                -x['published_date'].timestamp()
            ))
            
            logger.info(f"{len(all_entries)} RSS Einträge für Kategorie {category_slug} gesammelt")
            return all_entries
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der RSS Feeds für {category_slug}: {e}")
            return []
    
    def _calculate_relevance_score(self, entry: Dict, category_slug: str) -> float:
        """
        Berechnet Relevance Score für RSS Entry
        
        Args:
            entry: RSS Entry Dictionary
            category_slug: Kategorie
            
        Returns:
            Relevance Score (0.0 - 1.0)
        """
        score = 0.5  # Basis-Score
        
        text_content = f"{entry['title']} {entry['summary']}".lower()
        
        # Kategorie-spezifische Keywords
        category_keywords = {
            'bitcoin': ['bitcoin', 'btc', 'cryptocurrency', 'blockchain', 'crypto', 'satoshi', 'mining'],
            'wirtschaft': ['wirtschaft', 'finanzen', 'börse', 'aktien', 'inflation', 'zinsen', 'bank'],
            'technologie': ['technologie', 'tech', 'ai', 'künstliche intelligenz', 'software', 'startup'],
            'weltpolitik': ['politik', 'regierung', 'wahl', 'präsident', 'minister', 'parlament'],
            'sport': ['sport', 'fussball', 'tennis', 'olympia', 'weltmeisterschaft', 'bundesliga'],
            'lokale_news_schweiz': ['schweiz', 'zürich', 'bern', 'basel', 'snb', 'nationalbank', 'chf'],
            'wissenschaft': ['wissenschaft', 'forschung', 'studie', 'universität', 'medizin', 'klima'],
            'entertainment': ['entertainment', 'film', 'musik', 'celebrity', 'hollywood', 'netflix']
        }
        
        keywords = category_keywords.get(category_slug, [])
        
        # Keyword-Matching
        keyword_matches = sum(1 for keyword in keywords if keyword in text_content)
        if keyword_matches > 0:
            score += min(0.3, keyword_matches * 0.1)
        
        # Schweizer Boost für lokale News
        if category_slug == 'lokale_news_schweiz':
            swiss_terms = ['zürich', 'schweiz', 'snb', 'chf', 'bundesrat']
            swiss_matches = sum(1 for term in swiss_terms if term in text_content)
            if swiss_matches > 0:
                score += min(0.2, swiss_matches * 0.05)
        
        # Aktualitäts-Boost (neuere Artikel bevorzugen)
        hours_old = (datetime.now() - entry['published_date']).total_seconds() / 3600
        if hours_old < 2:
            score += 0.1
        elif hours_old < 6:
            score += 0.05
        
        return min(1.0, round(score, 2))
    
    async def save_rss_entries_to_db(self, entries: List[Dict], stream_id: Optional[str] = None) -> int:
        """
        Speichert RSS Einträge in der Datenbank
        
        Args:
            entries: Liste von RSS Entry Dictionaries
            stream_id: Optional Stream ID
            
        Returns:
            Anzahl gespeicherter Einträge
        """
        saved_count = 0
        
        try:
            for entry in entries:
                # Prüfen ob Entry bereits existiert
                existing = await self.supabase.get_news_content_by_external_id(
                    external_id=entry['id']
                )
                
                if existing:
                    continue  # Entry bereits vorhanden
                
                # Entry in news_content speichern
                news_data = {
                    'stream_id': stream_id,
                    'category_id': await self.supabase.get_category_id_by_slug(entry['category_slug']),
                    'source_id': entry['source_id'],
                    'content_type': 'rss',
                    'original_text': f"{entry['title']}\n\n{entry['summary']}",
                    'relevance_score': entry['relevance_score'],
                    'sentiment_score': 0.0,  # Wird später von GPT berechnet
                    'metadata': {
                        'rss_id': entry['id'],
                        'title': entry['title'],
                        'link': entry['link'],
                        'published_date': entry['published_date'].isoformat(),
                        'author': entry['author'],
                        'source_name': entry['source_name'],
                        'tags': entry['tags']
                    }
                }
                
                await self.supabase.create_news_content(news_data)
                saved_count += 1
            
            logger.info(f"{saved_count} neue RSS Einträge in Datenbank gespeichert")
            return saved_count
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der RSS Einträge: {e}")
            return saved_count


# Async Wrapper für einfache Nutzung
async def collect_latest_rss_news() -> Dict[str, List[Dict]]:
    """Sammelt die neuesten RSS News aller Kategorien"""
    service = RSSService()
    
    # Alle aktiven Kategorien abrufen
    categories = await service.supabase.get_active_categories()
    all_news = {}
    
    for category in categories:
        category_slug = category['slug']
        news = await service.collect_rss_for_category(category_slug)
        all_news[category_slug] = news
    
    return all_news


async def collect_rss_for_stream(stream_id: str, category_mix: Dict[str, int]) -> int:
    """
    Sammelt RSS News für einen spezifischen Stream basierend auf Category Mix
    
    Args:
        stream_id: Stream ID
        category_mix: Dictionary mit Kategorie -> Prozent
        
    Returns:
        Anzahl gesammelter News
    """
    service = RSSService()
    total_saved = 0
    
    for category_slug, percentage in category_mix.items():
        if percentage > 0:
            # Anzahl News basierend auf Prozentsatz
            max_news = max(1, int(percentage / 20))  # 20% = 1 News, 60% = 3 News
            
            news = await service.collect_rss_for_category(category_slug)
            selected_news = news[:max_news]  # Top News nehmen
            
            saved = await service.save_rss_entries_to_db(selected_news, stream_id)
            total_saved += saved
    
    return total_saved 