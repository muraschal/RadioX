#!/usr/bin/env python3
"""
ElevenLabs MCP Setup für Cursor und andere MCP-Clients
Automatische Konfiguration des ElevenLabs MCP Servers
"""

import os
import json
import platform
from pathlib import Path
from dotenv import load_dotenv

def get_cursor_config_path():
    """Ermittelt den Cursor-Konfigurationspfad je nach Betriebssystem."""
    system = platform.system()
    
    if system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "cursor.mcp"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "cursor.mcp"
    else:  # Linux
        return Path.home() / ".config" / "Cursor" / "User" / "globalStorage" / "cursor.mcp"

def get_claude_config_path():
    """Ermittelt den Claude Desktop-Konfigurationspfad."""
    system = platform.system()
    
    if system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"

def create_mcp_config(api_key: str):
    """Erstellt die MCP-Konfiguration."""
    return {
        "mcpServers": {
            "ElevenLabs": {
                "command": "python",
                "args": ["-m", "elevenlabs_mcp"],
                "env": {
                    "ELEVENLABS_API_KEY": api_key,
                    "ELEVENLABS_MCP_BASE_PATH": str(Path.cwd() / "audio")
                }
            }
        }
    }

def setup_cursor_mcp(api_key: str):
    """Konfiguriert ElevenLabs MCP für Cursor."""
    try:
        config_path = get_cursor_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lade existierende Konfiguration oder erstelle neue
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}
        
        # Füge ElevenLabs MCP hinzu
        config["mcpServers"]["ElevenLabs"] = {
            "command": "python",
            "args": ["-m", "elevenlabs_mcp"],
            "env": {
                "ELEVENLABS_API_KEY": api_key,
                "ELEVENLABS_MCP_BASE_PATH": str(Path.cwd() / "audio")
            }
        }
        
        # Speichere Konfiguration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Cursor MCP konfiguriert: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Cursor-Konfiguration: {e}")
        return False

def setup_claude_mcp(api_key: str):
    """Konfiguriert ElevenLabs MCP für Claude Desktop."""
    try:
        config_path = get_claude_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lade existierende Konfiguration oder erstelle neue
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}
        
        # Füge ElevenLabs MCP hinzu
        config["mcpServers"]["ElevenLabs"] = {
            "command": "python",
            "args": ["-m", "elevenlabs_mcp"],
            "env": {
                "ELEVENLABS_API_KEY": api_key,
                "ELEVENLABS_MCP_BASE_PATH": str(Path.cwd() / "audio")
            }
        }
        
        # Speichere Konfiguration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Claude Desktop MCP konfiguriert: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Claude-Konfiguration: {e}")
        return False

def test_mcp_connection():
    """Testet die MCP-Verbindung."""
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "elevenlabs_mcp", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ ElevenLabs MCP Server ist funktionsfähig")
            return True
        else:
            print(f"❌ MCP Server Test fehlgeschlagen: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim MCP-Test: {e}")
        return False

def main():
    """Hauptfunktion für das MCP-Setup."""
    print("🎙️ ElevenLabs MCP Setup für RadioX")
    print("=" * 50)
    
    # Lade Umgebungsvariablen
    load_dotenv()
    
    # Hole API-Key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY nicht gefunden!")
        print("Bitte setze deinen API-Key in der .env-Datei:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ ElevenLabs API-Key gefunden: {api_key[:8]}...")
    
    # Teste MCP-Verbindung
    if not test_mcp_connection():
        return False
    
    # Konfiguriere für verschiedene Clients
    success_count = 0
    
    # Cursor
    if setup_cursor_mcp(api_key):
        success_count += 1
    
    # Claude Desktop
    if setup_claude_mcp(api_key):
        success_count += 1
    
    # Erstelle lokale Konfigurationsdatei
    try:
        config = create_mcp_config(api_key)
        with open("mcp_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print("✅ Lokale MCP-Konfiguration erstellt: mcp_config.json")
        success_count += 1
    except Exception as e:
        print(f"❌ Fehler bei lokaler Konfiguration: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎉 Setup abgeschlossen! {success_count} Konfigurationen erstellt.")
    print("\n📋 Nächste Schritte:")
    print("1. Starte Cursor/Claude Desktop neu")
    print("2. Der ElevenLabs MCP sollte automatisch verfügbar sein")
    print("3. Teste mit: 'Generate speech from text using ElevenLabs'")
    
    return success_count > 0

if __name__ == "__main__":
    main() 