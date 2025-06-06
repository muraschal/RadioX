# RadioX - AI-Powered Radio Broadcasting System

> **🚀 Production Ready** - Vollständiges AI-Radio-System mit DALL-E 3 Cover-Art & optimierter Audio-Pipeline!

Ein innovatives AI-gesteuertes Radio-System mit vollautomatisierter Broadcast-Generierung, das News sammelt, analysiert und in professionelle Audio-Shows mit embedded Cover-Art umwandelt.

## 🆕 **LATEST UPDATES (Juni 2025)**

### 🔧 **Environment Setup System**
- ✅ **Automatisches .env Setup** - intelligente Template-Generierung
- ✅ **23 Environment Variablen** vollständig erfasst & validiert
- ✅ **Smart Backup System** - sichere Reparatur bei fehlerhafter .env
- ✅ **Required vs Optional** - klare API Key Kategorisierung
- ✅ **Ein-Kommando Setup** - `./setup.sh` für sofortige Konfiguration

### 🎨 **Cover-Art Integration - DALL-E 3**
- ✅ **Automatische Cover-Generierung** für jede Show mit DALL-E 3
- ✅ **Zeitspezifische Themes** (Morgen/Mittag/Abend/Nacht-Designs)
- ✅ **MP3-Metadata-Embedding** mit ID3-Tags und Cover-Art
- ✅ **Swiss Design Principles** - professionelle 1024x1024 Cover

### 🗣️ **Audio-Optimierungen**
- ✅ **Marcel spricht reines Hochdeutsch** (keine Schweizerdeutsch-Wörter mehr)
- ✅ **Schnellere Voice-Settings** - beide Sprecher optimiert für Tempo
- ✅ **Automatisches Cleanup** - temporäre Dateien werden gelöscht
- ✅ **4-5 Min professionelle Broadcasts** mit natürlichen Dialogen

### 🚀 **Pipeline-Verbesserungen**
- ✅ **generate_audio_with_cover()** - Audio + Cover in einem Workflow
- ✅ **Robuste Error-Handling** - Cover optional, Audio immer verfügbar
- ✅ **Optimierte ffmpeg-Integration** für saubere Audio-Kombination

## 🎯 System-Überblick

RadioX ist ein vollständig automatisiertes Radio-System, das:
- **📊 News sammelt** von 22+ RSS-Feeds, Twitter und APIs (Wetter, Bitcoin)
- **🔄 Content analysiert** und intelligent verarbeitet mit GPT-4
- **🎭 Broadcasts generiert** mit natürlichen Hochdeutsch-Dialogen (Marcel & Jarvis)
- **🔊 Audio produziert** mit ElevenLabs (optimierte Voice-Settings)
- **🎨 Cover-Art erstellt** mit DALL-E 3 und automatischem MP3-Embedding
- **🗑️ Auto-Cleanup** - alle temporären Dateien automatisch gelöscht
- **📈 System überwacht** mit umfassendem Monitoring
- **🌐 Web-Interface** mit responsive Next.js Frontend

## 🏗️ Architektur

### Backend (Python + FastAPI)
```
backend/
├── radiox_master.py          # 🎛️ Master Control Script
├── src/services/             # 📦 Modulare Services
│   ├── data_collection_service.py      # 📊 Datensammlung (RSS, Twitter, APIs)
│   ├── content_processing_service.py   # 🔄 Content-Verarbeitung & Analyse
│   ├── broadcast_generation_service.py # 🎭 GPT-4 Broadcast-Generierung
│   ├── audio_generation_service.py     # 🔊 ElevenLabs Audio + Cover-Embedding
│   ├── image_generation_service.py     # 🎨 DALL-E 3 Cover-Art Generation
│   ├── system_monitoring_service.py    # 📈 System-Monitoring & Health
│   ├── rss_feed_manager.py            # 📰 RSS-Feed-Management
│   ├── weather_service.py             # 🌤️ Wetter-Daten (OpenWeatherMap)
│   ├── crypto_service.py              # ₿ Crypto-Preise (CoinMarketCap)
│   ├── twitter_service.py             # 🐦 Twitter/X-Integration
│   └── supabase_service.py            # 🗄️ Supabase-Datenbank
├── output/                   # 🎵 Generierte Content-Dateien
│   ├── audio/               # 🔊 Audio-Shows mit embedded Covers
│   │   └── RadioX_Broadcast_*.mp3   # 4-5MB finale Shows (128kbps)
│   ├── covers/              # 🎨 DALL-E 3 Cover-Art  
│   │   └── RadioX_Cover_*.png       # 1024x1024 zeitspezifische Designs
│   └── *.txt                # Broadcast-Info & Metadaten
├── requirements.txt          # 📋 Python Dependencies
└── env_template.txt         # ⚙️ Environment-Template
```

