# RadioX 🎙️🚀

**RadioX** ist ein AI-basiertes, voll konfigurierbares Radiosystem im Stil von GTA & Cyberpunk – personalisiert, modular, radikal anders.

## 💡 Idee
Ein individuell generierbarer Radiosender, der automatisch aus Musik, AI-generierten Voice-Overs, News und Pseudo-Werbung einen durchgehenden Stream produziert – abgestimmt auf die Präferenzen des Users.

## 🔧 Features
- 🎵 Musik-Input via Spotify API (Playlists oder Trends)
- 🗣 ElevenLabs Voice-TTS (mehrsprachig, verschiedene Sprecher)
- 📰 Nachrichten-Snippets & Werbung über GPT und RSS
- 🤖 Personas: unterschiedliche Moderationsstile pro User
- 📦 Audio-Mix als MP3 oder Live-Stream (für Tesla, YouTube etc.)

## 🧱 Projektstruktur
```
ai-radio-mvp/
├── main.py                   # Einstiegspunkt
├── src/
│   ├── audio/
│   │   ├── mixer.py         # Audio-Mixing Pipeline
│   │   ├── stream.py        # Streaming-Handler
│   │   └── effects.py       # Audio-Effekte
│   ├── content/
│   │   ├── music.py         # Musik-Management
│   │   ├── news.py          # News-Generator
│   │   └── ads.py           # Werbe-Generator
│   ├── tts/
│   │   ├── elevenlabs.py    # TTS-Integration
│   │   └── voices.py        # Voice-Management
│   └── utils/
│       ├── config.py        # Konfigurations-Manager
│       └── logger.py        # Logging-System
├── profiles/
│   └── marcel.json          # User-Profil mit Präferenzen
├── tracks/                  # Lokale Musik (Test)
├── audio/                   # Voice-Snippets (generiert)
├── output/                  # Finaler Radiomix (MP3)
├── tests/                   # Unit Tests
├── .env                     # API-Keys
├── requirements.txt         # Dependencies
└── docker-compose.yml       # Container-Konfiguration
```

## ⚙️ Technische Spezifikationen

### Audio-Processing
- Format: MP3, 320kbps
- Sample Rate: 44.1kHz
- Channels: Stereo
- Segment-Länge: 3-5 Minuten
- Übergänge: Crossfade (2-3 Sekunden)

### Content-Generation
- News-Update: Alle 30 Minuten
- Werbe-Spots: 2-3 pro Stunde
- Voice-Over: Pro Segment
- Musik: 70% des Contents

### Personas
- Basis-Personas: 3 (Maximalist, Cyberpunk, Retro)
- Voice-Profile: Pro Persona
- Sprachstil: Anpassbar
- Übergänge: Kontextabhängig

### Performance
- Latenz: < 2 Sekunden
- Buffer: 30 Sekunden
- Cache: 1 Stunde Content
- RAM: ~500MB pro Stream

## 🔄 Entwicklungs-Phasen

### Phase 1: Lokales MVP (2 Wochen)
- [ ] Grundlegende Audio-Pipeline
- [ ] Lokale Musik-Integration
- [ ] Basic TTS mit ElevenLabs
- [ ] Einfache Persona-Implementierung

### Phase 2: Content-Generation (2 Wochen)
- [ ] News-Generator mit GPT
- [ ] Werbe-Spot-Generator
- [ ] Erweiterte Personas
- [ ] Content-Scheduling

### Phase 3: Streaming (1 Woche)
- [ ] Icecast-Integration
- [ ] Stream-Management
- [ ] Performance-Optimierung
- [ ] Error-Handling

### Phase 4: UI & Features (2 Wochen)
- [ ] Web-Interface
- [ ] Persona-Konfiguration
- [ ] Playlist-Management
- [ ] Analytics

## ⚙️ Setup
```bash
# 1. Projekt klonen
$ git clone https://github.com/deinname/radiox.git
$ cd radiox

# 2. Virtuelle Umgebung und Pakete
$ python -m venv venv && source venv/bin/activate
$ pip install -r requirements.txt

# 3. .env Datei anlegen
ELEVENLABS_API_KEY=dein_key
SPOTIFY_CLIENT_ID=dein_client
SPOTIFY_CLIENT_SECRET=dein_secret
```

## 🚀 Ausführen
```bash
$ python main.py
```

## 🔄 Aktueller Flow (MVP)
```text
[Load UserProfile] -->
[Ziehe Musik-Snippets (lokal oder Spotify)] -->
[Generiere Voice-Overs (Greeting, News, Outro)] -->
[Ziehe News Snippets über GPT oder RSS] -->
[Baue Radioprogramm mit ffmpeg] -->
[Speichere Output als MP3]
```

## 🧠 Persona-Design (später modular)
```yaml
persona:
  id: gta_maximalist
  tone: "frech, zynisch, direkt"
  vocab: ["Fiat-Idioten", "Channel-Rebalancing"]
  voice: "anton"
  fallback_mode: "deadpan"
```

## 🔄 Geplante Erweiterungen
- Spotify API Integration mit OAuth
- ElevenLabs TTS mit Charakterwechsel & Multilingual
- Echtzeit-News mit GPT-Zusammenfassung
- Icecast-Streaming statt MP3
- UI für Persona-Konfiguration

## 🔗 Inspiration & Dank
- GTA Vice City Radio
- Blade Runner Ambience
- Bitcoin Maximalism & Open Source

---

> „Wake up, Maxi. Fiat stirbt. Aber du kannst wenigstens dabei Musik hören.“
