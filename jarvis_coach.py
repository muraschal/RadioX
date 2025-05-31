#!/usr/bin/env python3
"""
Jarvis AI Coach - Interaktiver AI-Assistent mit ElevenLabs TTS
Kurze, prägnante Antworten im Jarvis-Stil
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from src.tts.elevenlabs_direct import ElevenLabsDirect

class JarvisCoach:
    """AI Coach im Jarvis-Stil mit Sprachausgabe."""
    
    def __init__(self):
        try:
            self.tts = ElevenLabsDirect()
            self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Echte JARVIS-Stimme!
            print("🤖 Echte JARVIS-Stimme aktiviert!")
        except Exception as e:
            print(f"❌ ElevenLabs-Initialisierung fehlgeschlagen: {e}")
            sys.exit(1)
    
    def speak(self, text: str, play_immediately: bool = True):
        """Generiert Sprache und spielt sie optional sofort ab."""
        try:
            # Kurze, prägnante Antworten - maximal 80 Zeichen für Jarvis-Stil
            if len(text) > 80:
                text = text[:77] + "..."
            
            audio_file = self.tts.generate_speech(
                text=text,
                voice_id=self.jarvis_voice_id,
                output_file=f"audio/jarvis_response_{int(time.time())}.mp3",
                stability=0.9,  # Sehr stabil für Jarvis
                similarity_boost=0.95,  # Hohe Ähnlichkeit
                style=0.1,  # Wenig Emotion, professionell
                use_speaker_boost=True
            )
            
            if play_immediately:
                self.play_audio(audio_file)
            
            return audio_file
            
        except Exception as e:
            print(f"❌ Sprachgenerierung fehlgeschlagen: {e}")
            return None
    
    def play_audio(self, audio_file: str):
        """Spielt Audio-Datei ab."""
        try:
            if sys.platform == "win32":
                # Windows - verwende Windows Media Player
                subprocess.run(["start", "", audio_file], shell=True)
            elif sys.platform == "darwin":
                # macOS
                subprocess.run(["afplay", audio_file])
            else:
                # Linux
                subprocess.run(["mpg123", audio_file])
        except Exception as e:
            print(f"⚠️ Audio-Wiedergabe fehlgeschlagen: {e}")
    
    def get_jarvis_response(self, user_input: str) -> str:
        """Generiert Jarvis-ähnliche Antworten basierend auf Benutzereingabe."""
        
        user_input = user_input.lower().strip()
        
        # Begrüßungen
        if any(word in user_input for word in ['hallo', 'hi', 'hey', 'guten']):
            return "Guten Tag, Sir. Wie kann ich assistieren?"
        
        # Status-Anfragen
        elif any(word in user_input for word in ['status', 'wie geht', 'läuft']):
            return "Alle Systeme funktional. Bereit für Befehle."
        
        # RadioX-bezogene Anfragen
        elif 'radiox' in user_input or 'radio' in user_input:
            return "RadioX-System online. Soll ich starten?"
        
        # Coding/Entwicklung
        elif any(word in user_input for word in ['code', 'programmier', 'entwickl', 'bug', 'fehler']):
            return "Code-Analyse läuft. Wie kann ich helfen?"
        
        # Hilfe
        elif any(word in user_input for word in ['hilfe', 'help', 'was kannst']):
            return "Ich bin Ihr persönlicher AI-Assistent."
        
        # Verabschiedung
        elif any(word in user_input for word in ['tschüss', 'bye', 'ende', 'stop']):
            return "Auf Wiedersehen, Sir. Standby-Modus."
        
        # Komplimente
        elif any(word in user_input for word in ['danke', 'gut', 'super', 'toll']):
            return "Gern geschehen. Weitere Befehle?"
        
        # Projekte
        elif any(word in user_input for word in ['projekt', 'arbeit', 'task']):
            return "Projekt-Status wird analysiert."
        
        # Zeit/Termine
        elif any(word in user_input for word in ['zeit', 'uhr', 'termin']):
            return "Zeitmanagement-System bereit."
        
        # Default
        else:
            return "Verstanden. Weitere Details erforderlich."
    
    def interactive_mode(self):
        """Startet den interaktiven Jarvis-Modus."""
        print("🤖 JARVIS AI Coach aktiviert")
        print("💬 Sprechen Sie mit mir! (Tippen Sie 'exit' zum Beenden)")
        print("-" * 50)
        
        # Begrüßung
        self.speak("JARVIS online. Wie kann ich helfen, Sir?")
        
        while True:
            try:
                user_input = input("\n👤 Sie: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'ende', 'stop']:
                    self.speak("System shutdown. Auf Wiedersehen, Sir.")
                    break
                
                if not user_input:
                    continue
                
                # Generiere Antwort
                response = self.get_jarvis_response(user_input)
                print(f"🤖 JARVIS: {response}")
                
                # Spreche Antwort
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\n🤖 JARVIS: Notfall-Shutdown aktiviert.")
                self.speak("Emergency shutdown initiated.")
                break
            except Exception as e:
                print(f"❌ Fehler: {e}")

def quick_test():
    """Schneller Test der JARVIS-Stimme."""
    print("🎯 JARVIS Quick Test")
    print("=" * 20)
    
    coach = JarvisCoach()
    
    # Teste die angeforderten Phrasen
    test_phrases = [
        "Hallo, das ist ein Test von RadioX!",
        "Alle Systeme funktional. Bereit für Befehle.",
        "RadioX-System online. Wie kann ich helfen?"
    ]
    
    for phrase in test_phrases:
        print(f"\n🤖 JARVIS: {phrase}")
        coach.speak(phrase, play_immediately=True)
        time.sleep(2)  # Pause zwischen Tests

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS AI Coach")
    parser.add_argument("--test", action="store_true", help="Schneller Test")
    parser.add_argument("--interactive", action="store_true", help="Interaktiver Modus")
    
    args = parser.parse_args()
    
    if args.test:
        quick_test()
    elif args.interactive:
        coach = JarvisCoach()
        coach.interactive_mode()
    else:
        print("🤖 JARVIS AI Coach")
        print("Verwendung:")
        print("  python jarvis_coach.py --interactive  # Interaktiver Chat")
        print("  python jarvis_coach.py --test         # Schneller Test") 