### Frontend (Next.js 14)
```
frontend/
├── app/                     # 🌐 Next.js App Router
│   ├── api/                 # 🔌 API Routes (Backend-Integration)
│   ├── layout.tsx           # 📱 App Layout & Theme Provider
│   └── page.tsx            # 🏠 Main Radio Interface
├── components/              # 🧩 React Components
│   ├── radio-app-fullscreen.tsx    # 🎙️ Haupt-Radio-Interface
│   ├── audio-visualizer-line.tsx   # 📊 Audio-Visualisierung
│   ├── startup-animation.tsx       # ⏳ Loading-Animation
│   ├── news-feed.tsx              # 📰 News-Dashboard
│   ├── api-info-modal.tsx         # ℹ️ System-Status-Modal
│   └── ui/                        # 🎨 UI-Komponenten (Shadcn/ui)
├── lib/                     # 🛠️ Utilities & Types
│   ├── utils.ts             # 🔧 Utility-Funktionen
│   └── types.ts            # 📝 TypeScript-Interfaces
├── styles/                  # 🎨 Global Styling
└── package.json            # 📦 NPM Dependencies
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# 🔧 Automatisches .env Setup (ZUERST!)
./setup.sh                # Intelligente .env Generierung
nano .env                 # API Keys eintragen (siehe 🔑 Abschnitt unten)
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # oder: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# 🧪 System testen
python cli_master.py status
```

### 3. Frontend Setup
```bash
cd frontend
npm install
# oder
pnpm install
```

### 4. System starten
```bash
# Backend (Terminal 1)
cd backend && source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### 5. Erste Broadcast generieren
```bash
cd backend && source venv/bin/activate
python radiox_master.py --action generate_broadcast --time 18:10
```

## 🎛️ Master Script - Vollständige Kommandos

Das `radiox_master.py` Script ist der zentrale Entry-Point für alle Operationen:

### Broadcast-Generierung
```bash
# 🎨🔊 Vollständigen Broadcast mit Audio + Cover-Art generieren
python radiox_master.py --action generate_broadcast --time 20:00 --channel zurich --generate-audio

# ⚡ Schneller Test-Broadcast (nur Script)
python radiox_master.py --action generate_broadcast --time 18:10 --news-count 3

# 🌅 Morgen-Edition mit zeitspezifischem Cover
python radiox_master.py --action generate_broadcast --time 08:00 --generate-audio

# 🌆 Abend-Edition mit golden-hour Theme
python radiox_master.py --action generate_broadcast --time 20:00 --generate-audio
```

### System-Management
```bash
# Alle Services auf Funktionalität testen
python radiox_master.py --action test_services

# System-Status und Gesundheits-Check
python radiox_master.py --action system_status

# News-Analyse ohne Broadcast-Generierung
python radiox_master.py --action analyze_news --max-age 2

# Alte Daten automatisch aufräumen
python radiox_master.py --action cleanup --cleanup-days 7
```

### Parameter-Referenz
- `--time HH:MM`: Zielzeit für zeitspezifische Stile (Morgen/Abend/Nacht)
- `--channel`: Radio-Kanal (zurich, basel, bern) - beeinflusst lokale News
- `--news-count N`: Anzahl News für Broadcast (Standard: 4)
- `--max-age N`: Maximales News-Alter in Stunden (Standard: 1)
- `--generate-audio`: Audio + Cover-Art mit ElevenLabs + DALL-E 3 generieren
- `--cleanup-days N`: Alter für automatisches Daten-Cleanup

## 📂 **Typischer Output**

Nach erfolgreicher Generierung erhältst du:

```
output/
├── audio/
│   └── RadioX_Broadcast_8cdf7643.mp3    # 4.5MB finale Show
└── covers/
    └── RadioX_Cover_8cdf7643_20250605_2000.png  # Zeitspezifisches Cover

