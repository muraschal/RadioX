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
        
        # Prüfe, ob API-Keys verfügbar sind
        if not os.getenv("ELEVENLABS_API_KEY"):
            logger.warning("ElevenLabs API-Key nicht gefunden - überspringe TTS")
            tts = None
        else:
            tts = TTSManager()
        
        if not all([os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"), os.getenv("SPOTIFY_REDIRECT_URI")]):
            logger.warning("Spotify API-Credentials nicht vollständig - überspringe Spotify")
            spotify = None
        else:
            spotify = SpotifyManager()
        
        # Hole Persona-Konfiguration
        persona = DEFAULT_PERSONAS[persona_name]
        
        # Generiere Begrüßung (falls TTS verfügbar)
        if tts:
            logger.info(f"Generiere Begrüßung für {persona_name}...")
            greeting_path = tts.generate_greeting(persona_name, persona.voice)
            
            # Füge Begrüßung zum Mix hinzu
            mixer.add_segment(greeting_path)
        else:
            logger.info("TTS nicht verfügbar - überspringe Begrüßung")
        
        # Hole Top-Tracks von Spotify (falls verfügbar)
        if spotify:
            logger.info("Hole Top-Tracks von Spotify...")
            try:
                tracks = spotify.get_top_tracks(limit=3)
                
                # Zeige gefundene Tracks
                for track in tracks:
                    logger.info(f"Track: {track['name']} von {', '.join(track['artists'])}")
            except Exception as e:
                logger.warning(f"Spotify-Fehler: {e}")
        else:
            logger.info("Spotify nicht verfügbar - überspringe Musik-Tracks")
        
        # TODO: Hier später Musik und News einfügen
        
        # Generiere Abschluss (falls TTS verfügbar)
        if tts:
            logger.info("Generiere Abschluss...")
            outro_path = tts.generate_outro(persona_name, persona.voice)
            
            # Füge Abschluss zum Mix hinzu
            mixer.add_segment(outro_path)
        else:
            logger.info("TTS nicht verfügbar - überspringe Abschluss")
        
        # Exportiere Mix (nur wenn Segmente vorhanden)
        if mixer.segments:
            output_path = mixer.export(f"demo_{persona_name}.mp3")
            logger.success(f"Demo-Segment erstellt: {output_path}")
            return output_path
        else:
            logger.warning("Keine Audio-Segmente zum Exportieren vorhanden")
            return None
        
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
    
    if output_path:
        logger.success(f"Demo erfolgreich erstellt! Output: {output_path}")
    else:
        logger.info("Demo beendet - keine Audio-Ausgabe erstellt (API-Keys fehlen)")

if __name__ == "__main__":
    main() 