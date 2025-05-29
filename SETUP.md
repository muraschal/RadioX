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

### 4. FFmpeg installieren (für Audio-Processing)
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download von: https://ffmpeg.org/download.html
```

### 5. API Keys konfigurieren
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

### 6. Erste Tests
```bash
# Spotify Authentication testen
python spotify_test.py

# Hauptanwendung starten
python main.py
```

## 🎵 Verwendung

Das System generiert automatisch personalisierte Radio-Inhalte mit:
- **Musik** von Spotify basierend auf deinen Präferenzen
- **KI-Moderator** mit verschiedenen Personas
- **Nachrichten & Werbung** (simuliert)
- **Seamless Audio-Mixing**

## 🎭 Personas

- **Maximalist**: Energetisch, übertrieben, hyperaktiv
- **Cyberpunk**: Düster, technisch, futuristisch  
- **Retro**: Nostalgisch, warm, entspannt

## 🛠 Troubleshooting

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
├── main.py              # Hauptanwendung
├── src/
│   ├── audio/           # Audio-Processing
│   ├── config/          # Persona-Konfigurationen
│   ├── integrations/    # API-Wrapper
│   └── utils/           # Hilfsfunktionen
├── requirements.txt     # Python Dependencies
├── .env.example        # Environment Template
└── README.md           # Projekt-Dokumentation
``` 