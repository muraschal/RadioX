import os
from pathlib import Path
from typing import Optional
from elevenlabs import generate, set_api_key
from loguru import logger

from ..utils.config import VoiceConfig

class TTSManager:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API-Key nicht gefunden")
        set_api_key(self.api_key)
        
    def generate_speech(
        self,
        text: str,
        voice_config: VoiceConfig,
        output_dir: str = "audio",
        filename: Optional[str] = None
    ) -> str:
        """Generiert Sprachausgabe mit ElevenLabs."""
        try:
            # Generiere Audio (angepasst an neue API)
            audio = generate(
                text=text,
                voice=voice_config.voice_id,
                model="eleven_multilingual_v2"
            )
            
            # Speichere Audio
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            if not filename:
                filename = f"tts_{hash(text)}.mp3"
                
            file_path = output_path / filename
            with open(file_path, "wb") as f:
                f.write(audio)
                
            logger.info(f"TTS generiert und gespeichert: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Fehler bei TTS-Generierung: {e}")
            raise
            
    def generate_greeting(self, persona_name: str, voice_config: VoiceConfig) -> str:
        """Generiert eine Begrüßung für die Persona."""
        greetings = {
            "maximalist": "Willkommen im RadioX, wo Fiat stirbt und Bitcoin lebt!",
            "cyberpunk": "Schaltet ein, Neo. Die Zukunft des Radios beginnt jetzt.",
            "retro": "Hey there, RadioX-Fans! Let's rock the house!"
        }
        
        text = greetings.get(persona_name, "Willkommen bei RadioX!")
        return self.generate_speech(
            text=text,
            voice_config=voice_config,
            filename=f"greeting_{persona_name}.mp3"
        )
        
    def generate_outro(self, persona_name: str, voice_config: VoiceConfig) -> str:
        """Generiert einen Abschluss für die Persona."""
        outros = {
            "maximalist": "HODL strong, Leute! Bis zum nächsten Mal.",
            "cyberpunk": "Stay connected. The signal never dies.",
            "retro": "That's all for now, folks! Keep it real!"
        }
        
        text = outros.get(persona_name, "Bis zum nächsten Mal bei RadioX!")
        return self.generate_speech(
            text=text,
            voice_config=voice_config,
            filename=f"outro_{persona_name}.mp3"
        ) 