"""
Content Mixer für RadioX
Kombiniert alle Content-Quellen zu einem optimalen Mix
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import sys
import os

# Backend-Pfad hinzufügen für relative Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import get_settings
from database.supabase_client import SupabaseClient
from .twitter_service import TwitterService
from .rss_service import RSSService
from .weather_service import WeatherService
from src.services.rss_parser import RSSParser

logger = logging.getLogger(__name__)

class ContentMixer:
    """Zentraler Content Mixer für RadioX"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase = SupabaseClient()
        self.twitter_service = TwitterService()
        self.rss_service = RSSService()
        self.weather_service = WeatherService()
        self.rss_parser = RSSParser()
    
    async def create_comprehensive_content_mix(
        self, 
        stream_template: str = "balanced_news",
        target_duration_minutes: int = 60
    ) -> Dict:
        """
        Erstellt einen umfassenden Content-Mix für RadioX
        
        Args:
            stream_template: Template (balanced_news, bitcoin_focus, etc.)
            target_duration_minutes: Ziel-Dauer in Minuten
            
        Returns:
            Vollständiger Content-Mix
        """
        try:
            logger.info(f"Erstelle Content-Mix für Template: {stream_template}")
            
            # Stream-Template Konfiguration
            template_config = self._get_template_config(stream_template)
            
            # Content von allen Quellen sammeln
            content_mix = {
                'template': stream_template,
                'target_duration': target_duration_minutes,
                'created_at': datetime.now(),
                'categories': {},
                'weather': {},
                'total_items': 0,
                'content_breakdown': {}
            }
            
            # 1. Wetter-Update (immer dabei)
            logger.info("📡 Sammle Wetter-Daten...")
            try:
                weather_data = await self.weather_service.get_weather_for_station("zurich")
                if weather_data:
                    content_mix['weather'] = {
                        'location': weather_data.get('location', 'Zürich'),
                        'current': weather_data.get('current'),
                        'forecast': weather_data.get('forecast'),
                        'radio_current': weather_data.get('radio_current'),
                        'radio_forecast': weather_data.get('radio_forecast'),
                        'summary_text': weather_data.get('radio_current', 'Wetter nicht verfügbar'),
                        'timestamp': datetime.now().isoformat()
                    }
                    logger.info("✅ Wetter-Daten gesammelt")
                else:
                    logger.warning("⚠️ Keine Wetter-Daten verfügbar")
            except Exception as e:
                logger.error(f"❌ Fehler beim Sammeln der Wetter-Daten: {e}")
                content_mix['weather'] = {
                    'summary_text': 'Wetter momentan nicht verfügbar',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 2. RSS News sammeln (kategorie-spezifisch)
            logger.info("📰 Sammle RSS News...")
            
            # Template-spezifische RSS-Sammlung
            if stream_template == "swiss_local":
                # Für Züri Style: Spezielle Zürich-fokussierte Sammlung
                rss_news = await self.rss_parser.get_zueri_style_feed()
                logger.info(f"🏔️ Züri Style: {len(rss_news)} Zürich-fokussierte RSS Items")
            elif stream_template == "balanced_news":
                # Für Breaking News: Standard Breaking News Feed
                rss_news = await self.rss_parser.get_breaking_news_feed()
                logger.info(f"🚨 Breaking News: {len(rss_news)} RSS Items")
            else:
                # Standard RSS-Sammlung für andere Templates
                rss_news = await self.rss_parser.get_latest_news(max_items=15)
                logger.info(f"📰 Standard: {len(rss_news)} RSS Items")
            
            # RSS News nach Kategorien organisieren
            for item in rss_news:
                category = item.category
                if category not in content_mix['categories']:
                    content_mix['categories'][category] = {
                        'items': [],
                        'total_items': 0,
                        'avg_priority': 0
                    }
                
                content_mix['categories'][category]['items'].append({
                    'title': item.title,
                    'summary': item.summary,
                    'source_name': item.source,
                    'link': item.link,
                    'published_date': item.published,
                    'priority': item.priority,
                    'tags': item.tags,
                    'content_type': 'rss'
                })
                content_mix['categories'][category]['total_items'] += 1
            
            # Durchschnittliche Priorität pro Kategorie berechnen
            for category_data in content_mix['categories'].values():
                if category_data['total_items'] > 0:
                    total_priority = sum(item['priority'] for item in category_data['items'])
                    category_data['avg_priority'] = total_priority / category_data['total_items']
            
            # Gesamtanzahl Items aktualisieren
            content_mix['total_items'] = sum(
                category_data['total_items'] 
                for category_data in content_mix['categories'].values()
            )
            
            # 3. Content-Breakdown berechnen
            content_mix['content_breakdown'] = self._calculate_content_breakdown(content_mix)
            
            # 4. Qualitäts-Score berechnen
            content_mix['quality_score'] = self._calculate_quality_score(content_mix)
            
            logger.info(f"🎉 Content-Mix erstellt: {content_mix['total_items']} Items, Quality Score: {content_mix['quality_score']}")
            
            return content_mix
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Content-Mix: {e}")
            return {}
    
    def _get_template_config(self, template: str) -> Dict:
        """
        Holt Template-Konfiguration
        
        Args:
            template: Template Name
            
        Returns:
            Template-Konfiguration
        """
        templates = {
            'bitcoin_focus': {
                'name': 'Bitcoin Focus',
                'description': 'Bitcoin-fokussierter Stream',
                'category_mix': {
                    'bitcoin': 50,
                    'wirtschaft': 25,
                    'technologie': 15,
                    'lokale_news_schweiz': 10
                },
                'persona': 'maximalist'
            },
            'balanced_news': {
                'name': 'Balanced News',
                'description': 'Ausgewogener News-Mix',
                'category_mix': {
                    'bitcoin': 20,
                    'wirtschaft': 25,
                    'weltpolitik': 20,
                    'lokale_news_schweiz': 15,
                    'technologie': 10,
                    'sport': 5,
                    'entertainment': 5
                },
                'persona': 'cyberpunk'
            },
            'business_focus': {
                'name': 'Business Focus',
                'description': 'Business und Wirtschafts-fokussiert',
                'category_mix': {
                    'wirtschaft': 40,
                    'bitcoin': 30,
                    'technologie': 15,
                    'lokale_news_schweiz': 15
                },
                'persona': 'professional'
            },
            'swiss_local': {
                'name': 'Swiss Local',
                'description': 'Schweiz-fokussierte Nachrichten',
                'category_mix': {
                    'lokale_news_schweiz': 50,
                    'wirtschaft': 20,
                    'sport': 15,
                    'bitcoin': 10,
                    'entertainment': 5
                },
                'persona': 'retro'
            },
            'entertainment': {
                'name': 'Entertainment',
                'description': 'Entertainment und Lifestyle',
                'category_mix': {
                    'entertainment': 40,
                    'sport': 25,
                    'technologie': 15,
                    'lokale_news_schweiz': 10,
                    'bitcoin': 10
                },
                'persona': 'cyberpunk'
            }
        }
        
        return templates.get(template, templates['balanced_news'])
    
    async def _collect_category_content(
        self, 
        category_slug: str, 
        percentage: int,
        target_duration: int
    ) -> Dict:
        """
        Sammelt Content für eine spezifische Kategorie
        
        Args:
            category_slug: Kategorie
            percentage: Prozentsatz im Mix
            target_duration: Ziel-Dauer
            
        Returns:
            Kategorie-Content
        """
        try:
            # Anzahl Items basierend auf Prozentsatz berechnen
            # Basis: 1 Item pro 10% für 60min Stream
            base_items = max(1, int((percentage / 10) * (target_duration / 60)))
            
            category_content = {
                'category': category_slug,
                'percentage': percentage,
                'target_items': base_items,
                'items': [],
                'sources': {
                    'rss': [],
                    'twitter': []
                }
            }
            
            # RSS Content sammeln (Hauptquelle)
            rss_items = await self.rss_service.collect_rss_for_category(category_slug)
            if rss_items:
                # Top RSS Items nehmen
                selected_rss = rss_items[:max(1, base_items - 1)]
                category_content['sources']['rss'] = selected_rss
                category_content['items'].extend(selected_rss)
            
            # Twitter Content sammeln (nur für Bitcoin OG News)
            if category_slug == 'bitcoin' and base_items > 1:
                try:
                    twitter_items = await self.twitter_service.collect_tweets_for_category(category_slug)
                    if twitter_items:
                        # Nur 1 Top Tweet für OG News
                        selected_twitter = twitter_items[:1]
                        category_content['sources']['twitter'] = selected_twitter
                        category_content['items'].extend(selected_twitter)
                except Exception as e:
                    logger.warning(f"Twitter Rate Limit für {category_slug}: {e}")
            
            # Nach Relevanz sortieren
            category_content['items'].sort(
                key=lambda x: x.get('relevance_score', 0), 
                reverse=True
            )
            
            # Auf Ziel-Anzahl begrenzen
            category_content['items'] = category_content['items'][:base_items]
            category_content['actual_items'] = len(category_content['items'])
            
            return category_content
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von Content für {category_slug}: {e}")
            return {
                'category': category_slug,
                'percentage': percentage,
                'target_items': 0,
                'actual_items': 0,
                'items': [],
                'sources': {'rss': [], 'twitter': []}
            }
    
    def _calculate_content_breakdown(self, content_mix: Dict) -> Dict:
        """
        Berechnet Content-Breakdown Statistiken
        
        Args:
            content_mix: Content-Mix
            
        Returns:
            Breakdown-Statistiken
        """
        breakdown = {
            'total_items': content_mix['total_items'],
            'by_category': {},
            'by_source_type': {'rss': 0, 'twitter': 0, 'weather': 0},
            'avg_relevance_score': 0.0
        }
        
        all_scores = []
        
        # Kategorien analysieren
        for category_slug, category_data in content_mix['categories'].items():
            items = category_data.get('items', [])
            breakdown['by_category'][category_slug] = len(items)
            
            # Source-Types zählen
            for item in items:
                content_type = item.get('content_type', 'unknown')
                if content_type in breakdown['by_source_type']:
                    breakdown['by_source_type'][content_type] += 1
                
                # Relevance Scores sammeln
                score = item.get('relevance_score', 0)
                if score > 0:
                    all_scores.append(score)
        
        # Wetter hinzufügen
        if content_mix.get('weather'):
            breakdown['by_source_type']['weather'] = 1
            all_scores.append(0.8)  # Wetter hat fixen Score
        
        # Durchschnittlicher Relevance Score
        if all_scores:
            breakdown['avg_relevance_score'] = round(sum(all_scores) / len(all_scores), 2)
        
        return breakdown
    
    def _calculate_quality_score(self, content_mix: Dict) -> float:
        """
        Berechnet Qualitäts-Score für Content-Mix
        
        Args:
            content_mix: Content-Mix
            
        Returns:
            Qualitäts-Score (0.0 - 1.0)
        """
        score = 0.0
        
        # Basis-Score: Anzahl Items
        total_items = content_mix['total_items']
        if total_items >= 5:
            score += 0.3
        elif total_items >= 3:
            score += 0.2
        elif total_items >= 1:
            score += 0.1
        
        # Diversitäts-Score: Anzahl verschiedener Kategorien
        num_categories = len([cat for cat, data in content_mix['categories'].items() 
                             if data.get('actual_items', 0) > 0])
        if num_categories >= 4:
            score += 0.2
        elif num_categories >= 2:
            score += 0.1
        
        # Relevance-Score: Durchschnittliche Relevanz
        avg_relevance = content_mix.get('content_breakdown', {}).get('avg_relevance_score', 0)
        score += min(0.3, avg_relevance * 0.5)
        
        # Wetter-Bonus
        if content_mix.get('weather'):
            score += 0.1
        
        # Aktualitäts-Bonus: Content der letzten 6h
        recent_items = 0
        cutoff_time = datetime.now() - timedelta(hours=6)
        
        for category_data in content_mix['categories'].values():
            for item in category_data.get('items', []):
                item_time = None
                if 'published_date' in item:
                    item_time = item['published_date']
                elif 'created_at' in item:
                    item_time = item['created_at']
                
                if item_time and item_time > cutoff_time:
                    recent_items += 1
        
        if recent_items >= 3:
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    async def save_content_mix_to_stream(self, content_mix: Dict, stream_id: str) -> bool:
        """
        Speichert Content-Mix in einen Stream
        
        Args:
            content_mix: Content-Mix
            stream_id: Stream ID
            
        Returns:
            True wenn erfolgreich
        """
        try:
            saved_items = 0
            
            # Wetter speichern
            if content_mix.get('weather'):
                weather_saved = await self.weather_service.save_weather_to_db(
                    content_mix['weather'], 
                    stream_id
                )
                if weather_saved:
                    saved_items += 1
            
            # Content für jede Kategorie speichern
            for category_slug, category_data in content_mix['categories'].items():
                items = category_data.get('items', [])
                
                # RSS Items speichern
                rss_items = [item for item in items if item.get('content_type') == 'rss']
                if rss_items:
                    rss_saved = await self.rss_service.save_rss_entries_to_db(rss_items, stream_id)
                    saved_items += rss_saved
                
                # Twitter Items speichern
                twitter_items = [item for item in items if item.get('content_type') == 'tweet']
                if twitter_items:
                    twitter_saved = await self.twitter_service.save_tweets_to_db(twitter_items, stream_id)
                    saved_items += twitter_saved
            
            logger.info(f"Content-Mix gespeichert: {saved_items} Items in Stream {stream_id}")
            return saved_items > 0
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Content-Mix: {e}")
            return False


# Async Wrapper für einfache Nutzung
async def create_radio_content_mix(
    template: str = "balanced_news",
    duration_minutes: int = 60
) -> Dict:
    """
    Erstellt einen kompletten Radio-Content-Mix
    
    Args:
        template: Stream-Template
        duration_minutes: Ziel-Dauer
        
    Returns:
        Content-Mix Dictionary
    """
    mixer = ContentMixer()
    return await mixer.create_comprehensive_content_mix(template, duration_minutes)


async def create_and_save_content_for_stream(
    stream_id: str,
    template: str = "balanced_news",
    duration_minutes: int = 60
) -> Dict:
    """
    Erstellt und speichert Content für einen Stream
    
    Args:
        stream_id: Stream ID
        template: Stream-Template
        duration_minutes: Ziel-Dauer
        
    Returns:
        Content-Mix mit Speicher-Status
    """
    mixer = ContentMixer()
    
    # Content-Mix erstellen
    content_mix = await mixer.create_comprehensive_content_mix(template, duration_minutes)
    
    if content_mix:
        # In Stream speichern
        saved = await mixer.save_content_mix_to_stream(content_mix, stream_id)
        content_mix['saved_to_stream'] = saved
        content_mix['stream_id'] = stream_id
    
    return content_mix 