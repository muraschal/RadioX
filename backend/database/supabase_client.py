"""
RadioX Supabase Database Client
Zentrale Datenbankverbindung und CRUD-Operationen
"""

from supabase import create_client, Client
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
import uuid
import sys
import os
from loguru import logger

# Backend-Pfad hinzufügen für relative Imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.settings import get_settings

settings = get_settings()


class SupabaseClient:
    """RadioX Supabase Database Client"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        logger.info("Supabase Client initialisiert")
    
    # ==================== STREAMS ====================
    
    async def create_stream(
        self,
        title: str,
        description: Optional[str] = None,
        duration_minutes: int = 60,
        persona: str = "cyberpunk"
    ) -> Dict[str, Any]:
        """Erstellt einen neuen Stream"""
        try:
            stream_data = {
                "title": title,
                "description": description,
                "duration_minutes": duration_minutes,
                "persona": persona,
                "status": "planned"
            }
            
            result = self.client.table("streams").insert(stream_data).execute()
            logger.info(f"Stream erstellt: {title}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Streams: {e}")
            raise
    
    async def get_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Holt einen Stream anhand der ID"""
        try:
            result = self.client.table("streams").select("*").eq("id", stream_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Streams {stream_id}: {e}")
            return None
    
    async def update_stream_status(
        self,
        stream_id: str,
        status: str,
        file_url: Optional[str] = None,
        file_size_mb: Optional[float] = None
    ) -> bool:
        """Aktualisiert den Status eines Streams"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if status == "completed":
                update_data["generated_at"] = datetime.now(timezone.utc).isoformat()
                
            if file_url:
                update_data["file_url"] = file_url
                
            if file_size_mb:
                update_data["file_size_mb"] = file_size_mb
            
            result = self.client.table("streams").update(update_data).eq("id", stream_id).execute()
            logger.info(f"Stream {stream_id} Status aktualisiert: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Stream-Status: {e}")
            return False
    
    async def get_recent_streams(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Holt die neuesten Streams"""
        try:
            result = self.client.table("streams").select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der neuesten Streams: {e}")
            return []
    
    # ==================== SPOTIFY TRACKS ====================
    
    async def add_spotify_track(
        self,
        stream_id: str,
        spotify_url: str,
        track_name: str,
        artist_name: str,
        duration_ms: int,
        position_in_stream: int,
        youtube_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fügt einen Spotify Track zu einem Stream hinzu"""
        try:
            track_data = {
                "stream_id": stream_id,
                "spotify_url": spotify_url,
                "track_name": track_name,
                "artist_name": artist_name,
                "duration_ms": duration_ms,
                "position_in_stream": position_in_stream,
                "youtube_url": youtube_url
            }
            
            result = self.client.table("spotify_tracks").insert(track_data).execute()
            logger.info(f"Spotify Track hinzugefügt: {track_name} - {artist_name}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen des Spotify Tracks: {e}")
            raise
    
    async def get_stream_tracks(self, stream_id: str) -> List[Dict[str, Any]]:
        """Holt alle Tracks eines Streams"""
        try:
            result = self.client.table("spotify_tracks").select("*").eq("stream_id", stream_id).order("position_in_stream").execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Stream-Tracks: {e}")
            return []
    
    async def update_track_file_path(self, track_id: str, local_file_path: str) -> bool:
        """Aktualisiert den lokalen Dateipfad eines Tracks"""
        try:
            result = self.client.table("spotify_tracks").update({"local_file_path": local_file_path}).eq("id", track_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Track-Dateipfads: {e}")
            return False
    
    # ==================== NEWS CONTENT ====================
    
    async def add_news_content(
        self,
        stream_id: str,
        content_type: str,  # 'tweet', 'rss', 'weather'
        original_text: str,
        source_author: Optional[str] = None,
        source_url: Optional[str] = None,
        ai_summary: Optional[str] = None,
        relevance_score: Optional[float] = None,
        position_in_stream: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fügt News Content zu einem Stream hinzu"""
        try:
            news_data = {
                "stream_id": stream_id,
                "content_type": content_type,
                "original_text": original_text,
                "source_author": source_author,
                "source_url": source_url,
                "ai_summary": ai_summary,
                "relevance_score": relevance_score,
                "position_in_stream": position_in_stream
            }
            
            result = self.client.table("news_content").insert(news_data).execute()
            logger.info(f"News Content hinzugefügt: {content_type} von {source_author}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen des News Contents: {e}")
            raise
    
    async def get_stream_news(self, stream_id: str) -> List[Dict[str, Any]]:
        """Holt alle News eines Streams"""
        try:
            result = self.client.table("news_content").select("*").eq("stream_id", stream_id).order("position_in_stream").execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Stream-News: {e}")
            return []
    
    async def update_news_voice_file(self, news_id: str, voice_file_path: str) -> bool:
        """Aktualisiert den Voice-Dateipfad für News Content"""
        try:
            result = self.client.table("news_content").update({"voice_file_path": voice_file_path}).eq("id", news_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des News Voice-Dateipfads: {e}")
            return False
    
    # ==================== BITCOIN OG ACCOUNTS ====================
    
    async def get_active_bitcoin_ogs(self) -> List[Dict[str, Any]]:
        """Holt alle aktiven Bitcoin OG Accounts"""
        try:
            result = self.client.table("bitcoin_og_accounts").select("*").eq("is_active", True).order("priority_level").execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Bitcoin OG Accounts: {e}")
            return []
    
    async def update_og_last_checked(self, twitter_handle: str) -> bool:
        """Aktualisiert den last_checked Timestamp für einen OG Account"""
        try:
            result = self.client.table("bitcoin_og_accounts").update({
                "last_checked_at": datetime.now(timezone.utc).isoformat()
            }).eq("twitter_handle", twitter_handle).execute()
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des OG last_checked: {e}")
            return False
    
    # ==================== GENERATION LOGS ====================
    
    async def log_generation_step(
        self,
        stream_id: str,
        step: str,
        status: str,
        message: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ) -> bool:
        """Loggt einen Generierungsschritt"""
        try:
            log_data = {
                "stream_id": stream_id,
                "step": step,
                "status": status,
                "message": message,
                "execution_time_ms": execution_time_ms
            }
            
            result = self.client.table("generation_logs").insert(log_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Loggen des Generierungsschritts: {e}")
            return False
    
    async def get_stream_logs(self, stream_id: str) -> List[Dict[str, Any]]:
        """Holt alle Logs eines Streams"""
        try:
            result = self.client.table("generation_logs").select("*").eq("stream_id", stream_id).order("created_at").execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Stream-Logs: {e}")
            return []

    # ==================== CONTENT CATEGORIES & SOURCES ====================
    
    async def get_active_categories(self) -> List[Dict[str, Any]]:
        """Holt alle aktiven Content-Kategorien"""
        try:
            result = self.client.table("content_categories").select("*").eq("is_active", True).order("priority_level").execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der aktiven Kategorien: {e}")
            return []
    
    async def get_content_sources_by_category(
        self, 
        category_slug: str, 
        source_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Holt Content Sources für eine Kategorie"""
        try:
            query = self.client.table("content_sources").select("""
                *,
                content_categories!inner(slug)
            """).eq("content_categories.slug", category_slug)
            
            if source_type:
                query = query.eq("source_type", source_type)
            
            if active_only:
                query = query.eq("is_active", True)
            
            result = query.order("priority_level").execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Content Sources: {e}")
            return []
    
    async def get_category_id_by_slug(self, slug: str) -> Optional[str]:
        """Holt Category ID anhand des Slugs"""
        try:
            result = self.client.table("content_categories").select("id").eq("slug", slug).single().execute()
            return result.data["id"] if result.data else None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Category ID für {slug}: {e}")
            return None
    
    async def create_news_content(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt neuen News Content"""
        try:
            result = self.client.table("news_content").insert(news_data).execute()
            logger.info(f"News Content erstellt: {news_data.get('content_type')}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des News Contents: {e}")
            raise
    
    async def get_news_content_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Prüft ob News Content mit externer ID bereits existiert"""
        try:
            result = self.client.table("news_content").select("*").contains("metadata", {"tweet_id": external_id}).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der externen ID: {e}")
            return None


# Singleton Instance
db = SupabaseClient() 