✅ Features:
• 🗣️ Marcel: Fließendes Hochdeutsch (keine CH-Dialekt-Wörter)
• 🔊 4-5 Min professioneller Dialog zwischen Marcel & Jarvis  
• 🎨 Cover automatisch in MP3-Metadaten eingebettet
• 🗑️ Alle 30+ temporären Audio-Segmente automatisch gelöscht
• 📱 ID3-Tags: Titel, Artist, Album, Cover-Art für alle Player
```

## 🔧 Service-Architektur im Detail

### 📊 Data Collection Service
- **RSS-Feeds**: NZZ, 20min, Tagesanzeiger, ZüriToday
- **Twitter/X**: Live-Updates über Bearer Token
- **Wetter**: OpenWeatherMap für Zürich/Schweiz
- **Crypto**: CoinMarketCap für Bitcoin/Ethereum
- **Parallele Sammlung**: Async-basiert für Performance

### 🔄 Content Processing Service
- **News-Analyse**: GPT-4 basierte Kategorisierung
- **Duplikat-Erkennung**: Intelligente Content-Deduplication
- **Sentiment-Analyse**: Positive/Negative/Neutral-Klassifizierung
- **Themen-Balance**: Ausgewogene News-Auswahl
- **Lokalspezifische Filterung**: Zürich/Schweiz-Fokus

### 🎭 Broadcast Generation Service
- **GPT-4 Dialoge**: Natürliche Marcel & Jarvis Gespräche
- **Zeitspezifische Stile**: 
  - 🌅 **Morgen** (6-11h): Energisch, motivierend
  - ☀️ **Mittag** (12-17h): Entspannt, informativ  
  - 🌆 **Abend** (18-22h): Gemütlich, nachdenklich
  - 🌙 **Nacht** (23-5h): Ruhig, introspektiv
- **Schweizer Lokalkolorit**: Zürich-bezogene Inhalte
- **Structured Scripts**: JSON-Format für weitere Verarbeitung

### 🔊 Audio Generation Service
- **ElevenLabs TTS**: Hochqualitative deutsche Stimmen (optimierte Settings)
- **Sprecher-Profile**:
  - **Marcel**: Hauptmoderator, **reines Hochdeutsch**, warm (`owi9KfbgBi6A987h5eJH`)
    - Stability: 0.55 (schneller), Style: 0.45 (lebendiger)
  - **Jarvis**: AI-Co-Host, tech-fokussiert, analytisch (`dmLlPcdDHenQXbfM5tee`)
    - Stability: 0.60 (präziser), Style: 0.40 (schneller)
- **Audio-Quality**: 128kbps MP3, Web-optimiert, 4-5 Min Dauer
- **Auto-Processing**: Parallele Generierung + automatisches Cleanup
- **Cover-Integration**: Automatisches Embedding in MP3-Metadaten

### 🎨 Image Generation Service (DALL-E 3)
- **Intelligente Cover-Art**: Automatische Generierung basierend auf Inhalt & Zeit
- **Zeitspezifische Themes**:
  - 🌅 **Morgen** (6-11h): Sunrise-Farben, energetisch
  - ☀️ **Mittag** (12-17h): Professional blau/weiß
  - 🌆 **Abend** (18-22h): Golden hour, warme Töne  
  - 🌙 **Nacht** (23-5h): Dunkle blau/lila Atmosphäre
- **News-thematische Anpassung**: Politik, Crypto, Wetter, Tech-Themes
- **Swiss Design Principles**: Clean, minimal, professionell
- **MP3-Embedding**: Automatisches ID3-Tag-Integration mit mutagen
- **Format**: 1024x1024 PNG, optimiert für alle Devices

### 📈 System Monitoring Service
- **Performance-Metriken**: Response-Zeiten, Erfolgsraten
- **System-Health**: CPU, Memory, Disk-Usage
- **Error-Tracking**: Automatische Fehler-Protokollierung
- **Health-Score**: Gesamtsystem-Bewertung (0-100)
- **Alerting**: Automatische Warnungen bei kritischen Issues

## 🌐 Frontend Features - Vollständiges Radio-Interface

### 🎙️ Radio-Player
- **HTML5 Audio**: Native Browser-Unterstützung
- **Fullwidth Cover**: Responsive 1024x1024 Cover-Display
- **Audio-Controls**: Play/Pause, Volume, Progress-Bar
- **Real-time Metadata**: Titel, Dauer, File-Info
- **Auto-Loading**: Neueste Show automatisch geladen

### 📱 Responsive Design
- **Mobile-First**: Optimiert für alle Screen-Größen
- **Touch-Optimierung**: 44px+ Touch-Targets
- **Progressive Web App**: Installierbar, Offline-fähig
- **Performance**: < 2s Loading-Zeit, 95+ Lighthouse Score

### 🎨 UI/UX Design
- **Swiss Design Principles**: Clean, minimal, funktional
- **Dark Theme**: Slate-basiert mit Accent-Farben
- **Audio-Visualizer**: Live Waveform-Animation
- **Startup-Animation**: Professionelle Loading-Experience

### 📊 System-Dashboard
- **Live-Status**: Real-time System-Health-Monitoring
- **News-Feed**: Aktuelle Nachrichten-Übersicht
- **Broadcast-History**: Alle generierten Shows
- **API-Status**: Service-Verbindungen im Überblick

## 🔑 Environment-Konfiguration

### 🆕 **AUTOMATISCHES .ENV SETUP**

**RadioX verfügt über ein intelligentes Setup-System, das .env automatisch verwaltet:**

#### **⚡ Quick Setup**
```bash
# Automatisches .env Setup ausführen
./setup.sh
# oder direkt:
python3 setup_env.py
```

#### **🔧 Was passiert automatisch:**
- ✅ **Prüft .env Existenz** und Vollständigkeit
- ✅ **Analysiert fehlende API Keys** (Required vs Optional)
- ✅ **Erstellt Backup** bei Reparatur/Überschreibung
- ✅ **Kopiert .env.example** wenn .env leer/fehlerhaft
- ✅ **Validiert Setup** und gibt Status-Report
- ✅ **Zeigt nächste Schritte** an

#### **📋 Setup-Szenarien:**

| Situation | Aktion | Ergebnis |
|-----------|--------|----------|
| **Keine .env** | `./setup.sh` | Erstellt .env aus Template |
| **Leere .env** | `./setup.sh` | Überschreibt mit Template |
| **Unvollständige .env** | `./setup.sh` | Backup + Reparatur |
| **Vollständige .env** | `./setup.sh` | Validation Report |

#### **📍 Beispiel Setup-Output:**
```bash
🔧 RadioX Environment Setup
==================================================
📍 Aktuelle .env Status: ⚠️ 4 erforderliche Variable(n) fehlen
🔧 Repariere unvollständige .env Datei...
💾 Backup erstellt: .env.backup
✅ .env repariert!

