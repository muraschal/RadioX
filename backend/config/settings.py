"""
RadioX Backend Configuration
Zentrale Konfiguration für alle Services und APIs
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, List
import os
from pathlib import Path

# Root-Verzeichnis ermitteln (ein Verzeichnis über backend/)
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """RadioX Konfiguration mit Environment Variables"""
    
    # Supabase Database
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # ElevenLabs TTS (optional für ersten Test)
    elevenlabs_api_key: Optional[str] = Field(None, env="ELEVENLABS_API_KEY")
    
    # OpenAI GPT (optional für ersten Test)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Weather API
    weather_api_key: Optional[str] = Field(None, env="WEATHER_API_KEY")
    
    # CoinMarketCap API
    coinmarketcap_api_key: Optional[str] = Field(None, env="COINMARKETCAP_API_KEY")
    
    # Spotify API (optional für ersten Test)
    spotify_client_id: Optional[str] = Field(None, env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: Optional[str] = Field(None, env="SPOTIFY_CLIENT_SECRET")
    
    # X (Twitter) API (optional für ersten Test)
    x_api_key: Optional[str] = Field(None, env="X_API_KEY")
    x_api_secret: Optional[str] = Field(None, env="X_API_SECRET")
    x_access_token: Optional[str] = Field(None, env="X_ACCESS_TOKEN")
    x_access_token_secret: Optional[str] = Field(None, env="X_ACCESS_TOKEN_SECRET")
    x_bearer_token: Optional[str] = Field(None, env="X_BEARER_TOKEN")
    
    # YouTube API (optional für ersten Test)
    youtube_api_key: Optional[str] = Field(None, env="YOUTUBE_API_KEY")
    
    # RSS Feeds
    rss_weather_url: Optional[str] = Field(None, env="RSS_WEATHER_URL")
    rss_news_url: Optional[str] = Field(None, env="RSS_NEWS_URL")
    
    # Stream Configuration
    stream_duration_minutes: int = Field(60, env="STREAM_DURATION_MINUTES")
    audio_quality: int = Field(320, env="AUDIO_QUALITY")
    output_format: str = Field("mp3", env="OUTPUT_FORMAT")
    
    # Vercel Upload (später)
    vercel_token: Optional[str] = Field(None, env="VERCEL_TOKEN")
    vercel_project_id: Optional[str] = Field(None, env="VERCEL_PROJECT_ID")
    
    # Local Paths
    audio_output_dir: str = Field("./output/audio", env="AUDIO_OUTPUT_DIR")
    temp_dir: str = Field("./temp", env="TEMP_DIR")
    
    # Content Monitoring
    content_check_interval_minutes: int = Field(5, env="CONTENT_CHECK_INTERVAL_MINUTES")
    max_content_per_hour: int = Field(20, env="MAX_CONTENT_PER_HOUR")
    relevance_threshold: float = Field(0.6, env="RELEVANCE_THRESHOLD")
    
    # Content Processing Rules
    content_processing: Dict = {
        "max_tweet_length": 280,
        "max_rss_length": 500,
        "summary_target_length": 150,
        "sentiment_analysis_enabled": True,
        "auto_translation_enabled": False,
        "profanity_filter_enabled": True
    }
    
    class Config:
        env_file = str(ENV_FILE_PATH)  # Verwende Root .env Datei
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignoriert unbekannte Felder in .env


# Singleton Instance
settings = Settings()


def get_settings() -> Settings:
    """Gibt die globale Settings-Instanz zurück"""
    return settings


def ensure_directories():
    """Erstellt notwendige Verzeichnisse falls sie nicht existieren"""
    os.makedirs(settings.audio_output_dir, exist_ok=True)
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(f"{settings.temp_dir}/spotify", exist_ok=True)
    os.makedirs(f"{settings.temp_dir}/tts", exist_ok=True)
    os.makedirs(f"{settings.temp_dir}/mixed", exist_ok=True)
    
    # Kategoriebasierte Temp-Ordner
    for category in ["bitcoin", "wirtschaft", "tech", "politik", "sport", "lokal", "wissenschaft", "entertainment"]:
        os.makedirs(f"{settings.temp_dir}/content/{category}", exist_ok=True)


# Initialisierung beim Import
ensure_directories() 