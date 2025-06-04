"""
RadioX Persona System - Hörer-Zielgruppen für verschiedene Content-Styles
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class PersonaType(str, Enum):
    """Verfügbare Persona-Typen für RadioX"""
    ZUERI_STYLE = "zueri_style"
    BITCOIN_OG = "bitcoin_og"
    TRADFI_NEWS = "tradfi_news"
    BREAKING_NEWS = "breaking_news"
    TECH_INSIDER = "tech_insider"
    SWISS_LOCAL = "swiss_local"


class VoiceStyle(BaseModel):
    """Voice-Over Stil-Konfiguration"""
    voice_name: str
    voice_id: Optional[str] = None
    speed: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    language: str = "de"


class ContentMix(BaseModel):
    """Content-Mix Prozentsätze pro Kategorie"""
    bitcoin: int = 0
    wirtschaft: int = 0
    technologie: int = 0
    weltpolitik: int = 0
    sport: int = 0
    lokale_news_schweiz: int = 0
    wissenschaft: int = 0
    entertainment: int = 0


class PersonaConfig(BaseModel):
    """Vollständige Persona-Konfiguration"""
    name: str
    display_name: str
    description: str
    target_audience: str
    voice_style: VoiceStyle
    content_mix: ContentMix
    tone: str  # "professional", "casual", "energetic", "cyberpunk"
    intro_style: str
    outro_style: str
    news_format: str  # "bullet_points", "narrative", "analysis"
    music_genre_preference: List[str]
    segment_length_minutes: int = 60
    news_density: str = "medium"  # "low", "medium", "high"


# Persona-Definitionen
PERSONAS: Dict[PersonaType, PersonaConfig] = {
    
    PersonaType.ZUERI_STYLE: PersonaConfig(
        name="zueri_style",
        display_name="Züri Style",
        description="Lokaler Zürich-Fokus mit Schweizer Dialekt-Touch",
        target_audience="Zürich Locals, Schweizer Expats, Urban Professionals",
        voice_style=VoiceStyle(
            voice_name="Flavia",
            speed=0.95,
            stability=0.6,
            similarity_boost=0.8,
            style=0.2
        ),
        content_mix=ContentMix(
            lokale_news_schweiz=40,
            wirtschaft=25,
            bitcoin=15,
            sport=10,
            entertainment=5,
            technologie=5
        ),
        tone="casual",
        intro_style="Grüezi Zürich! Hier sind eure lokalen News...",
        outro_style="Das wars für heute - bis zum nächsten Mal, Zürich!",
        news_format="narrative",
        music_genre_preference=["swiss_pop", "indie", "electronic"],
        news_density="medium"
    ),
    
    PersonaType.BITCOIN_OG: PersonaConfig(
        name="bitcoin_og",
        display_name="Bitcoin OG",
        description="Hardcore Bitcoin Maximalist Content",
        target_audience="Bitcoin OGs, Crypto Veterans, HODLers",
        voice_style=VoiceStyle(
            voice_name="Flavia",
            speed=1.05,
            stability=0.7,
            similarity_boost=0.9,
            style=0.3
        ),
        content_mix=ContentMix(
            bitcoin=60,
            wirtschaft=20,
            technologie=15,
            lokale_news_schweiz=5
        ),
        tone="energetic",
        intro_style="Stack sats, stay humble! Hier sind die Bitcoin News...",
        outro_style="Remember: Bitcoin fixes this. Until next time, HODLers!",
        news_format="analysis",
        music_genre_preference=["cyberpunk", "electronic", "synthwave"],
        news_density="high"
    ),
    
    PersonaType.TRADFI_NEWS: PersonaConfig(
        name="tradfi_news",
        display_name="TradFi News",
        description="Traditionelle Finanz- und Wirtschaftsnachrichten",
        target_audience="Banker, Finanzprofis, Investoren, Business Leaders",
        voice_style=VoiceStyle(
            voice_name="Flavia",
            speed=0.9,
            stability=0.8,
            similarity_boost=0.85,
            style=0.1
        ),
        content_mix=ContentMix(
            wirtschaft=45,
            weltpolitik=25,
            bitcoin=15,
            lokale_news_schweiz=10,
            technologie=5
        ),
        tone="professional",
        intro_style="Guten Tag, hier sind die Wirtschaftsnachrichten...",
        outro_style="Das waren die wichtigsten Marktentwicklungen. Auf Wiederhören.",
        news_format="bullet_points",
        music_genre_preference=["classical", "ambient", "jazz"],
        news_density="high"
    ),
    
    PersonaType.BREAKING_NEWS: PersonaConfig(
        name="breaking_news",
        display_name="Breaking News",
        description="Eilmeldungen und aktuelle Ereignisse - Default RadioX Persona",
        target_audience="News Junkies, Politiker, Journalisten, Allgemeine Hörer",
        voice_style=VoiceStyle(
            voice_name="Breaking News Voice",
            voice_id="QTGiyJvep6bcx4WD1qAq",  # Neue ElevenLabs Voice ID
            speed=1.1,
            stability=0.6,
            similarity_boost=0.8,
            style=0.4
        ),
        content_mix=ContentMix(
            weltpolitik=35,
            lokale_news_schweiz=25,
            wirtschaft=20,
            bitcoin=10,
            sport=5,
            technologie=5
        ),
        tone="energetic",
        intro_style="Breaking: Hier sind die neuesten Entwicklungen...",
        outro_style="Wir halten Sie auf dem Laufenden. Bis zur nächsten Meldung!",
        news_format="narrative",
        music_genre_preference=["electronic", "drum_and_bass", "minimal"],
        news_density="high"
    ),
    
    PersonaType.TECH_INSIDER: PersonaConfig(
        name="tech_insider",
        display_name="Tech Insider",
        description="Technologie-News für Entwickler und Tech-Enthusiasten",
        target_audience="Entwickler, Tech Workers, Startup Founders, AI Researchers",
        voice_style=VoiceStyle(
            voice_name="Flavia",
            speed=1.0,
            stability=0.5,
            similarity_boost=0.75,
            style=0.3
        ),
        content_mix=ContentMix(
            technologie=40,
            bitcoin=25,
            wirtschaft=15,
            wissenschaft=10,
            lokale_news_schweiz=5,
            entertainment=5
        ),
        tone="casual",
        intro_style="Hey Tech Community! Hier sind die neuesten Updates...",
        outro_style="Keep coding, keep innovating. Catch you next time!",
        news_format="analysis",
        music_genre_preference=["electronic", "synthwave", "lo-fi"],
        news_density="medium"
    ),
    
    PersonaType.SWISS_LOCAL: PersonaConfig(
        name="swiss_local",
        display_name="Swiss Local",
        description="Schweiz-weite Nachrichten mit lokalem Fokus",
        target_audience="Schweizer Bürger, Expats, Touristen",
        voice_style=VoiceStyle(
            voice_name="Flavia",
            speed=0.95,
            stability=0.7,
            similarity_boost=0.8,
            style=0.2
        ),
        content_mix=ContentMix(
            lokale_news_schweiz=50,
            sport=20,
            wirtschaft=15,
            entertainment=10,
            bitcoin=5
        ),
        tone="casual",
        intro_style="Hallo Schweiz! Hier sind eure lokalen Nachrichten...",
        outro_style="Das wars aus der Schweiz. Bis bald!",
        news_format="narrative",
        music_genre_preference=["swiss_folk", "pop", "indie"],
        news_density="medium"
    )
}


def get_default_persona() -> PersonaConfig:
    """Gibt die Standard-Persona zurück (Breaking News)"""
    return PERSONAS[PersonaType.BREAKING_NEWS]


def get_persona(persona_type: PersonaType) -> PersonaConfig:
    """Holt eine spezifische Persona-Konfiguration"""
    return PERSONAS[persona_type]


def list_personas() -> List[PersonaConfig]:
    """Listet alle verfügbaren Personas auf"""
    return list(PERSONAS.values())


def get_persona_by_name(name: str) -> Optional[PersonaConfig]:
    """Holt eine Persona anhand des Namens"""
    for persona in PERSONAS.values():
        if persona.name == name:
            return persona
    return None


def validate_content_mix(content_mix: ContentMix) -> bool:
    """Validiert, dass Content-Mix zu 100% addiert"""
    total = (
        content_mix.bitcoin + content_mix.wirtschaft + content_mix.technologie +
        content_mix.weltpolitik + content_mix.sport + content_mix.lokale_news_schweiz +
        content_mix.wissenschaft + content_mix.entertainment
    )
    return total == 100


def get_voice_prompt_for_persona(persona: PersonaConfig, content_type: str = "news") -> str:
    """Generiert Voice-Over Prompts basierend auf Persona"""
    
    base_prompts = {
        "zueri_style": "Sprich wie ein freundlicher Zürich Radio-Moderator. Verwende gelegentlich Schweizer Ausdrücke.",
        "bitcoin_og": "Sprich energisch und überzeugend wie ein Bitcoin-Evangelist. Verwende Bitcoin-Slang.",
        "tradfi_news": "Sprich professionell und sachlich wie ein Wirtschaftsnachrichtensprecher.",
        "breaking_news": "Sprich dringend und aufmerksam wie bei Eilmeldungen.",
        "tech_insider": "Sprich locker und kompetent wie ein Tech-Podcaster.",
        "swiss_local": "Sprich warm und einladend wie ein lokaler Radio-Moderator."
    }
    
    return base_prompts.get(persona.name, "Sprich klar und professionell.") 