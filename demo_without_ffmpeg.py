import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

def demo_project_structure():
    """Demonstriert die Projektstruktur und verfügbare Funktionen."""
    
    logger.info("=== RadioX Projekt-Demo ===")
    
    # Lade Umgebungsvariablen
    load_dotenv()
    
    # Zeige Projektstruktur
    logger.info("📁 Projektstruktur:")
    
    # Hauptverzeichnis
    main_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    logger.info(f"   Hauptverzeichnis: {len(main_files)} Dateien")
    for file in sorted(main_files)[:5]:  # Zeige nur die ersten 5
        logger.info(f"   - {file}")
    
    # src-Verzeichnis
    if os.path.exists('src'):
        logger.info("   src/:")
        for subdir in os.listdir('src'):
            if os.path.isdir(f'src/{subdir}'):
                files = os.listdir(f'src/{subdir}')
                logger.info(f"     - {subdir}/: {len(files)} Dateien")
    
    # Audio-Verzeichnis
    if os.path.exists('audio'):
        audio_files = os.listdir('audio')
        logger.info(f"   audio/: {len(audio_files)} Dateien")
        for file in audio_files:
            size = os.path.getsize(f'audio/{file}') / 1024  # KB
            logger.info(f"     - {file} ({size:.1f} KB)")
    
    # Prüfe API-Konfiguration
    logger.info("\n🔑 API-Konfiguration:")
    
    spotify_configured = all([
        os.getenv("SPOTIFY_CLIENT_ID"),
        os.getenv("SPOTIFY_CLIENT_SECRET"),
        os.getenv("SPOTIFY_REDIRECT_URI")
    ])
    logger.info(f"   Spotify API: {'✅ Konfiguriert' if spotify_configured else '❌ Nicht konfiguriert'}")
    
    elevenlabs_configured = bool(os.getenv("ELEVENLABS_API_KEY"))
    logger.info(f"   ElevenLabs API: {'✅ Konfiguriert' if elevenlabs_configured else '❌ Nicht konfiguriert'}")
    
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    logger.info(f"   OpenAI API: {'✅ Konfiguriert' if openai_configured else '❌ Nicht konfiguriert'}")
    
    # Prüfe System-Abhängigkeiten
    logger.info("\n🛠 System-Abhängigkeiten:")
    
    # FFmpeg
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("   FFmpeg: ✅ Installiert")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("   FFmpeg: ❌ Nicht installiert")
    
    # Python-Pakete
    logger.info("\n📦 Python-Pakete:")
    
    packages = [
        'pydub', 'sounddevice', 'spotipy', 'elevenlabs', 
        'openai', 'loguru', 'python-dotenv', 'requests'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"   {package}: ✅ Installiert")
        except ImportError:
            logger.info(f"   {package}: ❌ Nicht installiert")
    
    # Zeige Personas
    logger.info("\n🎭 Verfügbare Personas:")
    
    try:
        from src.utils.config import DEFAULT_PERSONAS
        for name, persona in DEFAULT_PERSONAS.items():
            logger.info(f"   - {name}: {persona.description}")
            logger.info(f"     Ton: {persona.tone}")
            logger.info(f"     Voice ID: {persona.voice.voice_id}")
    except Exception as e:
        logger.error(f"   Fehler beim Laden der Personas: {e}")
    
    # Zusammenfassung
    logger.info("\n📊 Zusammenfassung:")
    logger.info("   RadioX ist ein AI-basiertes Radiosystem mit folgenden Features:")
    logger.info("   - 🎵 Spotify-Integration für Musik")
    logger.info("   - 🗣 ElevenLabs TTS für Moderatoren")
    logger.info("   - 📰 OpenAI für News und Content")
    logger.info("   - 🎛 Audio-Mixing mit ffmpeg")
    logger.info("   - 🎭 Verschiedene Moderator-Personas")
    
    if not any([spotify_configured, elevenlabs_configured]):
        logger.info("\n💡 Nächste Schritte:")
        logger.info("   1. API-Keys in .env-Datei konfigurieren")
        logger.info("   2. FFmpeg installieren für Audio-Processing")
        logger.info("   3. python main.py ausführen für Demo")

if __name__ == "__main__":
    demo_project_structure() 