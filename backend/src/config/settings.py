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
    weather_api_key: Optional[str] = None  # OpenWeatherMap API Key
    
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
        
        # Hilfsfunktion für Template-Wert-Erkennung
        def is_valid_key(value: Optional[str]) -> bool:
            """Prüft ob ein API Key gültig ist (nicht None, nicht leer, nicht Template)"""
            if not value:
                return False
            if value.startswith("your_") or value.endswith("_here"):
                return False
            return True
        
        # Debug: Zeige geladene API Keys mit ASCII-Zeichen für Windows-Kompatibilität
        print("Settings geladen:")
        print(f"   OpenAI API Key: {'[OK]' if is_valid_key(_settings.openai_api_key) else '[FEHLT]'}")
        print(f"   ElevenLabs API Key: {'[OK]' if is_valid_key(_settings.elevenlabs_api_key) else '[FEHLT]'}")
        print(f"   CoinMarketCap API Key: {'[OK]' if is_valid_key(_settings.coinmarketcap_api_key) else '[FEHLT]'}")
        print(f"   Weather API Key: {'[OK]' if is_valid_key(_settings.weather_api_key) else '[FEHLT]'}")
        print(f"   Supabase URL: {'[OK]' if is_valid_key(_settings.supabase_url) else '[FEHLT]'}")
        print(f"   Twitter Bearer: {'[OK]' if is_valid_key(_settings.twitter_bearer_token) else '[FEHLT]'}")
    return _settings 