📝 NÄCHSTE SCHRITTE:
1. Trage deine API Keys in .env ein
2. Teste mit: cd backend && python cli_master.py status
```

### 📍 **WICHTIG: .env Datei-Location**

**Die `.env` Datei MUSS im ROOT-Verzeichnis des Projekts liegen:**
```
RadioX/
├── .env                    ← 🔑 HIER LIEGT DIE .env DATEI! 
├── .env.example           ← 📋 Vollständiges Template
├── setup_env.py          ← 🔧 Automatisches Setup
├── setup.sh              ← ⚡ Setup-Alias
├── backend/               ← NICHT hier!
│   ├── radiox_master.py
│   └── src/...
└── frontend/
```

Das Settings-System lädt die .env automatisch aus dem Root-Verzeichnis:
```python
# Path in Settings-Klasse: 
env_file = Path(__file__).parent.parent.parent.parent / ".env"
# => RadioX/.env (nicht backend/.env!)
```

### 🎯 **Setup-Workflow Empfehlung:**

```bash
# 1. Repository klonen
git clone https://github.com/your-repo/RadioX.git
cd RadioX

# 2. Automatisches .env Setup
./setup.sh

# 3. API Keys eintragen (siehe .env Datei)
nano .env  # oder dein bevorzugter Editor

# 4. Backend Setup
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 5. System testen
python cli_master.py status
```

### Backend (.env im ROOT-Verzeichnis!)

Das automatische Setup erstellt eine vollständige .env mit **allen 23 Variablen**:

#### **🔑 ERFORDERLICHE API KEYS (6):**
```env
# 🗄️ DATABASE (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# 🤖 AI SERVICES (REQUIRED)
OPENAI_API_KEY=sk-your_openai_key             # GPT-4 + DALL-E 3
ELEVENLABS_API_KEY=your_elevenlabs_key        # Text-to-Speech

# 💰 DATA SOURCES (REQUIRED)
COINMARKETCAP_API_KEY=your_crypto_key         # Crypto-Preise
WEATHER_API_KEY=your_weather_key              # Wetter-Daten
```

#### **⚙️ OPTIONALE KONFIGURATION (17):**
```env
# 🎤 Voice-IDs (Optional - Fallback auf Default)
ELEVENLABS_MARCEL_VOICE_ID=owi9KfbgBi6A987h5eJH
ELEVENLABS_JARVIS_VOICE_ID=dmLlPcdDHenQXbfM5tee

