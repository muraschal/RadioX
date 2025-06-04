"""
RadioX Backend Configuration
Zentrale Konfiguration für alle Services und APIs
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, List
import os


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
    
    # Personas Configuration
    personas: Dict = {
        "maximalist": {
            "name": "Bitcoin Maximalist",
            "voice_style": "Frech, direkt, Bitcoin-maximalistisch",
            "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "intro_style": "Willkommen bei RadioX, dem einzig wahren Bitcoin-Radio!",
            "news_style": "Breaking aus dem Bitcoin-Space:",
            "outro_style": "Das war euer Update aus der Bitcoin-Matrix."
        },
        "cyberpunk": {
            "name": "Cyberpunk Matrix",
            "voice_style": "Dystopisch, tech-fokussiert, Matrix-Style",
            "elevenlabs_voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella
            "intro_style": "Verbindung zur Matrix hergestellt. RadioX lädt...",
            "news_style": "Datenstream empfangen:",
            "outro_style": "Transmission beendet. Weiter geht's mit Musik..."
        },
        "retro": {
            "name": "80s Retro Wave",
            "voice_style": "80s Nostalgie mit Bitcoin-Twist",
            "elevenlabs_voice_id": "ErXwobaYiN019PkySvjV",  # Antoni
            "intro_style": "Zurück in die Zukunft mit RadioX - Bitcoin meets 80s!",
            "news_style": "Newsflash aus der Zukunft:",
            "outro_style": "Totally radical! Weiter mit den Beats..."
        },
        "professional": {
            "name": "Professional News",
            "voice_style": "Seriös, professionell, nachrichtentauglich",
            "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam
            "intro_style": "Guten Tag, hier ist RadioX mit den aktuellen Nachrichten.",
            "news_style": "Aktuelle Meldung:",
            "outro_style": "Das waren die Nachrichten. Jetzt Musik."
        }
    }
    
    # Default Category Mix für verschiedene Stream-Typen
    stream_templates: Dict = {
        "bitcoin_focus": {
            "name": "Bitcoin Focus",
            "description": "Bitcoin-lastiger Stream mit Tech-News",
            "category_mix": {
                "bitcoin": 50,
                "tech": 25,
                "wirtschaft": 20,
                "lokal": 5
            }
        },
        "balanced_news": {
            "name": "Balanced News",
            "description": "Ausgewogener Mix aller Kategorien",
            "category_mix": {
                "bitcoin": 20,
                "wirtschaft": 25,
                "tech": 20,
                "politik": 15,
                "lokal": 10,
                "sport": 10
            }
        },
        "business_focus": {
            "name": "Business Focus",
            "description": "Wirtschafts- und Finanz-fokussiert",
            "category_mix": {
                "wirtschaft": 40,
                "bitcoin": 30,
                "tech": 20,
                "politik": 10
            }
        },
        "swiss_local": {
            "name": "Swiss Local Mix",
            "description": "Schweiz-fokussiert mit lokalen News",
            "category_mix": {
                "lokal": 40,
                "wirtschaft": 25,
                "bitcoin": 20,
                "tech": 15
            }
        },
        "entertainment": {
            "name": "Entertainment Mix",
            "description": "Leichter Mix mit Entertainment",
            "category_mix": {
                "entertainment": 30,
                "sport": 25,
                "tech": 20,
                "bitcoin": 15,
                "lokal": 10
            }
        }
    }
    
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
        env_file = ".env"
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


def get_category_mix(template_name: str) -> Dict[str, int]:
    """Gibt die Kategorie-Mischung für ein Template zurück"""
    return settings.stream_templates.get(template_name, {}).get("category_mix", {})


def get_persona_config(persona_name: str) -> Dict:
    """Gibt die Konfiguration für eine Persona zurück"""
    return settings.personas.get(persona_name, settings.personas["cyberpunk"])


# Initialisierung beim Import
ensure_directories() 