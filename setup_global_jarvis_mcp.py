#!/usr/bin/env python3
"""
Globale JARVIS MCP-Konfiguration für Cursor
Macht JARVIS in allen Cursor-Projekten verfügbar
"""

import os
import json
import platform
from pathlib import Path
from dotenv import load_dotenv

def get_cursor_global_config_path():
    """Ermittelt den globalen Cursor MCP-Konfigurationspfad."""
    system = platform.system()
    
    if system == "Windows":
        # Windows: AppData\Roaming\Cursor\User\settings.json
        return Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
    else:  # Linux
        return Path.home() / ".config" / "Cursor" / "User" / "settings.json"

def create_global_jarvis_mcp_config():
    """Erstellt die globale JARVIS MCP-Konfiguration für Cursor."""
    
    # Lade API-Key
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY nicht gefunden!")
        print("Bitte setze deinen API-Key in der .env-Datei:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    # Erstelle MCP-Konfiguration
    mcp_config = {
        "mcp.servers": {
            "jarvis-elevenlabs": {
                "command": "python",
                "args": ["-m", "elevenlabs_mcp"],
                "env": {
                    "ELEVENLABS_API_KEY": api_key
                }
            }
        }
    }
    
    # Pfad zur globalen Cursor-Konfiguration
    config_path = get_cursor_global_config_path()
    
    try:
        # Lade existierende Konfiguration
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        else:
            existing_config = {}
        
        # Füge MCP-Konfiguration hinzu
        existing_config.update(mcp_config)
        
        # Erstelle Verzeichnis falls nötig
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Speichere Konfiguration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2)
        
        print(f"✅ Globale JARVIS MCP-Konfiguration erstellt: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei globaler Konfiguration: {e}")
        return False

def create_jarvis_mcp_wrapper():
    """Erstellt einen globalen JARVIS MCP-Wrapper."""
    
    wrapper_content = '''#!/usr/bin/env python3
"""
Globaler JARVIS MCP-Wrapper
Macht JARVIS-Funktionen in jedem Cursor-Projekt verfügbar
"""

import os
import sys
import json
import requests
from pathlib import Path

class GlobalJarvisMCP:
    """Globaler JARVIS MCP-Server."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY nicht gefunden")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"
    
    def generate_speech(self, text: str, output_dir: str = None) -> str:
        """Generiert Sprache mit JARVIS-Stimme."""
        
        if not output_dir:
            output_dir = Path.home() / "jarvis_audio"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # API-Request
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.9,
                "similarity_boost": 0.95,
                "style": 0.1,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(
            f"{self.base_url}/text-to-speech/{self.jarvis_voice_id}",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        
        # Speichere Audio
        output_file = output_dir / f"jarvis_{hash(text) % 100000}.mp3"
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        return str(output_file)
    
    def quick_response(self, message: str) -> dict:
        """Schnelle JARVIS-Antwort."""
        
        message = message.lower().strip()
        
        # Generiere Antwort basierend auf Eingabe
        if any(word in message for word in ['status', 'wie geht', 'läuft']):
            response = "Alle Systeme funktional, Sir."
        elif any(word in message for word in ['code', 'review', 'programmier']):
            response = "Code-Analyse läuft. Wie kann ich helfen?"
        elif any(word in message for word in ['fehler', 'error', 'bug']):
            response = "Analysiere Fehler. Einen Moment, Sir."
        elif any(word in message for word in ['hallo', 'hi', 'hey']):
            response = "Guten Tag, Sir. Bereit für Arbeit."
        elif any(word in message for word in ['danke', 'gut', 'super']):
            response = "Gern geschehen. Weitere Befehle?"
        else:
            response = "Verstanden. Weitere Details erforderlich."
        
        # Generiere Audio
        try:
            audio_file = self.generate_speech(response)
            return {
                "text": response,
                "audio_file": audio_file,
                "status": "success"
            }
        except Exception as e:
            return {
                "text": response,
                "audio_file": None,
                "status": "error",
                "error": str(e)
            }

# MCP-Server-Funktionen
def list_tools():
    """Listet verfügbare JARVIS-Tools auf."""
    return [
        {
            "name": "jarvis_say",
            "description": "Lässt JARVIS einen Text sprechen",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text den JARVIS sprechen soll"}
                },
                "required": ["text"]
            }
        },
        {
            "name": "jarvis_respond",
            "description": "JARVIS antwortet intelligent auf eine Nachricht",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Nachricht an JARVIS"}
                },
                "required": ["message"]
            }
        }
    ]

def call_tool(name: str, arguments: dict):
    """Führt JARVIS-Tool aus."""
    jarvis = GlobalJarvisMCP()
    
    if name == "jarvis_say":
        text = arguments.get("text", "")
        result = jarvis.generate_speech(text)
        return {"content": [{"type": "text", "text": f"JARVIS: {text}\\nAudio: {result}"}]}
    
    elif name == "jarvis_respond":
        message = arguments.get("message", "")
        result = jarvis.quick_response(message)
        return {"content": [{"type": "text", "text": f"JARVIS: {result['text']}\\nAudio: {result.get('audio_file', 'N/A')}"}]}
    
    else:
        return {"content": [{"type": "text", "text": "Unbekanntes JARVIS-Tool"}]}

if __name__ == "__main__":
    # Einfacher Test
    jarvis = GlobalJarvisMCP()
    result = jarvis.quick_response("hallo jarvis")
    print(f"JARVIS: {result['text']}")
    if result['audio_file']:
        print(f"Audio: {result['audio_file']}")
'''
    
    # Speichere Wrapper
    wrapper_path = Path("global_jarvis_mcp.py")
    with open(wrapper_path, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print(f"✅ Globaler JARVIS MCP-Wrapper erstellt: {wrapper_path}")
    return wrapper_path

def main():
    """Hauptfunktion für globale JARVIS MCP-Setup."""
    print("🌍 Globale JARVIS MCP-Konfiguration für Cursor")
    print("=" * 50)
    
    # Erstelle globale Konfiguration
    if create_global_jarvis_mcp_config():
        print("✅ Globale MCP-Konfiguration erfolgreich")
    else:
        print("❌ Globale MCP-Konfiguration fehlgeschlagen")
        return False
    
    # Erstelle MCP-Wrapper
    wrapper_path = create_jarvis_mcp_wrapper()
    
    print("\n" + "=" * 50)
    print("🎉 Globale JARVIS MCP-Setup abgeschlossen!")
    print("\n📋 Nächste Schritte:")
    print("1. Starte Cursor komplett neu")
    print("2. JARVIS ist jetzt in ALLEN Cursor-Projekten verfügbar")
    print("3. Verwende in jedem Projekt:")
    print("   - 'Generate speech with JARVIS: Hello World'")
    print("   - 'JARVIS respond to: status check'")
    
    return True

if __name__ == "__main__":
    main() 