# 🐦 Social Media APIs (Optional)
TWITTER_BEARER_TOKEN=your_twitter_token
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret

# X API (New Twitter API)
X_CLIENT_ID=your_x_client_id
X_CLIENT_SECRET=your_x_client_secret
X_BEARER_TOKEN=your_x_bearer_token
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_TOKEN_SECRET=your_x_access_secret

# 🌤️ Additional Weather
SRF_WEATHER_API_KEY=your_srf_key

# 🎵 Spotify Integration
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri

# ⚙️ System Configuration
SUPABASE_SERVICE_ROLE_KEY=your_service_key    # Enhanced DB Access
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false
```

#### **🎯 Minimale Konfiguration für Start:**
```bash
# Nur diese 6 Keys werden für Grundfunktionalität benötigt:
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
OPENAI_API_KEY=...
ELEVENLABS_API_KEY=...
COINMARKETCAP_API_KEY=...
WEATHER_API_KEY=...
```

### 🔗 **API Key Beschaffung - Schnell-Links**

| Service | Zweck | URL | Kosten |
|---------|-------|-----|--------|
| **🤖 OpenAI** | GPT-4 + DALL-E 3 | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | ~$0.50/Show |
| **🎤 ElevenLabs** | Text-to-Speech | [elevenlabs.io/app/speech-synthesis](https://elevenlabs.io/app/speech-synthesis) | ~$0.30/Show |
| **💰 CoinMarketCap** | Crypto-Daten | [coinmarketcap.com/api/](https://coinmarketcap.com/api/) | Kostenlos |
| **🌤️ OpenWeather** | Wetter-API | [openweathermap.org/api](https://openweathermap.org/api) | Kostenlos |
| **🗄️ Supabase** | Datenbank | [supabase.com/dashboard](https://supabase.com/dashboard) | Kostenlos |
| **🐦 Twitter/X** | Social Media | [developer.twitter.com](https://developer.twitter.com) | Optional |

#### **💰 Geschätzte Kosten pro Show:**
- **OpenAI GPT-4**: ~$0.30 (Script-Generierung)
- **OpenAI DALL-E 3**: ~$0.08 (Cover-Art)  
- **ElevenLabs TTS**: ~$0.25 (5-Min Audio)
- **Andere APIs**: Kostenlos
- **📊 Total**: ~$0.63 pro 5-Minuten Show

### Frontend (.env.local)
```env
# Supabase (für Frontend-Integration)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Backend API
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## 🔧 Environment Setup System im Detail

### 🏗️ **Setup-Manager Architektur**

Das `setup_env.py` System besteht aus mehreren intelligenten Komponenten:

#### **📋 Environment Variable Definition**
```python
@dataclass
class EnvVariable:
    name: str                    # Variable-Name
    required: bool              # Pflicht oder Optional?
    description: str            # Benutzer-freundliche Beschreibung
    category: str              # Kategorie (database, ai, voice, etc.)
```

#### **🔍 Intelligente Analyse-Engine**
```python
def _analyze_env_file(self) -> Dict[str, any]:
    """
    Analysiert .env Status:
    - Datei existiert?
    - Alle Required Keys vorhanden?
    - Placeholder-Werte ("your_key_here") entdeckt?
    - Empfohlene Aktion bestimmt
    """
```

### 🎯 **Setup-Modi im Detail**

#### **1. 🆕 CREATE MODE** 
**Situation:** Keine .env Datei vorhanden
```bash
📍 Status: ❌ .env Datei existiert nicht
🎯 Aktion: Erstelle .env aus .env.example
✅ Ergebnis: Vollständige .env mit allen 23 Variablen
```

#### **2. 🔧 REPAIR MODE**
**Situation:** .env unvollständig oder fehlerhaft
```bash
📍 Status: ⚠️ 4 erforderliche Variable(n) fehlen
🎯 Aktion: Backup + Überschreibung mit Template
💾 Backup: .env.backup erstellt
✅ Ergebnis: Reparierte .env mit allen Variablen
```

