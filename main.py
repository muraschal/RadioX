import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from src.audio.mixer import AudioMixer
from src.tts.elevenlabs import TTSManager
from src.content.spotify import SpotifyManager
from src.utils.config import DEFAULT_PERSONAS, DEFAULT_CONFIG

def setup_logging():
    """Konfiguriert das Logging-System."""
    logger.add("radio.log", rotation="1 day", retention="7 days")

def create_demo_segment(persona_name: str = "maximalist"):
    """Erstellt ein Demo-Radiosegment."""
    try:
        # Initialisiere Komponenten
        mixer = AudioMixer()
        tts = TTSManager()
        spotify = SpotifyManager()
        
        # Hole Persona-Konfiguration
        persona = DEFAULT_PERSONAS[persona_name]
        
        # Generiere Begrüßung
        logger.info(f"Generiere Begrüßung für {persona_name}...")
        greeting_path = tts.generate_greeting(persona_name, persona.voice)
        
        # Lade Begrüßung
        greeting_audio = mixer.load_audio(greeting_path)
        
        # Füge Begrüßung zum Mix hinzu
        mixer.add_segment(greeting_audio)
        
        # Hole Top-Tracks von Spotify
        logger.info("Hole Top-Tracks von Spotify...")
        tracks = spotify.get_top_tracks(limit=3)
        
        # Zeige gefundene Tracks
        for track in tracks:
            logger.info(f"Track: {track['name']} von {', '.join(track['artists'])}")
        
        # TODO: Hier später Musik und News einfügen
        
        # Generiere Abschluss
        logger.info("Generiere Abschluss...")
        outro_path = tts.generate_outro(persona_name, persona.voice)
        
        # Lade Abschluss
        outro_audio = mixer.load_audio(outro_path)
        
        # Füge Abschluss zum Mix hinzu
        mixer.add_segment(outro_audio)
        
        # Exportiere Mix
        output_path = mixer.export(f"demo_{persona_name}.mp3")
        logger.success(f"Demo-Segment erstellt: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Fehler bei der Demo-Erstellung: {e}")
        raise

def main():
    """Hauptfunktion für die Demo."""
    # Lade Umgebungsvariablen
    load_dotenv()
    
    # Setup Logging
    setup_logging()
    
    logger.info("Starte RadioX Demo...")
    
    # Erstelle Demo-Segment
    output_path = create_demo_segment()
    
    logger.success(f"Demo erfolgreich erstellt! Output: {output_path}")

if __name__ == "__main__":
    main() 