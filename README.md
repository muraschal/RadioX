# RadioX - AI-Powered Radio Broadcasting System

Ein innovatives AI-gesteuertes Radio-System mit modularer Architektur für automatisierte Broadcast-Generierung.

## 🎯 Überblick

RadioX ist ein vollständig automatisiertes Radio-System, das:
- **News sammelt** von RSS-Feeds, Twitter und anderen Quellen
- **Content analysiert** und intelligent verarbeitet
- **Broadcasts generiert** mit GPT-4 für natürliche Dialoge
- **Audio produziert** mit ElevenLabs Text-to-Speech
- **System überwacht** mit umfassendem Monitoring

## 🏗️ Architektur

### Backend (Python)
```
backend/
├── radiox_master.py          # 🎛️ Master Control Script
├── src/services/             # 📦 Modulare Services
│   ├── data_collection_service.py      # 📊 Datensammlung
│   ├── content_processing_service.py   # 🔄 Content-Verarbeitung
│   ├── broadcast_generation_service.py # 🎭 Broadcast-Generierung
│   ├── audio_generation_service.py     # 🔊 Audio-Synthese
│   ├── system_monitoring_service.py    # 📈 System-Monitoring
│   ├── rss_feed_manager.py            # 📰 RSS-Management
│   ├── weather_service.py             # 🌤️ Wetter-Daten
│   ├── crypto_service.py              # ₿ Crypto-Preise
│   ├── twitter_service.py             # 🐦 Twitter-Integration
│   └── supabase_service.py            # 🗄️ Datenbank
├── requirements.txt          # 📋 Dependencies
└── env_template.txt         # ⚙️ Environment-Vorlage
```

### Frontend (Next.js)
```
frontend/
├── app/                     # 🌐 Next.js App Router
├── components/              # 🧩 React Components
├── lib/                     # 🛠️ Utility Functions
├── styles/                  # 🎨 Styling
└── package.json            # 📦 Dependencies
```

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp env_template.txt .env
# Konfiguriere .env mit deinen API-Keys
```

### 2. Frontend Setup
```bash
cd frontend
npm install
# oder
pnpm install
```

### 3. Broadcast generieren
```bash
cd backend
python radiox_master.py --action generate_broadcast --time 16:00
```

## 🎛️ Master Script Kommandos

Das `radiox_master.py` Script ist der zentrale Entry-Point:

```bash
# Vollständigen Broadcast generieren
python radiox_master.py --action generate_broadcast --time 16:00 --channel zurich

# Nur News analysieren
python radiox_master.py --action analyze_news --max-age 2

# Alle Services testen
python radiox_master.py --action test_services

# System-Status abrufen
python radiox_master.py --action system_status

# Alte Daten aufräumen
python radiox_master.py --action cleanup --cleanup-days 7
```

### Parameter
- `--time`: Zielzeit (HH:MM) für zeitspezifische Stile
- `--channel`: Radio-Kanal (zurich, basel, bern)
- `--news-count`: Anzahl News für Broadcast (Standard: 4)
- `--max-age`: Maximales News-Alter in Stunden (Standard: 1)
- `--generate-audio`: Audio-Dateien generieren
- `--cleanup-days`: Alter für Daten-Cleanup (Standard: 7)

## 🔧 Services

### 📊 Data Collection Service
- RSS-Feed-Management
- Twitter/X-Integration
- Wetter-Daten (OpenWeatherMap)
- Crypto-Preise (CoinMarketCap)
- Parallele Datensammlung

### 🔄 Content Processing Service
- News-Analyse und Kategorisierung
- Duplikat-Erkennung
- Sentiment-Analyse
- Content-Optimierung
- Themen-Balance

### 🎭 Broadcast Generation Service
- GPT-4 basierte Skript-Generierung
- Marcel & Jarvis Dialog-Erstellung
- Zeitspezifische Stile (Morgen, Mittag, Abend, Nacht)
- Schweizer Lokalkolorit

### 🔊 Audio Generation Service
- ElevenLabs Text-to-Speech
- Sprecher-spezifische Stimmen
- Audio-Mixing und -Verarbeitung
- Multiple Format-Unterstützung

### 📈 System Monitoring Service
- Performance-Metriken
- Error-Tracking
- System-Health-Checks
- Automatisches Cleanup
- Alert-System

## 🌐 Frontend Features

- **Live Radio Interface** - Moderne Web-App
- **News Dashboard** - Aktuelle Nachrichten-Übersicht
- **Broadcast History** - Vergangene Sendungen
- **System Monitoring** - Real-time Status
- **Responsive Design** - Mobile-optimiert

## 🔑 Umgebungsvariablen

Kopiere `backend/env_template.txt` zu `backend/.env` und konfiguriere:

```env
# OpenAI (für Broadcast-Generierung)
OPENAI_API_KEY=your_openai_key

# ElevenLabs (für Audio-Synthese)
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_MARCEL_VOICE_ID=voice_id_marcel
ELEVENLABS_JARVIS_VOICE_ID=voice_id_jarvis

# Supabase (Datenbank)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional: Externe APIs
OPENWEATHERMAP_API_KEY=your_weather_key
COINMARKETCAP_API_KEY=your_crypto_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

## 📊 Datenbank

Das System verwendet Supabase (PostgreSQL) mit folgenden Tabellen:
- `broadcast_scripts` - Generierte Broadcast-Skripte
- `broadcast_logs` - System-Events und Monitoring
- `used_news` - Verwendete News (Duplikat-Vermeidung)
- `rss_feed_preferences` - RSS-Feed-Konfiguration

## 🎨 Broadcast-Stile

Das System passt Stil und Tempo automatisch an die Tageszeit an:

- **🌅 Morgen (6-11h)**: Energisch, motivierend, optimistisch
- **☀️ Mittag (12-17h)**: Entspannt, informativ, freundlich
- **🌆 Abend (18-22h)**: Gemütlich, nachdenklich, ruhig
- **🌙 Nacht (23-5h)**: Ruhig, entspannend, introspektiv

## 🔄 Deployment

### Backend
```bash
# Produktions-Setup
pip install -r requirements.txt
python radiox_master.py --action test_services
```

### Frontend (Vercel)
```bash
# Automatisches Deployment via Git
git push origin main
```

## 📈 Monitoring

Das System bietet umfassendes Monitoring:
- **System-Metriken**: CPU, Memory, Disk
- **Performance**: Response-Zeiten, Erfolgsraten
- **Error-Tracking**: Automatische Fehler-Protokollierung
- **Health-Score**: Gesamtsystem-Bewertung
- **Alerts**: Automatische Warnungen bei Problemen

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Committe deine Änderungen
4. Push zum Branch
5. Erstelle einen Pull Request

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

Bei Fragen oder Problemen:
1. Prüfe die [Dokumentation](RADIOX_MONSTER_RELEASE_V1.0_DOCUMENTATION.md)
2. Teste mit `python radiox_master.py --action test_services`
3. Prüfe die Logs in `backend/logs/`
4. Erstelle ein GitHub Issue

---

**RadioX** - Wo AI auf Radio trifft 🎙️✨
