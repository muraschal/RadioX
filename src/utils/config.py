from typing import Dict, List
from pydantic import BaseModel

class VoiceConfig(BaseModel):
    voice_id: str
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

class PersonaConfig(BaseModel):
    name: str
    description: str
    voice: VoiceConfig
    vocabulary: List[str]
    tone: str
    fallback_mode: str = "neutral"

class RadioConfig(BaseModel):
    segment_length: int = 300  # 5 Minuten
    crossfade_duration: int = 2000  # 2 Sekunden
    music_ratio: float = 0.7
    news_interval: int = 1800  # 30 Minuten
    ads_per_hour: int = 3

# Vordefinierte Personas
DEFAULT_PERSONAS: Dict[str, PersonaConfig] = {
    "maximalist": PersonaConfig(
        name="Maximalist",
        description="Bitcoin-Maximalist mit zynischem Humor",
        voice=VoiceConfig(
            voice_id="dmLlPcdDHenQXbfM5tee",
            stability=0.7,
            style=0.3
        ),
        vocabulary=[
            "Fiat-Idioten",
            "Channel-Rebalancing",
            "HODL",
            "To the Moon"
        ],
        tone="zynisch, direkt, überzeugt"
    ),
    "cyberpunk": PersonaConfig(
        name="Cyberpunk",
        description="Futuristischer Tech-Enthusiast",
        voice=VoiceConfig(
            voice_id="dmLlPcdDHenQXbfM5tee",
            stability=0.6,
            style=0.4
        ),
        vocabulary=[
            "Neural-Link",
            "Quantum-Computing",
            "Augmented Reality",
            "Cyber-Space"
        ],
        tone="mysteriös, technisch, visionär"
    ),
    "retro": PersonaConfig(
        name="Retro",
        description="Nostalgischer 80er-Jahre DJ",
        voice=VoiceConfig(
            voice_id="dmLlPcdDHenQXbfM5tee",
            stability=0.8,
            style=0.2
        ),
        vocabulary=[
            "Totally Rad",
            "Awesome",
            "Groovy",
            "Far Out"
        ],
        tone="energetisch, enthusiastisch, retro"
    )
}

# Standard-Konfiguration
DEFAULT_CONFIG = RadioConfig() 