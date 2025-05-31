#!/usr/bin/env python3
"""
Test-Script für ElevenLabs MCP Integration
Testet die grundlegenden MCP-Funktionen
"""

import os
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

def test_mcp_installation():
    """Testet, ob ElevenLabs MCP korrekt installiert ist."""
    print("🔍 Teste MCP-Installation...")
    
    try:
        result = subprocess.run(
            ["python", "-m", "elevenlabs_mcp", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ ElevenLabs MCP ist installiert und funktionsfähig")
            return True
        else:
            print(f"❌ MCP-Installation fehlerhaft: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Python oder MCP nicht gefunden")
        return False
    except subprocess.TimeoutExpired:
        print("❌ MCP-Test Timeout")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

def test_api_key():
    """Testet, ob der ElevenLabs API-Key verfügbar ist."""
    print("🔑 Teste API-Key...")
    
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY nicht gefunden")
        print("💡 Setze deinen API-Key in der .env-Datei:")
        print("   ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    if len(api_key) < 10:
        print("❌ API-Key scheint ungültig zu sein (zu kurz)")
        return False
    
    print(f"✅ API-Key gefunden: {api_key[:8]}...")
    return True

def test_mcp_config():
    """Testet, ob die MCP-Konfiguration existiert."""
    print("⚙️ Teste MCP-Konfiguration...")
    
    config_file = Path("mcp_config.json")
    
    if not config_file.exists():
        print("❌ mcp_config.json nicht gefunden")
        print("💡 Führe aus: python setup_elevenlabs_mcp.py")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "mcpServers" in config and "ElevenLabs" in config["mcpServers"]:
            print("✅ MCP-Konfiguration ist gültig")
            return True
        else:
            print("❌ MCP-Konfiguration ist unvollständig")
            return False
            
    except json.JSONDecodeError:
        print("❌ MCP-Konfiguration ist fehlerhaft (JSON-Fehler)")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Konfiguration: {e}")
        return False

def test_cursor_integration():
    """Testet, ob Cursor MCP-Integration verfügbar ist."""
    print("🖱️ Teste Cursor-Integration...")
    
    # Windows Cursor-Pfad
    cursor_config = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "cursor.mcp"
    
    if cursor_config.exists():
        try:
            with open(cursor_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "mcpServers" in config and "ElevenLabs" in config["mcpServers"]:
                print("✅ Cursor MCP-Integration konfiguriert")
                return True
            else:
                print("⚠️ Cursor-Konfiguration unvollständig")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Lesen der Cursor-Konfiguration: {e}")
            return False
    else:
        print("⚠️ Cursor MCP-Konfiguration nicht gefunden")
        print("💡 Führe aus: python setup_elevenlabs_mcp.py")
        return False

def show_usage_examples():
    """Zeigt Verwendungsbeispiele für die MCP-Integration."""
    print("\n🎯 MCP-Verwendungsbeispiele:")
    print("=" * 50)
    
    examples = [
        "Generate speech from this text: 'Willkommen bei RadioX!'",
        "Create a voice clone from my audio file",
        "List all available ElevenLabs voices",
        "Transcribe this audio file to text",
        "Generate a radio intro with dramatic emotion",
        "Create a multi-voice radio segment"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\n💡 Diese Befehle funktionieren in:")
    print("   - Cursor Chat")
    print("   - Claude Desktop")
    print("   - Anderen MCP-kompatiblen Clients")

def main():
    """Hauptfunktion für den MCP-Test."""
    print("🎙️ RadioX ElevenLabs MCP Test")
    print("=" * 50)
    
    tests = [
        ("MCP Installation", test_mcp_installation),
        ("API Key", test_api_key),
        ("MCP Konfiguration", test_mcp_config),
        ("Cursor Integration", test_cursor_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Test-Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("✅ Alle Tests erfolgreich! MCP ist einsatzbereit.")
        show_usage_examples()
    else:
        print("⚠️ Einige Tests fehlgeschlagen. Prüfe die Konfiguration.")
        print("\n🔧 Lösungsschritte:")
        print("1. pip install elevenlabs-mcp")
        print("2. Setze ELEVENLABS_API_KEY in .env")
        print("3. python setup_elevenlabs_mcp.py")
        print("4. Starte Cursor/Claude Desktop neu")
    
    return passed == total

if __name__ == "__main__":
    main() 