#### **3. ✅ VALIDATE MODE**
**Situation:** .env vollständig konfiguriert
```bash
📍 Status: ✅ .env vollständig (3 optionale fehlen)
🎯 Aktion: Validation Report
📊 Ergebnis: Status-Übersicht aller API Keys
```

### 🧰 **Technische Features**

#### **🔒 Backup-System**
```python
# Automatisches Backup vor jeder Änderung
backup_file = self.env_file.with_suffix('.env.backup')
shutil.copy2(self.env_file, backup_file)
```

#### **🔍 Smart Parsing**
```python
# Intelligentes .env Parsing
def _load_env_file(self) -> Dict[str, str]:
    env_vars = {}
    for line in f:
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
```

#### **✨ Template-Erkennung**
```python
# Erkennt Placeholder-Werte
if value and not value.startswith("your_"):
    status = "✅ Konfiguriert"
else:
    status = "❌ Placeholder"
```

### 📊 **Status-Reporting**

#### **API Key Kategorien:**
- 🗄️ **Database**: Supabase URLs & Keys
- 🤖 **AI Services**: OpenAI & ElevenLabs
- 💰 **Data Sources**: Crypto & Weather APIs
- 🐦 **Social Media**: Twitter/X Integration
- 🎤 **Voice Config**: Spezielle Voice-IDs
- 🎵 **Music**: Spotify Integration
- ⚙️ **System**: Logging & Debug-Settings

#### **Beispiel Validation Report:**
```bash
✅ .env Validierung:

🔑 ERFORDERLICHE API KEYS:
   ✅ SUPABASE_URL: Supabase Projekt URL
   ✅ SUPABASE_ANON_KEY: Supabase Anonymous Key
   ✅ OPENAI_API_KEY: OpenAI API Key für GPT-4 & DALL-E
   ✅ ELEVENLABS_API_KEY: ElevenLabs TTS
   ❌ COINMARKETCAP_API_KEY: CoinMarketCap Crypto-Daten
   ❌ WEATHER_API_KEY: Weather API Key

📊 OPTIONALE KEYS:
   ✅ 8/17 optionale Keys konfiguriert

⚠️ Erforderliche API Keys fehlen noch!
📝 Editiere .env und trage die fehlenden Werte ein.
```

### 🚀 **Integration mit CLI-System**

Das Setup-System ist vollständig in das Master-CLI integriert:

```bash
# Automatische .env Prüfung bei CLI-Start
cd backend && python cli_master.py status
# → Prüft .env automatisch vor Systemstart

# Setup-Validation in jedem Service
from config.settings import get_settings
settings = get_settings()  # Lädt und validiert .env automatisch
```

### 🔄 **Best Practices Workflow**

#### **Für Entwickler:**
```bash
# 1. Frisches Repository
git clone repository && cd RadioX

# 2. Einmalige Setup
./setup.sh

# 3. API Keys eintragen
nano .env

# 4. System testen
cd backend && python cli_master.py status
```

#### **Für CI/CD:**
```bash
# In GitHub Actions / CI Pipeline
- name: Setup Environment
  run: |
    python3 setup_env.py
    # Dann API Keys aus Secrets eintragen
```

#### **Für Team-Onboarding:**
```bash
# Neuer Entwickler bekommt:
1. git clone + cd RadioX
2. ./setup.sh
3. API Key-Liste zum Eintragen
4. python cli_master.py status → Ready!
```

### 🛠️ **Setup Troubleshooting**

#### **❓ Häufige Probleme & Lösungen**

| Problem | Lösung |
|---------|--------|
| `python command not found` | Verwende `python3 setup_env.py` |
| `Permission denied: ./setup.sh` | `chmod +x setup.sh` |
| `.env existiert aber API Keys fehlen` | `./setup.sh` repariert automatisch |
| `Setup läuft nicht` | Stelle sicher du bist im Root-Verzeichnis |
| `Backup-Datei überschrieben` | Backups heißen `.env.backup` |

#### **🔍 Debug-Modi:**
```bash
# Verbose Setup-Output
python3 setup_env.py  # Zeigt detaillierte Analyse

# Manual .env Check
python3 -c "from backend.src.config.settings import get_settings; get_settings()"

# CLI-System Status
cd backend && python cli_master.py status
```

#### **⚠️ Setup-System Limits:**
- ✅ **Unterstützt**: Standard .env Format
- ✅ **Backup**: Automatisch vor jeder Änderung
- ✅ **Validation**: Alle 23 Variablen
- ❌ **Nicht unterstützt**: Multi-line Values, komplexe Quoting

