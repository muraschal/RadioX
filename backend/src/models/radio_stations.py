"""
RadioX Radio Stations System - Verschiedene Radio Sender mit eigenen Profilen
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class RadioStationType(str, Enum):
    """Radio Station Typen - Nur Züri Style für Entwicklung"""
    ZUERI_STYLE = "zueri_style"
    
    # DEAKTIVIERT FÜR ENTWICKLUNG:
    # BREAKING_NEWS = "breaking_news"
    # BITCOIN_OG = "bitcoin_og"
    # TRADFI_NEWS = "tradfi_news"
    # TECH_INSIDER = "tech_insider"
    # SWISS_LOCAL = "swiss_local"


class VoiceProfile(BaseModel):
    """Voice-Konfiguration für ElevenLabs"""
    voice_name: str
    voice_id: Optional[str] = None  # ElevenLabs Voice ID
    speed: float = 1.0  # 0.7 - 1.2
    stability: float = 0.5  # 0.0 - 1.0
    similarity_boost: float = 0.75  # 0.0 - 1.0
    style: float = 0.0  # 0.0 - 1.0
    use_speaker_boost: bool = True
    language: str = "en"


class ContentProfile(BaseModel):
    """Content-Mix Profil für Radio Station"""
    # Kategorien in Prozent (müssen zusammen 100% ergeben)
    bitcoin: int = 0
    wirtschaft: int = 0
    technologie: int = 0
    weltpolitik: int = 0
    sport: int = 0
    lokale_news_schweiz: int = 0
    wissenschaft: int = 0
    entertainment: int = 0
    
    def validate_total(self) -> bool:
        """Validiert dass Content-Mix 100% ergibt"""
        total = (self.bitcoin + self.wirtschaft + self.technologie + 
                self.weltpolitik + self.sport + self.lokale_news_schweiz + 
                self.wissenschaft + self.entertainment)
        return total == 100


class RadioStationConfig(BaseModel):
    """Vollständige Radio Station Konfiguration"""
    station_id: str
    display_name: str
    description: str
    tagline: str  # Kurzer Slogan für die Station
    target_audience: str
    voice_profile: VoiceProfile
    content_profile: ContentProfile
    
    # Tonalität & Stil
    tone: str  # "professional", "casual", "energetic", "cyberpunk", "local"
    energy_level: str  # "low", "medium", "high", "breaking"
    formality: str  # "formal", "semi-formal", "casual", "street"
    
    # Radio-spezifische Einstellungen
    intro_jingle: str  # Intro-Text/Jingle
    outro_jingle: str  # Outro-Text/Jingle
    news_format: str  # "bullet_points", "narrative", "analysis", "breaking"
    segment_style: str  # "smooth", "punchy", "analytical", "conversational"
    
    # Musik & Audio Präferenzen
    music_genres: List[str]
    audio_branding: str  # "minimal", "electronic", "classical", "urban"
    
    # Timing & Frequenz
    stream_duration_minutes: int = 60
    news_density: str = "medium"  # "low", "medium", "high", "breaking"
    update_frequency_minutes: int = 30  # Wie oft neue Streams generiert werden
    
    # Spezielle Features
    weather_updates: bool = True
    traffic_updates: bool = False
    bitcoin_price_updates: bool = False
    breaking_news_priority: bool = False
    
    # Meta
    is_default: bool = False


# Radio Station Konfigurationen
RADIO_STATIONS = {
    # 1. ZÜRI STYLE - Hauptstation für Entwicklung
    "zueri_style": RadioStationConfig(
        station_id="zueri_style",
        display_name="Züri Style",
        description="Zürich hört Zürich - Lokale News mit Schweizer Charme",
        tagline="Zürich hört Zürich",
        target_audience="Zürich Locals, 25-45 Jahre",
        
        # Voice Profile - Deine eigene deutsche Stimme
        voice_profile=VoiceProfile(
            voice_name="Deine Stimme (Deutsch)",  # Deine eigene Voice
            voice_id="owi9KfbgBi6A987h5eJH",  # Deine deutsche Voice ID
            speed=0.95,
            stability=0.6,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True,
            language="de"
        ),
        
        # Content Profile - Fokus auf Zürich und Schweiz
        content_profile=ContentProfile(
            lokale_news_schweiz=50,  # Mehr Zürich-News
            wirtschaft=30,
            bitcoin=20,
            technologie=0,
            weltpolitik=0,
            sport=0,
            wissenschaft=0,
            entertainment=0
        ),
        
        # Tonalität & Stil
        tone="casual",
        energy_level="medium",
        formality="informal",
        
        # Radio-spezifische Einstellungen
        intro_jingle="Grüezi Zürich! Hier sind eure lokalen News...",
        outro_jingle="Das wars für heute - bis zum nächsten Mal, Zürich!",
        news_format="conversational",
        segment_style="local_focus",
        
        # Musik & Audio
        music_genres=["swiss_pop", "indie", "electronic"],
        audio_branding="urban_swiss",
        
        # Features
        weather_updates=True,
        traffic_updates=True,
        bitcoin_price_updates=True,
        breaking_news_priority=False,
        
        # Meta
        is_default=True,  # Züri Style als Default für Entwicklung
        update_frequency_minutes=30
    ),
    
    # ALLE ANDEREN STATIONEN DEAKTIVIERT FÜR ENTWICKLUNG
    # Können später wieder aktiviert werden
    
    # "breaking_news": RadioStationConfig(
    #     # ... deaktiviert
    # ),
    
    # "bitcoin_og": RadioStationConfig(
    #     # ... deaktiviert  
    # ),
    
    # "tradfi_news": RadioStationConfig(
    #     # ... deaktiviert
    # ),
    
    # "tech_insider": RadioStationConfig(
    #     # ... deaktiviert
    # ),
    
    # "swiss_local": RadioStationConfig(
    #     # ... deaktiviert
    # )
}


def get_station(station_type: RadioStationType) -> RadioStationConfig:
    """Holt Radio Station Konfiguration nach Typ"""
    station_id = station_type.value
    if station_id in RADIO_STATIONS:
        return RADIO_STATIONS[station_id]
    else:
        raise ValueError(f"Radio Station '{station_id}' nicht gefunden")


def get_default_station() -> RadioStationConfig:
    """Gibt die Standard-Radio Station zurück (Züri Style)"""
    return RADIO_STATIONS["zueri_style"]


def list_stations() -> List[RadioStationConfig]:
    """Gibt alle verfügbaren Radio Stations zurück"""
    return list(RADIO_STATIONS.values())


def get_station_by_id(station_id: str) -> Optional[RadioStationConfig]:
    """Holt Radio Station nach ID"""
    return RADIO_STATIONS.get(station_id)


def validate_content_profile(content_profile: ContentProfile) -> bool:
    """Validiert ein Content-Profil"""
    return content_profile.validate_total()


def get_voice_prompt_for_station(station: RadioStationConfig) -> str:
    """Generiert Voice-Prompt für ElevenLabs basierend auf Station"""
    
    prompts = {
        "professional": f"Sprechen Sie als professioneller Nachrichtensprecher für {station.display_name}. Klar, autoritativ und vertrauenswürdig.",
        "casual": f"Sprechen Sie freundlich und entspannt für {station.display_name}. Natürlich und zugänglich.",
        "energetic": f"Sprechen Sie mit Energie und Begeisterung für {station.display_name}. Dynamisch und mitreißend.",
        "cyberpunk": f"Sprechen Sie im futuristischen Cyberpunk-Stil für {station.display_name}. Cool und technisch."
    }
    
    base_prompt = prompts.get(station.tone, prompts["professional"])
    
    # Formality hinzufügen
    if station.formality == "formal":
        base_prompt += " Verwenden Sie formelle Sprache."
    elif station.formality == "casual":
        base_prompt += " Verwenden Sie lockere, umgangssprachliche Ausdrücke."
    
    # Energy Level hinzufügen
    if station.energy_level == "high":
        base_prompt += " Sprechen Sie mit hoher Energie und Dringlichkeit."
    elif station.energy_level == "breaking":
        base_prompt += " Dies sind Eilmeldungen - sprechen Sie mit angemessener Dringlichkeit."
    
    return base_prompt


def get_station_summary() -> Dict[str, any]:
    """Erstellt eine Übersicht aller Radio Stations"""
    
    summary = {
        "total_stations": len(RADIO_STATIONS),
        "default_station": get_default_station().display_name,
        "stations": []
    }
    
    for station_type, station in RADIO_STATIONS.items():
        # Top Content-Kategorie finden
        content_dict = station.content_profile.dict()
        top_category = max(content_dict.items(), key=lambda x: x[1])
        
        station_info = {
            "id": station.station_id,
            "name": station.display_name,
            "tagline": station.tagline,
            "target_audience": station.target_audience.split(',')[0].strip(),
            "top_content": f"{top_category[0]} ({top_category[1]}%)",
            "tone": station.tone,
            "energy": station.energy_level,
            "voice_name": station.voice_profile.voice_name,
            "special_features": []
        }
        
        # Spezielle Features sammeln
        if station.weather_updates:
            station_info["special_features"].append("Wetter")
        if station.traffic_updates:
            station_info["special_features"].append("Verkehr")
        if station.bitcoin_price_updates:
            station_info["special_features"].append("Bitcoin Preis")
        if station.breaking_news_priority:
            station_info["special_features"].append("Eilmeldungen")
        
        summary["stations"].append(station_info)
    
    return summary 