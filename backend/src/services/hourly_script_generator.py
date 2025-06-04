"""
RadioX Hourly Script Generator
Erstellt stündlich ein detailliertes Radio-Skript mit echten News, Wetter und Musik
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
import json

from .weather_service import WeatherService
from .rss_parser import RSSParser, RSSNewsItem
from .x_api_service import XAPIService, XTweet
from .supabase_service import SupabaseService
from ..models.radio_stations import RadioStationType, get_station


@dataclass
class NewsItem:
    """Einzelne News für Radio-Skript"""
    title: str
    summary: str
    source: str
    category: str
    priority: int  # 1-10
    timestamp: datetime
    radio_text: Optional[str] = None


@dataclass
class WeatherSegment:
    """Wetter-Segment für Radio-Skript"""
    city: str
    current_temp: float
    condition: str
    forecast: str
    radio_text: str


@dataclass
class MusicTrack:
    """Musik-Track für Radio-Skript"""
    title: str
    artist: str
    duration_seconds: int
    spotify_id: Optional[str] = None
    genre: Optional[str] = None


@dataclass
class RadioSegment:
    """Einzelnes Radio-Segment"""
    type: str  # "intro", "news", "weather", "music", "outro", "x_tweet"
    content: str
    duration_seconds: int
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class HourlyRadioScript:
    """Komplettes Stunden-Radio-Skript"""
    station_type: RadioStationType
    hour: datetime
    script_id: str
    segments: List[RadioSegment]
    total_duration: int
    metadata: Dict[str, Any]


class HourlyScriptGenerator:
    """Generiert stündliche Radio-Skripte mit echten Daten"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.rss_parser = RSSParser()
        self.x_service = XAPIService()
        self.supabase_service = SupabaseService()
        
        # Musik-Tracks für Breaking News (Electronic/Progressive House)
        self.breaking_news_tracks = [
            {"title": "Midnight City", "artist": "M83", "duration": 240},
            {"title": "Strobe", "artist": "Deadmau5", "duration": 320},
            {"title": "Breathe Me", "artist": "Sia", "duration": 280},
            {"title": "Teardrop", "artist": "Massive Attack", "duration": 330},
            {"title": "Born Slippy", "artist": "Underworld", "duration": 360},
            {"title": "One More Time", "artist": "Daft Punk", "duration": 320}
        ]
    
    async def generate_breaking_news_script(
        self, 
        target_hour: datetime,
        save_to_supabase: bool = True
    ) -> Dict[str, Any]:
        """Generiert Breaking News Skript für eine bestimmte Stunde - 100% ECHTE DATEN"""
        
        script_id = f"breaking_news_{target_hour.strftime('%Y%m%d_%H')}_{uuid.uuid4().hex[:6]}"
        
        logger.info(f"🚨 Generiere Breaking News Skript für {target_hour.strftime('%H:%M')}")
        
        segments = []
        current_time = target_hour
        
        # 1. Intro Segment
        intro_text = f"Willkommen bei Breaking News auf RadioX. Hier sind die wichtigsten Nachrichten um {target_hour.strftime('%H:%M')} Uhr."
        
        intro_segment = RadioSegment(
            type="intro",
            content=intro_text,
            duration_seconds=8,
            timestamp=current_time,
            metadata={
                "voice": "JARVIS",
                "station": "Breaking News",
                "intro_type": "hourly"
            }
        )
        segments.append(intro_segment)
        current_time += timedelta(seconds=8)
        
        # 2. Echte RSS News sammeln
        logger.info("📰 Sammle aktuelle RSS News...")
        try:
            # Breaking News Feed (hohe Priorität)
            breaking_news = await self.rss_parser.get_breaking_news_feed()
            
            # News in Supabase speichern
            if save_to_supabase and breaking_news:
                news_for_db = []
                for news in breaking_news:
                    news_for_db.append({
                        'title': news.title,
                        'summary': news.summary,
                        'source': news.source,
                        'category': news.category,
                        'priority': news.priority,
                        'timestamp': news.published,
                        'link': news.link,
                        'tags': news.tags
                    })
                
                await self.supabase_service.save_news_content(news_for_db)
            
            # Top 5 News für Radio-Skript
            for i, news in enumerate(breaking_news[:5]):
                news_text = f"News von {news.source}: {news.title}"
                
                news_segment = RadioSegment(
                    type="news",
                    content=news_text,
                    duration_seconds=15,
                    timestamp=current_time,
                    metadata={
                        "voice": "JARVIS",
                        "source": news.source,
                        "category": news.category,
                        "priority": news.priority,
                        "link": news.link,
                        "original_title": news.title
                    }
                )
                segments.append(news_segment)
                current_time += timedelta(seconds=15)
                
        except Exception as e:
            logger.error(f"💥 Fehler beim Sammeln der News: {e}")
        
        # 3. Bitcoin OG Tweets sammeln
        logger.info("🐦 Sammle Bitcoin OG Tweets...")
        try:
            bitcoin_tweets = await self.x_service.get_breaking_bitcoin_tweets()
            
            # Tweets in Supabase speichern
            if save_to_supabase and bitcoin_tweets:
                tweets_for_db = []
                for tweet in bitcoin_tweets:
                    tweets_for_db.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'author_username': tweet.author_username,
                        'author_name': tweet.author_name,
                        'created_at': tweet.created_at,
                        'like_count': tweet.like_count,
                        'retweet_count': tweet.retweet_count,
                        'url': tweet.url,
                        'category': tweet.category,
                        'priority': tweet.priority,
                        'tags': tweet.tags
                    })
                
                await self.supabase_service.save_tweet_content(tweets_for_db)
            
            # Top 3 Tweets für Radio-Skript
            for tweet in bitcoin_tweets[:3]:
                tweet_text = f"Bitcoin Update von @{tweet.author_username}: {tweet.text[:100]}..."
                
                tweet_segment = RadioSegment(
                    type="tweet",
                    content=tweet_text,
                    duration_seconds=20,
                    timestamp=current_time,
                    metadata={
                        "voice": "JARVIS",
                        "author": tweet.author_username,
                        "likes": tweet.like_count,
                        "retweets": tweet.retweet_count,
                        "url": tweet.url,
                        "priority": tweet.priority
                    }
                )
                segments.append(tweet_segment)
                current_time += timedelta(seconds=20)
                
        except Exception as e:
            logger.error(f"💥 Fehler beim Sammeln der Tweets: {e}")
        
        # 4. Wetter für Zürich
        logger.info("🌤️ Sammle Wetter-Daten...")
        current_weather = await self.weather_service.get_current_weather("zurich")
        
        if current_weather:
            weather_text = self.weather_service.format_weather_for_radio(
                current_weather, "Zürich"
            )
            weather_segment = RadioSegment(
                type="weather",
                content=weather_text,
                duration_seconds=20,
                timestamp=current_time,
                metadata={
                    "voice": "JARVIS",
                    "city": "Zürich",
                    "temperature": current_weather.temperature,
                    "condition": current_weather.weather_code,
                    "humidity": current_weather.humidity
                }
            )
            segments.append(weather_segment)
            current_time += timedelta(seconds=20)
        
        # 5. Musik-Tracks einfügen
        remaining_time = 3600 - sum(s.duration_seconds for s in segments) - 6  # 6s für Outro
        
        while remaining_time > 60:  # Mindestens 1 Minute für einen Track
            track = self.breaking_news_tracks[len([s for s in segments if s.type == "music"]) % len(self.breaking_news_tracks)]
            
            # Track-Dauer an verbleibende Zeit anpassen
            track_duration = min(track["duration"], remaining_time - 60)  # 60s Puffer
            
            music_text = f"Jetzt läuft: {track['title']} von {track['artist']}"
            
            music_segment = RadioSegment(
                type="music",
                content=music_text,
                duration_seconds=track_duration,
                timestamp=current_time,
                metadata={
                    "track_title": track["title"],
                    "artist": track["artist"],
                    "genre": "Electronic/Progressive House",
                    "spotify_track": True
                }
            )
            segments.append(music_segment)
            current_time += timedelta(seconds=track_duration)
            remaining_time -= track_duration
        
        # 6. Outro Segment
        outro_text = "Das waren die Breaking News dieser Stunde. Bleiben Sie dran für weitere Updates."
        
        outro_segment = RadioSegment(
            type="outro",
            content=outro_text,
            duration_seconds=6,
            timestamp=current_time,
            metadata={
                "voice": "JARVIS",
                "station": "Breaking News",
                "outro_type": "hourly"
            }
        )
        segments.append(outro_segment)
        
        # 7. Skript zusammenstellen
        total_duration = sum(s.duration_seconds for s in segments)
        
        script_data = {
            "script_id": script_id,
            "station_type": "breaking_news",
            "target_hour": target_hour.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "total_duration_seconds": total_duration,
            "segments": [
                {
                    "type": s.type,
                    "content": s.content,
                    "duration_seconds": s.duration_seconds,
                    "timestamp": s.timestamp.isoformat(),
                    "metadata": s.metadata
                }
                for s in segments
            ],
            "metadata": {
                "station_type": "breaking_news",
                "target_hour": target_hour.isoformat(),
                "voice_profile": "JARVIS",
                "weather_city": "Zürich",
                "news_sources": list(set([s.metadata.get("source") for s in segments if s.type == "news"])),
                "bitcoin_accounts": list(set([s.metadata.get("author") for s in segments if s.type == "tweet"])),
                "total_news": len([s for s in segments if s.type == "news"]),
                "total_tweets": len([s for s in segments if s.type == "tweet"]),
                "total_music_tracks": len([s for s in segments if s.type == "music"]),
                "generation_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # 8. In Supabase speichern
        if save_to_supabase:
            try:
                saved_id = await self.supabase_service.save_radio_script(script_data)
                if saved_id:
                    logger.info(f"✅ Skript {script_id} erfolgreich in Supabase gespeichert")
                    script_data["metadata"]["supabase_saved"] = True
                    script_data["metadata"]["supabase_id"] = saved_id
                else:
                    logger.warning(f"⚠️ Skript {script_id} konnte nicht in Supabase gespeichert werden")
                    script_data["metadata"]["supabase_saved"] = False
            except Exception as e:
                logger.error(f"💥 Fehler beim Speichern in Supabase: {e}")
                script_data["metadata"]["supabase_saved"] = False
        
        logger.info(f"✅ Breaking News Skript generiert: {len(segments)} Segmente, {total_duration}s")
        
        return script_data
    
    async def generate_script_for_station(
        self, 
        station_type: RadioStationType, 
        target_hour: datetime
    ) -> HourlyRadioScript:
        """Generiert Skript für beliebige Radio-Station"""
        
        if station_type == RadioStationType.BREAKING_NEWS:
            return await self.generate_breaking_news_script(target_hour)
        else:
            # Für andere Stationen später implementieren
            logger.warning(f"Skript-Generierung für {station_type} noch nicht implementiert")
            return await self.generate_breaking_news_script(target_hour)  # Fallback
    
    def save_script_to_file(self, script: HourlyRadioScript, output_dir: str = "output") -> str:
        """Speichert Skript als JSON-Datei"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Dateiname generieren
        filename = f"radio_script_{script.station_type.value}_{script.hour.strftime('%Y%m%d_%H')}_{script.script_id.split('_')[-1]}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Script zu JSON serialisieren
        script_data = {
            "station_type": script.station_type.value,
            "hour": script.hour.isoformat(),
            "script_id": script.script_id,
            "total_duration": script.total_duration,
            "metadata": script.metadata,
            "segments": [
                {
                    "type": segment.type,
                    "content": segment.content,
                    "duration_seconds": segment.duration_seconds,
                    "timestamp": segment.timestamp.isoformat(),
                    "metadata": segment.metadata
                }
                for segment in script.segments
            ]
        }
        
        # JSON speichern
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Skript gespeichert: {filepath}")
        
        return filepath


# Convenience Functions
async def generate_breaking_news_script(target_hour: datetime = None) -> HourlyRadioScript:
    """Generiert Breaking News Skript für die nächste Stunde"""
    if not target_hour:
        target_hour = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    generator = HourlyScriptGenerator()
    return await generator.generate_breaking_news_script(target_hour)

async def generate_script_for_station(
    station_type: RadioStationType, 
    target_hour: datetime = None
) -> HourlyRadioScript:
    """Generiert Skript für beliebige Station"""
    if not target_hour:
        target_hour = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    generator = HourlyScriptGenerator()
    return await generator.generate_script_for_station(station_type, target_hour) 