### 📚 **Ausführliche Setup-Dokumentation**

> **Für detaillierte Informationen zum Environment Setup System siehe: [SETUP.md](SETUP.md)**

Das SETUP.md enthält:
- 🏗️ **Technische Architektur** des Setup-Managers
- 🎯 **Alle Setup-Modi** im Detail (CREATE, REPAIR, VALIDATE)
- 🧰 **Advanced Features** & Troubleshooting
- 🚀 **CI/CD Integration** & Team-Workflows
- 📊 **Custom Usage** & API-Beispiele

## 🗄️ Datenbank-Schema (Supabase)

Das System verwendet PostgreSQL mit folgenden optimierten Tabellen:

```sql
-- Broadcast-Scripts (GPT-4 generierte Inhalte)
CREATE TABLE broadcast_scripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id VARCHAR(50) UNIQUE NOT NULL,
  script_content JSONB NOT NULL,
  persona VARCHAR(50) NOT NULL,
  broadcast_time TIME NOT NULL,
  estimated_duration INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- System-Monitoring & Logs
CREATE TABLE broadcast_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(100) NOT NULL,
  session_id VARCHAR(50),
  message TEXT NOT NULL,
  metadata JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- News-Deduplication
CREATE TABLE used_news (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  news_hash VARCHAR(64) UNIQUE NOT NULL,
  title TEXT NOT NULL,
  source VARCHAR(100) NOT NULL,
  used_at TIMESTAMP DEFAULT NOW()
);

-- RSS-Feed-Konfiguration
CREATE TABLE rss_feed_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  feed_url TEXT UNIQUE NOT NULL,
  feed_name VARCHAR(100) NOT NULL,
  priority INTEGER DEFAULT 1,
  active BOOLEAN DEFAULT true,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🎵 Audio-Pipeline im Detail

### 1. Script-Generierung (GPT-4)
```python
# Beispiel-Prompt für Abend-Edition
prompt = f"""Du bist ein professioneller Radio-Script-Writer für RadioX Zürich.

SPRECHER:
- MARCEL: Hauptmoderator aus Zürich, warm, entspannt, hochdeutsch
- JARVIS: AI-Co-Host, tech-fokussiert, analytisch, hochdeutsch

ABEND-STIMMUNG (18:00-22:00):
- Entspannter, ruhiger Ton
- Tages-Rückblick-Charakter
- Gemütliche Atmosphere

CONTENT:
{news_content}
{weather_info}
{bitcoin_info}

Erstelle ein 5-8 minütiges Abend-Radio-Script mit natürlichen Dialogen...
"""
```

### 2. Audio-Synthese (ElevenLabs)
```python
# Optimierte ElevenLabs-Settings
voice_settings = {
    "stability": 0.85,
    "similarity_boost": 0.95,
    "style": 0.1,
    "use_speaker_boost": True
}

# Batch-Generierung für Performance
segments = []
for speaker, text in script_segments:
    audio = generate_speech(
        text=text,
        voice=VOICE_IDS[speaker],
        model="eleven_multilingual_v2",
        voice_settings=voice_settings
    )
    segments.append(audio)
```

### 3. Audio-Post-Processing
```python
# PyDub-basierte Audio-Verarbeitung
from pydub import AudioSegment

final_audio = AudioSegment.empty()
for segment in segments:
    # Audio-Segment hinzufügen
    final_audio += AudioSegment.from_mp3(segment)
    # Kurze Pause zwischen Sprechern
    final_audio += AudioSegment.silent(duration=500)

# Export mit optimierten Settings
final_audio.export(
    "output.mp3", 
    format="mp3", 
    bitrate="128k",
    parameters=["-ar", "44100"]
)
```

## 🚀 Deployment & Production

### Backend (FastAPI)
```bash
# Lokal für Development
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mit Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js auf Vercel)
```bash
# Automatisches Deployment via Git
git push origin main
# → Vercel deployed automatisch

# Lokales Build-Testing
npm run build && npm start
```

### Docker-Container (Optional)
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Monitoring & Performance

### System-Metriken
- **Backend Response Time**: < 200ms für API-Calls
- **Audio Generation**: 30-60s pro Show (abhängig von Länge)
- **Cover Generation**: 10-30s pro DALL-E 3 Bild
- **Memory Usage**: < 512MB während Generierung
- **Database**: < 50ms Query-Response-Time

### Frontend-Performance
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3s
- **Lighthouse Performance**: 95+

