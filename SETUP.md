# RadioX Setup Anleitung

## 🚀 Installation

### 1. Repository klonen
```bash
git clone https://github.com/muraschal/RadioX.git
cd RadioX
```

### 2. Virtual Environment erstellen
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oder: venv\Scripts\activate  # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. ElevenLabs MCP installieren (Empfohlen)
```bash
# Installiere den offiziellen ElevenLabs MCP Server
pip install elevenlabs-mcp

# Automatische Konfiguration für Cursor/Claude Desktop
python setup_elevenlabs_mcp.py
```

### 5. FFmpeg installieren (für Audio-Processing)
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download von: https://ffmpeg.org/download.html
```

### 6. API Keys konfigurieren
```bash
cp .env.example .env
```

Bearbeite `.env` mit deinen echten API Keys:

#### Spotify API (https://developer.spotify.com/dashboard)
1. Erstelle eine neue App
2. Füge `http://127.0.0.1:8888/callback` als Redirect URI hinzu
3. Kopiere Client ID und Secret

#### ElevenLabs API (https://elevenlabs.io)
1. Account erstellen
2. API Key generieren
3. Voice ID ermitteln (optional)

#### OpenAI API (https://platform.openai.com)
1. Account erstellen
2. API Key generieren
3. Guthaben aufladen

### 7. Erste Tests
```bash
# Spotify Authentication testen
python spotify_test.py

# Hauptanwendung starten
python main.py
```

## 🎙️ ElevenLabs MCP Integration

### Was ist MCP?
Model Context Protocol (MCP) ermöglicht es AI-Assistenten wie Cursor und Claude Desktop, direkt mit ElevenLabs zu interagieren. Das bedeutet:

- **Globale Verfügbarkeit**: ElevenLabs ist in allen deinen Projekten verfügbar
- **Erweiterte Features**: Voice Cloning, Audio-Transkription, erweiterte TTS
- **Nahtlose Integration**: Direkte Sprachgenerierung aus dem Chat

### Automatische Konfiguration
```bash
# Führe das Setup-Script aus
python setup_elevenlabs_mcp.py
```

Das Script konfiguriert automatisch:
- ✅ Cursor MCP-Integration
- ✅ Claude Desktop MCP-Integration  
- ✅ Lokale Konfigurationsdatei

### Manuelle Konfiguration (falls nötig)

#### Für Cursor:
1. Öffne Cursor Settings
2. Gehe zu "Extensions" → "MCP"
3. Füge diese Konfiguration hinzu:

```json
{
  "mcpServers": {
    "ElevenLabs": {
      "command": "python",
      "args": ["-m", "elevenlabs_mcp"],
      "env": {
        "ELEVENLABS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Für Claude Desktop:
Bearbeite `claude_desktop_config.json`:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

### MCP-Features testen
Nach dem Neustart von Cursor/Claude Desktop kannst du folgende Befehle testen:

```
"Generate speech from this text using ElevenLabs"
"Create a voice clone from this audio file"
"Transcribe this audio file to text"
"List all available ElevenLabs voices"
```

### Verfügbare MCP-Tools
- `generate_audio_simple`: Einfache Text-zu-Sprache
- `generate_audio_script`: Multi-Voice-Skripte
- `clone_voice`: Voice Cloning
- `transcribe_audio`: Audio-Transkription
- `list_voices`: Verfügbare Stimmen anzeigen
- `get_voiceover_history`: TTS-Historie

## 🎵 Verwendung

Das System generiert automatisch personalisierte Radio-Inhalte mit:
- **Musik** von Spotify basierend auf deinen Präferenzen
- **KI-Moderator** mit verschiedenen Personas
- **Nachrichten & Werbung** (simuliert)
- **Seamless Audio-Mixing**
- **🆕 MCP-Enhanced TTS** mit erweiterten Features

## 🎭 Personas

- **Maximalist**: Energetisch, übertrieben, hyperaktiv
- **Cyberpunk**: Düster, technisch, futuristisch  
- **Retro**: Nostalgisch, warm, entspannt

## 🛠 Troubleshooting

### ElevenLabs MCP Probleme
```bash
# Teste MCP-Verbindung
python -m elevenlabs_mcp --help

# Prüfe API-Key
echo $ELEVENLABS_API_KEY

# Neuinstallation
pip uninstall elevenlabs-mcp
pip install elevenlabs-mcp
python setup_elevenlabs_mcp.py
```

### Cursor MCP nicht verfügbar
1. Starte Cursor komplett neu
2. Prüfe MCP-Konfiguration in Settings
3. Logs prüfen: `%APPDATA%\Cursor\logs\`

### Spotify "INVALID_CLIENT" Fehler
- Prüfe, dass Redirect URI exakt übereinstimmt: `http://127.0.0.1:8888/callback`
- Verwende `127.0.0.1` statt `localhost`
- Port 8888 muss frei sein

### Audio-Probleme
- FFmpeg korrekt installiert?
- Sounddevice funktioniert: `python -c "import sounddevice; print('OK')"`

### API Rate Limits
- ElevenLabs: Begrenzte Characters pro Monat
- OpenAI: Pay-per-use Modell
- Spotify: 100 Requests pro Minute

## 📁 Projektstruktur

```
RadioX/
├── main.py                    # Hauptanwendung
├── setup_elevenlabs_mcp.py    # 🆕 MCP-Setup Script
├── mcp_config.json           # 🆕 MCP-Konfiguration
├── src/
│   ├── audio/                # Audio-Processing
│   ├── config/               # Persona-Konfigurationen
│   ├── integrations/         # API-Wrapper
│   ├── tts/                  # TTS & MCP Integration
│   └── utils/                # Hilfsfunktionen
├── requirements.txt          # Python Dependencies
├── .env.example             # Environment Template
└── README.md                # Projekt-Dokumentation
```

## 🎯 Erweiterte Features mit MCP

### Voice Cloning
```python
# In deinem Code oder über Cursor/Claude
"Clone my voice from this audio file and use it for the radio host"
```

### Multi-Voice Radio Segments
```python
# Erstelle komplexe Radio-Segmente
"Create a radio segment with 3 different voices: 
- Intro with energetic voice
- News with professional voice  
- Outro with warm voice"
```

### Audio-Transkription
```python
# Transkribiere Audio-Dateien
"Transcribe this podcast episode and create a summary"
```

## 🚀 Nächste Schritte

1. **Installiere MCP**: `python setup_elevenlabs_mcp.py`
2. **Starte Cursor neu**: Damit MCP verfügbar wird
3. **Teste Integration**: "Generate speech using ElevenLabs"
4. **Experimentiere**: Voice Cloning, Multi-Voice-Segmente
5. **Erweitere RadioX**: Nutze MCP für bessere TTS-Features