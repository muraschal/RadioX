#!/usr/bin/env python3
"""
Direkte ElevenLabs TTS-Integration ohne pydub
Kompatibel mit Python 3.13
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
from loguru import logger

class ElevenLabsDirect:
    """Direkte ElevenLabs API-Integration ohne externe Audio-Dependencies."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API-Key nicht gefunden")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """Listet alle verfügbaren Stimmen auf."""
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={
                    "Accept": "application/json",
                    "xi-api-key": self.api_key
                }
            )
            response.raise_for_status()
            
            voices_data = response.json()
            voices = voices_data.get("voices", [])
            
            logger.info(f"Gefunden: {len(voices)} verfügbare Stimmen")
            return voices
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Stimmen: {e}")
            return []
    
    def generate_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default: Rachel
        output_file: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.5,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> str:
        """Generiert Sprachausgabe und speichert sie als MP3-Datei."""
        
        try:
            # Erstelle Request-Body
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
            
            # API-Request
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            
            # Erstelle Output-Datei
            if not output_file:
                output_file = f"audio/tts_{hash(text) % 100000}.mp3"
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Speichere Audio-Daten
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Sprachausgabe generiert: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Fehler bei der Sprachgenerierung: {e}")
            raise
    
    def generate_radio_intro(
        self,
        persona: str = "energetic",
        voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    ) -> str:
        """Generiert ein energetisches Radio-Intro."""
        
        intros = {
            "energetic": "Willkommen bei RadioX! Der heißeste Sound der Stadt! Hier ist euer DJ mit den besten Beats!",
            "cyberpunk": "Verbindung hergestellt. RadioX online. Eure Datenübertragung für die besten Sounds der Zukunft.",
            "retro": "Hey Leute! Hier ist RadioX - euer Sender für die goldenen Hits und die besten Vibes!"
        }
        
        text = intros.get(persona, intros["energetic"])
        
        return self.generate_speech(
            text=text,
            voice_id=voice_id,
            output_file=f"audio/radio_intro_{persona}.mp3",
            stability=0.7,
            similarity_boost=0.8,
            style=0.3,
            use_speaker_boost=True
        )

def test_elevenlabs_direct():
    """Testet die direkte ElevenLabs-Integration."""
    print("🎙️ Teste direkte ElevenLabs-Integration...")
    
    try:
        # Initialisiere Client
        client = ElevenLabsDirect()
        
        # Test 1: Stimmen auflisten
        print("\n📋 Verfügbare Stimmen:")
        voices = client.list_voices()
        
        for voice in voices[:5]:  # Zeige nur die ersten 5
            print(f"  - {voice['name']} ({voice['voice_id']})")
        
        # Test 2: Einfache Sprachgenerierung
        print("\n🗣️ Generiere Test-Sprache...")
        test_text = "Hallo, das ist ein Test von RadioX!"
        audio_file = client.generate_speech(test_text)
        print(f"✅ Audio generiert: {audio_file}")
        
        # Test 3: Radio-Intro
        print("\n📻 Generiere Radio-Intro...")
        intro_file = client.generate_radio_intro("energetic")
        print(f"✅ Radio-Intro generiert: {intro_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    test_elevenlabs_direct() 