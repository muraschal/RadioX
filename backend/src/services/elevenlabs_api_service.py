"""
RadioX ElevenLabs API Service
Direkte Integration mit der ElevenLabs API ohne MCP Dependencies
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from pathlib import Path
import json

from dotenv import load_dotenv

# Load environment variables from root directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


class ElevenLabsAPIService:
    """Direkter ElevenLabs API Service ohne MCP Dependencies"""
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.error("❌ ElevenLabs API Key nicht gefunden!")
            logger.info("💡 Prüfe ELEVENLABS_API_KEY in der .env Datei")
            raise ValueError("❌ ElevenLabs API Key fehlt!")
        
        logger.info("✅ ElevenLabs API Service initialisiert")
        
        # RadioX Voice Mapping
        self.voices = {
            "breaking_news": {
                "voice_id": "dmLlPcdDHenQXbfM5tee",  # JARVIS
                "voice_name": "JARVIS",
                "stability": 0.5,
                "similarity_boost": 0.8,
                "speed": 1.0
            },
            "bitcoin_og": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
                "voice_name": "Rachel",
                "stability": 0.4,
                "similarity_boost": 0.8,
                "speed": 1.1
            },
            "zueri_style": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella/Sarah
                "voice_name": "Bella",
                "stability": 0.6,
                "similarity_boost": 0.75,
                "speed": 0.95
            },
            "tradfi_news": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam
                "voice_name": "Adam",
                "stability": 0.7,
                "similarity_boost": 0.8,
                "speed": 0.9
            }
        }
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: str,
        output_file: str,
        stability: float = 0.5,
        similarity_boost: float = 0.8,
        speed: float = 1.0,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> bool:
        """
        Konvertiert Text zu Sprache mit ElevenLabs API
        
        Args:
            text: Text zum Konvertieren
            voice_id: ElevenLabs Voice ID
            output_file: Pfad zur Output-Datei
            stability: Voice Stability (0.0-1.0)
            similarity_boost: Similarity Boost (0.0-1.0)
            speed: Sprechgeschwindigkeit (0.5-2.0)
            style: Voice Style (0.0-1.0)
            use_speaker_boost: Speaker Boost aktivieren
            
        Returns:
            bool: True wenn erfolgreich, False bei Fehler
        """
        
        try:
            logger.info(f"🎙️ Generiere Audio: {text[:50]}...")
            logger.info(f"🗣️ Voice ID: {voice_id}")
            
            # API Endpoint
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            # Request Headers
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            # Request Body
            data = {
                "text": text,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
            
            # Wenn Speed unterstützt wird (neuere API Versionen)
            if speed != 1.0:
                data["voice_settings"]["speed"] = speed
            
            # HTTP Request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    
                    if response.status == 200:
                        # Audio-Daten speichern
                        audio_data = await response.read()
                        
                        # Output-Verzeichnis erstellen
                        output_path = Path(output_file)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Audio-Datei schreiben
                        with open(output_path, 'wb') as f:
                            f.write(audio_data)
                        
                        file_size = len(audio_data) / 1024  # KB
                        logger.info(f"✅ Audio gespeichert: {output_file} ({file_size:.1f} KB)")
                        
                        return True
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ ElevenLabs API Fehler {response.status}: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"💥 TTS Generation Fehler: {e}")
            return False
    
    async def generate_radio_segment(
        self,
        text: str,
        station_type: str,
        segment_type: str,
        output_dir: str
    ) -> Optional[str]:
        """
        Generiert Audio für ein Radio-Segment
        
        Args:
            text: Text für das Segment
            station_type: Station (breaking_news, bitcoin_og, etc.)
            segment_type: Segment-Typ (intro, news, weather, etc.)
            output_dir: Output-Verzeichnis
            
        Returns:
            str: Pfad zur generierten Audio-Datei oder None bei Fehler
        """
        
        try:
            # Voice-Konfiguration für Station
            voice_config = self.voices.get(station_type, self.voices['breaking_news'])
            
            # Segment-spezifische Anpassungen
            stability = voice_config['stability']
            similarity_boost = voice_config['similarity_boost']
            speed = voice_config['speed']
            
            if segment_type == 'intro':
                stability = min(stability + 0.1, 1.0)  # Stabiler
                speed = speed * 0.95  # Langsamer
            elif segment_type == 'news':
                stability = min(stability + 0.2, 1.0)  # Sehr stabil
            elif segment_type == 'weather':
                speed = speed * 0.9  # Entspannter
            elif segment_type == 'outro':
                speed = speed * 0.9  # Langsamer ausklingen
            
            # Output-Datei
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"{segment_type}_{voice_config['voice_name'].lower()}_{timestamp}.mp3"
            output_file = Path(output_dir) / filename
            
            # Audio generieren
            success = await self.text_to_speech(
                text=text,
                voice_id=voice_config['voice_id'],
                output_file=str(output_file),
                stability=stability,
                similarity_boost=similarity_boost,
                speed=speed,
                style=0.0,
                use_speaker_boost=True
            )
            
            if success:
                return str(output_file)
            else:
                return None
                
        except Exception as e:
            logger.error(f"💥 Radio Segment Generation Fehler: {e}")
            return None
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """
        Holt verfügbare Voices von ElevenLabs API
        
        Returns:
            Dict mit verfügbaren Voices
        """
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    
                    if response.status == 200:
                        voices_data = await response.json()
                        logger.info(f"✅ {len(voices_data.get('voices', []))} Voices verfügbar")
                        return voices_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Voices API Fehler {response.status}: {error_text}")
                        return {}
        
        except Exception as e:
            logger.error(f"💥 Voices API Fehler: {e}")
            return {}
    
    async def get_user_info(self) -> Dict[str, Any]:
        """
        Holt Benutzer-Informationen und Quota von ElevenLabs API
        
        Returns:
            Dict mit Benutzer-Informationen
        """
        
        try:
            url = f"{self.base_url}/user"
            headers = {"xi-api-key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"✅ Benutzer-Info abgerufen")
                        return user_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ User API Fehler {response.status}: {error_text}")
                        return {}
        
        except Exception as e:
            logger.error(f"💥 User API Fehler: {e}")
            return {}


# Convenience Functions für einfache Nutzung
async def generate_breaking_news_audio(text: str, output_file: str) -> bool:
    """Generiert Breaking News Audio mit JARVIS Voice"""
    service = ElevenLabsAPIService()
    return await service.text_to_speech(
        text=text,
        voice_id=service.voices['breaking_news']['voice_id'],
        output_file=output_file,
        stability=0.5,
        similarity_boost=0.8,
        speed=1.0
    )

async def generate_bitcoin_og_audio(text: str, output_file: str) -> bool:
    """Generiert Bitcoin OG Audio mit Rachel Voice"""
    service = ElevenLabsAPIService()
    return await service.text_to_speech(
        text=text,
        voice_id=service.voices['bitcoin_og']['voice_id'],
        output_file=output_file,
        stability=0.4,
        similarity_boost=0.8,
        speed=1.1
    )

async def generate_zueri_style_audio(text: str, output_file: str) -> bool:
    """Generiert Züri Style Audio mit Bella Voice"""
    service = ElevenLabsAPIService()
    return await service.text_to_speech(
        text=text,
        voice_id=service.voices['zueri_style']['voice_id'],
        output_file=output_file,
        stability=0.6,
        similarity_boost=0.75,
        speed=0.95
    ) 