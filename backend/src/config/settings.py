"""
RadioX Settings - Konfiguration für alle Services
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """RadioX Konfiguration"""
    
    # Supabase
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None  
    supabase_service_role_key: Optional[str] = None
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # ElevenLabs
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_marcel_voice_id: Optional[str] = None
    elevenlabs_jarvis_voice_id: Optional[str] = None
    
    # CoinMarketCap
    coinmarketcap_api_key: Optional[str] = None
    
    # Weather API
    weather_api_key: Optional[str] = None
    
    # Twitter/X (alte und neue Feldnamen)
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    
    # X API (neue Feldnamen)
    x_client_id: Optional[str] = None
    x_client_secret: Optional[str] = None
    x_bearer_token: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None
    
    # SRF Weather
    srf_weather_api_key: Optional[str] = None
    
    # Spotify
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    spotify_redirect_uri: Optional[str] = None
    
    # System
    log_level: str = "INFO"
    debug: bool = False
    
    class Config:
        # .env-Datei aus dem RadioX Root-Verzeichnis laden
        # Von backend/src/config/settings.py aus sind das 3 Ebenen nach oben
        env_file = Path(__file__).parent.parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignoriere unbekannte Felder


# Global Settings Instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Holt die globale Settings-Instanz"""
    global _settings
    if _settings is None:
        _settings = Settings()
        # Debug: Zeige geladene API Keys (ohne Werte zu loggen)
        print(f"🔑 Settings geladen:")
        print(f"   OpenAI API Key: {'✅ Vorhanden' if _settings.openai_api_key else '❌ Fehlt'}")
        print(f"   ElevenLabs API Key: {'✅ Vorhanden' if _settings.elevenlabs_api_key else '❌ Fehlt'}")
        print(f"   CoinMarketCap API Key: {'✅ Vorhanden' if _settings.coinmarketcap_api_key else '❌ Fehlt'}")
        print(f"   Weather API Key: {'✅ Vorhanden' if _settings.weather_api_key else '❌ Fehlt'}")
        print(f"   Supabase URL: {'✅ Vorhanden' if _settings.supabase_url else '❌ Fehlt'}")
        print(f"   Twitter Bearer: {'✅ Vorhanden' if _settings.x_bearer_token else '❌ Fehlt'}")
    return _settings 