### Audio-Qualität
- **Format**: MP3, 128kbps, 44.1kHz Stereo
- **Playback-Latenz**: < 100ms
- **Buffer-Health**: 5s Vorpufferung
- **Dropout-Rate**: < 0.1%

## 🔄 Content-Generierung Workflow

### Vollständiger Broadcast-Workflow
1. **📊 Data Collection** (10-30s)
   - RSS-Feeds parallel abfragen
   - Wetter & Crypto-Daten laden
   - Twitter-Updates sammeln

2. **🔄 Content Processing** (5-15s)
   - News kategorisieren & deduplizieren
   - Sentiment-Analyse durchführen
   - Themen-Balance optimieren

3. **🎭 Script Generation** (15-45s)
   - GPT-4 Dialog erstellen
   - Zeitspezifischen Stil anwenden
   - JSON-Structure generieren

4. **🔊 Audio Synthesis** (30-90s)
   - ElevenLabs TTS per Segment
   - Audio-Mixing & Concatenation
   - MP3-Export mit Metadaten

5. **🎨 Cover Creation** (10-30s)
   - DALL-E 3 Cover generieren
   - Metadata in MP3 integrieren
   - Files für Frontend bereitstellen

## 🛡️ Security & Privacy

### API-Security
- **Rate Limiting**: 100 Requests/Minute pro IP
- **Input Validation**: Alle User-Inputs sanitized
- **CORS**: Nur erlaubte Origins (localhost, Vercel)
- **Environment Variables**: Sensitive Daten nur in .env

### Data Privacy
- **No User Tracking**: Keine persönlichen Daten gespeichert
- **Anonymous Analytics**: Nur aggregierte Nutzungsstatistiken
- **GDPR Compliant**: EU-Datenschutz-konform
- **Local Storage**: Nur User-Preferences lokal gespeichert

## 🔧 Troubleshooting & Debug

### Häufige Probleme
```bash
# Backend startet nicht
cd backend && source venv/bin/activate
python -c "import src.main"  # Test imports

# Frontend zeigt keine Daten
curl http://localhost:8000/api/latest-broadcast  # Test Backend-API

# Audio spielt nicht ab
# → Prüfe CORS-Einstellungen und Audio-MIME-Types

# Supabase-Verbindung fehlschlägt
python radiox_master.py --action test_services  # Service-Tests
```

### Logging & Debugging
```python
# Backend-Logs (loguru)
from loguru import logger
logger.info("✅ System startup successful")
logger.error("❌ API call failed: {error}")

# Detaillierte Error-Infos in broadcast_logs Tabelle
```

## 🤝 Entwicklung & Contribution

### Code-Standards
- **Python**: Black-formatting, Type-hints, Docstrings
- **TypeScript**: Strict mode, ESLint, Prettier
- **Git**: Conventional Commits, Feature-Branches
- **Testing**: Unit-Tests für Services, E2E für Frontend

### Development-Workflow
1. Fork das Repository
2. Feature-Branch erstellen (`feature/neue-funktion`)
3. Code implementieren + Tests schreiben
4. Pull Request mit ausführlicher Beschreibung
5. Code-Review & Testing
6. Merge nach Approval

## 📄 Lizenz & Credits

**Lizenz**: MIT License - siehe [LICENSE](LICENSE)

**Entwickelt von**: Marcel Rapold  
**AI-Technologien**: OpenAI GPT-4, ElevenLabs, DALL-E 3  
**UI-Framework**: Next.js 14, Tailwind CSS, Shadcn/ui  
**Backend**: FastAPI, Supabase PostgreSQL  

## 🆘 Support & Community

### Support-Kanäle
1. **📖 Dokumentation**: Diese README + Code-Kommentare
2. **🔧 System-Tests**: `python radiox_master.py --action test_services`
3. **📋 GitHub Issues**: Bug-Reports & Feature-Requests
4. **💬 Discussions**: Fragen & Community-Austausch

### Quick-Diagnose
```bash
# Vollständiger System-Check
cd backend && source venv/bin/activate
python radiox_master.py --action system_status

# Einzelne Services testen
python radiox_master.py --action test_services

# Log-Files prüfen (falls vorhanden)
tail -f logs/radiox.log
```

---

**RadioX AI** - Wo künstliche Intelligenz auf professionelles Radio trifft 🎙️✨

*Vollständig automatisiert. Lokal entwickelt. Schweiz-fokussiert.*
