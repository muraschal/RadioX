"""
RadioX Supabase Service
Speichert und verwaltet Radio-Skripte in der Supabase Datenbank
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass, asdict
from pathlib import Path

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from root directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


@dataclass
class RadioScript:
    """Radio Script für Supabase"""
    id: str
    station_type: str
    target_hour: datetime
    total_duration_seconds: int
    segment_count: int
    news_count: int
    tweet_count: int
    weather_city: str
    script_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    status: str = "generated"  # generated, gpt_enhanced, audio_ready, published


class SupabaseService:
    """Supabase Service für RadioX"""
    
    def __init__(self):
        # Lade Environment-Variablen (mehrere Varianten für Kompatibilität)
                # Import centralized settings
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from config.settings import get_settings
        
        settings = get_settings()
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_anon_key
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("❌ Supabase Credentials nicht gefunden!")
            logger.info("💡 Prüfe PUBLIC_SUPABASE_URL und PUBLIC_SUPABASE_ANON_KEY in der .env Datei")
            logger.info(f"🔍 SUPABASE_URL: {'✅ gefunden' if self.supabase_url else '❌ fehlt'}")
            logger.info(f"🔍 SUPABASE_ANON_KEY: {'✅ gefunden' if self.supabase_key else '❌ fehlt'}")
            raise ValueError("❌ Supabase Credentials fehlen!")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("✅ Supabase Client initialisiert")
    
    async def save_radio_script(self, script_data: Dict[str, Any]) -> str:
        """Speichert ein Radio-Skript in Supabase"""
        try:
            # Script ID extrahieren
            script_id = script_data.get('script_id')
            if not script_id:
                raise ValueError("Script ID fehlt")
            
            # Metadaten extrahieren
            metadata = script_data.get('metadata', {})
            segments = script_data.get('segments', [])
            
            # Radio Script Object erstellen
            radio_script = RadioScript(
                id=script_id,
                station_type=metadata.get('station_type', 'breaking_news'),
                target_hour=datetime.fromisoformat(metadata.get('target_hour')),
                total_duration_seconds=script_data.get('total_duration_seconds', 0),
                segment_count=len(segments),
                news_count=len([s for s in segments if s.get('type') == 'news']),
                tweet_count=len([s for s in segments if s.get('type') == 'tweet']),
                weather_city=metadata.get('weather_city', ''),
                script_data=script_data,
                metadata=metadata,
                created_at=datetime.utcnow(),
                status="generated"
            )
            
            # In Supabase speichern
            result = self.client.table('radio_scripts').insert(asdict(radio_script)).execute()
            
            if result.data:
                logger.info(f"✅ Radio-Skript {script_id} in Supabase gespeichert")
                return script_id
            else:
                logger.error(f"❌ Fehler beim Speichern von {script_id}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Supabase Fehler: {e}")
            return None
    
    async def get_radio_script(self, script_id: str) -> Optional[Dict[str, Any]]:
        """Lädt ein Radio-Skript aus Supabase"""
        try:
            result = self.client.table('radio_scripts').select('*').eq('id', script_id).execute()
            
            if result.data and len(result.data) > 0:
                script = result.data[0]
                logger.info(f"✅ Radio-Skript {script_id} geladen")
                return script
            else:
                logger.warning(f"📭 Radio-Skript {script_id} nicht gefunden")
                return None
                
        except Exception as e:
            logger.error(f"💥 Fehler beim Laden von {script_id}: {e}")
            return None
    
    async def list_radio_scripts(
        self, 
        station_type: str = None,
        limit: int = 50,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """Listet Radio-Skripte auf"""
        try:
            query = self.client.table('radio_scripts').select('*')
            
            if station_type:
                query = query.eq('station_type', station_type)
            
            if status:
                query = query.eq('status', status)
            
            query = query.order('created_at', desc=True).limit(limit)
            
            result = query.execute()
            
            if result.data:
                logger.info(f"✅ {len(result.data)} Radio-Skripte geladen")
                return result.data
            else:
                logger.info("📭 Keine Radio-Skripte gefunden")
                return []
                
        except Exception as e:
            logger.error(f"💥 Fehler beim Listen der Skripte: {e}")
            return []
    
    async def update_script_status(self, script_id: str, status: str, metadata: Dict = None) -> bool:
        """Aktualisiert den Status eines Skripts"""
        try:
            update_data = {'status': status}
            
            if metadata:
                # Merge mit existierenden Metadaten
                existing = await self.get_radio_script(script_id)
                if existing:
                    existing_metadata = existing.get('metadata', {})
                    existing_metadata.update(metadata)
                    update_data['metadata'] = existing_metadata
            
            result = self.client.table('radio_scripts').update(update_data).eq('id', script_id).execute()
            
            if result.data:
                logger.info(f"✅ Status von {script_id} auf '{status}' aktualisiert")
                return True
            else:
                logger.error(f"❌ Fehler beim Aktualisieren von {script_id}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Fehler beim Status-Update: {e}")
            return False
    
    async def save_news_content(self, news_items: List[Dict[str, Any]]) -> int:
        """Speichert News-Content in Supabase"""
        try:
            saved_count = 0
            
            for news_item in news_items:
                # Prüfen ob News bereits existiert (Duplikat-Vermeidung)
                existing = self.client.table('news_content').select('id').eq('title', news_item.get('title')).execute()
                
                if not existing.data:
                    # News-Item für Supabase vorbereiten
                    news_data = {
                        'title': news_item.get('title', ''),
                        'summary': news_item.get('summary', ''),
                        'source': news_item.get('source', ''),
                        'category': news_item.get('category', ''),
                        'priority': news_item.get('priority', 5),
                        'published_at': news_item.get('timestamp', datetime.utcnow()).isoformat(),
                        'content_type': 'rss_news',
                        'metadata': {
                            'link': news_item.get('link', ''),
                            'tags': news_item.get('tags', [])
                        },
                        'created_at': datetime.utcnow().isoformat()
                    }
                    
                    result = self.client.table('news_content').insert(news_data).execute()
                    
                    if result.data:
                        saved_count += 1
            
            logger.info(f"✅ {saved_count} News-Items in Supabase gespeichert")
            return saved_count
            
        except Exception as e:
            logger.error(f"💥 Fehler beim Speichern der News: {e}")
            return 0
    
    async def save_tweet_content(self, tweets: List[Dict[str, Any]]) -> int:
        """Speichert Tweet-Content in Supabase"""
        try:
            saved_count = 0
            
            for tweet in tweets:
                # Prüfen ob Tweet bereits existiert
                existing = self.client.table('news_content').select('id').eq('metadata->>tweet_id', tweet.get('id')).execute()
                
                if not existing.data:
                    # Tweet für Supabase vorbereiten
                    tweet_data = {
                        'title': f"@{tweet.get('author_username')}: {tweet.get('text', '')[:100]}...",
                        'summary': tweet.get('text', ''),
                        'source': f"twitter_{tweet.get('author_username')}",
                        'category': tweet.get('category', 'bitcoin'),
                        'priority': tweet.get('priority', 5),
                        'published_at': tweet.get('created_at', datetime.utcnow()).isoformat(),
                        'content_type': 'x_tweet',
                        'metadata': {
                            'tweet_id': tweet.get('id'),
                            'author_username': tweet.get('author_username'),
                            'author_name': tweet.get('author_name'),
                            'like_count': tweet.get('like_count', 0),
                            'retweet_count': tweet.get('retweet_count', 0),
                            'url': tweet.get('url', ''),
                            'tags': tweet.get('tags', [])
                        },
                        'created_at': datetime.utcnow().isoformat()
                    }
                    
                    result = self.client.table('news_content').insert(tweet_data).execute()
                    
                    if result.data:
                        saved_count += 1
            
            logger.info(f"✅ {saved_count} Tweets in Supabase gespeichert")
            return saved_count
            
        except Exception as e:
            logger.error(f"💥 Fehler beim Speichern der Tweets: {e}")
            return 0
    
    async def get_recent_content(
        self, 
        content_type: str = None,
        hours_back: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lädt recent Content aus Supabase"""
        try:
            since_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            query = self.client.table('news_content').select('*')
            
            if content_type:
                query = query.eq('content_type', content_type)
            
            query = query.gte('published_at', since_time.isoformat())
            query = query.order('published_at', desc=True).limit(limit)
            
            result = query.execute()
            
            if result.data:
                logger.info(f"✅ {len(result.data)} Content-Items geladen")
                return result.data
            else:
                logger.info("📭 Kein recent Content gefunden")
                return []
                
        except Exception as e:
            logger.error(f"💥 Fehler beim Laden des Contents: {e}")
            return []


# Convenience Functions
async def save_script_to_supabase(script_data: Dict[str, Any]) -> str:
    """Speichert ein Radio-Skript in Supabase"""
    service = SupabaseService()
    return await service.save_radio_script(script_data)

async def get_script_from_supabase(script_id: str) -> Optional[Dict[str, Any]]:
    """Lädt ein Radio-Skript aus Supabase"""
    service = SupabaseService()
    return await service.get_radio_script(script_id)

async def list_scripts_from_supabase(station_type: str = None) -> List[Dict[str, Any]]:
    """Listet Radio-Skripte aus Supabase"""
    service = SupabaseService()
    return await service.list_radio_scripts(station_type=station_type) 