#!/usr/bin/env python3
"""
JARVIS Cursor Integration - Subtile AI-Assistent Integration
Spielt Audio im Hintergrund ab ohne störende Player-Fenster
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from src.tts.elevenlabs_direct import ElevenLabsDirect

class JarvisCursorIntegration:
    """Subtile JARVIS-Integration für Cursor ohne störende Audio-Player."""
    
    def __init__(self):
        try:
            self.tts = ElevenLabsDirect()
            self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Echte JARVIS-Stimme
            self.audio_enabled = True
            print("🤖 JARVIS Cursor Integration aktiviert (subtil)")
        except Exception as e:
            print(f"❌ ElevenLabs-Initialisierung fehlgeschlagen: {e}")
            sys.exit(1)
    
    def speak_silent(self, text: str) -> str:
        """Generiert Sprache und spielt sie subtil im Hintergrund ab."""
        try:
            # Kurze, prägnante Antworten
            if len(text) > 80:
                text = text[:77] + "..."
            
            audio_file = self.tts.generate_speech(
                text=text,
                voice_id=self.jarvis_voice_id,
                output_file=f"audio/jarvis_cursor_{int(time.time())}.mp3",
                stability=0.9,
                similarity_boost=0.95,
                style=0.1,
                use_speaker_boost=True
            )
            
            if self.audio_enabled:
                # Spiele Audio im Hintergrund ab (ohne Fenster)
                threading.Thread(target=self._play_audio_silent, args=(audio_file,), daemon=True).start()
            
            return audio_file
            
        except Exception as e:
            print(f"❌ Sprachgenerierung fehlgeschlagen: {e}")
            return None
    
    def _play_audio_silent(self, audio_file: str):
        """Spielt Audio im Hintergrund ab ohne sichtbare Player."""
        try:
            if sys.platform == "win32":
                # Windows - verwende verschiedene Methoden für MP3-Wiedergabe
                audio_path = os.path.abspath(audio_file)
                
                # Methode 1: Windows Media Player (minimiert)
                try:
                    subprocess.run([
                        "powershell", "-WindowStyle", "Hidden", "-c",
                        f'Add-Type -AssemblyName presentationCore; '
                        f'$mediaPlayer = New-Object system.windows.media.mediaplayer; '
                        f'$mediaPlayer.open([uri]"{audio_path}"); '
                        f'$mediaPlayer.Play(); '
                        f'Start-Sleep -Seconds 5'
                    ], capture_output=True, timeout=10)
                    return
                except:
                    pass
                
                # Methode 2: Windows Media Player direkt (minimiert)
                try:
                    subprocess.run([
                        "start", "/min", "wmplayer", "/close", audio_file
                    ], shell=True, capture_output=True, timeout=10)
                    return
                except:
                    pass
                
                # Methode 3: Fallback - normaler Start aber minimiert
                try:
                    subprocess.run([
                        "start", "/min", audio_file
                    ], shell=True, capture_output=True)
                except:
                    pass
                    
            elif sys.platform == "darwin":
                # macOS - afplay ist bereits still
                subprocess.run(["afplay", audio_file], capture_output=True)
            else:
                # Linux - verwende mpg123 still
                subprocess.run(["mpg123", "-q", audio_file], capture_output=True)
                
        except Exception as e:
            print(f"🔇 Audio-Wiedergabe still fehlgeschlagen: {e}")
    
    def toggle_audio(self):
        """Schaltet Audio-Ausgabe ein/aus."""
        self.audio_enabled = not self.audio_enabled
        status = "aktiviert" if self.audio_enabled else "deaktiviert"
        print(f"🔊 JARVIS Audio {status}")
        return self.audio_enabled
    
    def quick_response(self, message: str) -> str:
        """Schnelle JARVIS-Antwort für Cursor-Integration."""
        
        message = message.lower().strip()
        
        # Coding-Hilfe
        if any(word in message for word in ['fehler', 'error', 'bug', 'problem']):
            response = "Analysiere Fehler. Einen Moment, Sir."
            
        elif any(word in message for word in ['code', 'function', 'class', 'method']):
            response = "Code-Review läuft. Wie kann ich helfen?"
            
        elif any(word in message for word in ['test', 'debug', 'fix']):
            response = "Debugging-Protokoll initiiert."
            
        # Projekt-Management
        elif any(word in message for word in ['commit', 'git', 'push', 'pull']):
            response = "Git-Operationen überwacht."
            
        elif any(word in message for word in ['deploy', 'build', 'compile']):
            response = "Build-System bereit."
            
        # Status & Hilfe
        elif any(word in message for word in ['status', 'wie geht', 'läuft']):
            response = "Alle Systeme funktional."
            
        elif any(word in message for word in ['hilfe', 'help']):
            response = "JARVIS bereit. Was benötigen Sie?"
            
        # Begrüßung
        elif any(word in message for word in ['hallo', 'hi', 'hey']):
            response = "Guten Tag, Sir. Bereit für Arbeit."
            
        # Komplimente
        elif any(word in message for word in ['danke', 'gut', 'super']):
            response = "Gern geschehen. Weitere Befehle?"
            
        # Default
        else:
            response = "Verstanden. Weitere Details?"
        
        # Generiere und spiele Audio subtil
        self.speak_silent(response)
        
        return response

def jarvis_say(message: str):
    """Einfache Funktion für schnelle JARVIS-Antworten."""
    jarvis = JarvisCursorIntegration()
    response = jarvis.quick_response(message)
    print(f"🤖 JARVIS: {response}")
    return response

def jarvis_silent(text: str):
    """Lässt JARVIS einen spezifischen Text sprechen (subtil)."""
    jarvis = JarvisCursorIntegration()
    jarvis.speak_silent(text)
    print(f"🤖 JARVIS: {text}")

# Convenience-Funktionen für Cursor
def j(message: str):
    """Kurze Funktion: j('hallo') für schnelle JARVIS-Interaktion."""
    return jarvis_say(message)

def js(text: str):
    """Kurze Funktion: js('text') für direktes JARVIS-Sprechen."""
    return jarvis_silent(text)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Cursor Integration")
    parser.add_argument("message", nargs="?", help="Nachricht an JARVIS")
    parser.add_argument("--say", "-s", help="Lasse JARVIS einen Text sprechen")
    parser.add_argument("--toggle-audio", "-t", action="store_true", help="Audio ein/aus")
    
    args = parser.parse_args()
    
    if args.toggle_audio:
        jarvis = JarvisCursorIntegration()
        jarvis.toggle_audio()
    elif args.say:
        jarvis_silent(args.say)
    elif args.message:
        jarvis_say(args.message)
    else:
        print("🤖 JARVIS Cursor Integration")
        print("Verwendung:")
        print("  python jarvis_cursor_integration.py 'hallo'")
        print("  python jarvis_cursor_integration.py --say 'System online'")
        print("  python jarvis_cursor_integration.py --toggle-audio")
        print("\nIn Python:")
        print("  from jarvis_cursor_integration import j, js")
        print("  j('status')  # Interaktive Antwort")
        print("  js('System bereit')  # Direktes Sprechen") 