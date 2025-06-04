# 📻 RadioX API Documentation

Umfangreiche API-Dokumentation für das RadioX Radio Stations System.

## 📋 **Inhaltsverzeichnis**

1. [Stream Generator API](#stream-generator-api)
2. [Radio Stations API](#radio-stations-api)
3. [Content Services API](#content-services-api)
4. [Database Models](#database-models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Authentication](#authentication)

---

## 🎙️ **Stream Generator API**

### **StreamGenerator Class**

Haupt-Orchestrator für die komplette RadioX Stream-Generierung.

```python
from src.services.stream_generator import StreamGenerator
from src.models.radio_stations import RadioStationType

generator = StreamGenerator()
```

### **generate_stream()**

Generiert einen kompletten RadioX Stream für eine Radio Station.

```python
async def generate_stream(
    station_type: RadioStationType,
    template_name: Optional[str] = None,
    stream_id: Optional[str] = None,
    duration_minutes: int = 60
) -> Dict[str, Any]
```

**Parameter:**
- `station_type` (RadioStationType): Radio Station Typ
  - `BREAKING_NEWS` - Eilmeldungen und aktuelle Ereignisse
  - `BITCOIN_OG` - Bitcoin Maximalist Sender
  - `ZUERI_STYLE` - Lokaler Zürich-Fokus
  - `TRADFI_NEWS` - Traditionelle Finanz- und Wirtschaftsnachrichten
  - `TECH_INSIDER` - Technologie-News für Entwickler
  - `SWISS_LOCAL` - Schweiz-weite Nachrichten
- `template_name` (Optional[str]): Content-Template Override
  - `"bitcoin_focus"` - 50% Bitcoin, 25% Tech, 20% Wirtschaft
  - `"balanced_news"` - Ausgewogener Mix aller Kategorien
  - `"business_focus"` - 40% Wirtschaft, 30% Bitcoin, 20% Tech
  - `"swiss_local"` - Schweiz-fokussiert
- `stream_id` (Optional[str]): Eindeutige Stream-ID (auto-generiert wenn nicht angegeben)
- `duration_minutes` (int): Ziel-Dauer des Streams (Standard: 60)

**Response:**
```json
{
  "stream_id": "abc123",
  "station_id": "breaking_news",
  "station_name": "RadioX Breaking News",
  "status": "completed",
  "generated_at": "2024-01-15T10:30:00Z",
  "estimated_duration_minutes": 60,
  "total_segments": 12,
  "audio_files": [
    {
      "segment_id": "intro",
      "file_path": "/output/breaking_news_abc123_intro.mp3",
      "duration_seconds": 15,
      "voice_settings": {
        "voice_name": "JARVIS",
        "voice_id": "dmLlPcdDHenQXbfM5tee",
        "speed": 1.1,
        "stability": 0.7
      }
    }
  ],
  "station_config": {
    "station_id": "breaking_news",
    "display_name": "RadioX Breaking News",
    "tagline": "Immer aktuell, immer informiert",
    "tone": "professional",
    "energy_level": "high",
    "content_profile": {
      "weltpolitik": 35,
      "lokale_news_schweiz": 25,
      "wirtschaft": 20,
      "bitcoin": 10,
      "sport": 5,
      "technologie": 5
    }
  },
  "generation_pipeline": {
    "content_mixer": {
      "template": "balanced_news",
      "quality_score": 8.5,
      "total_items": 25,
      "categories_used": 6
    },
    "news_summarizer": {
      "segments_created": 12,
      "estimated_duration_seconds": 3600,
      "has_weather": true,
      "has_intro_jingle": true,
      "has_outro_jingle": true
    },
    "voice_generator": {
      "audio_files_created": 12,
      "total_duration_seconds": 3580,
      "voice_settings": {...}
    }
  },
  "ready_for_broadcast": true
}
```

**Beispiel:**
```python
# Breaking News Stream generieren
stream = await generator.generate_stream(
    station_type=RadioStationType.BREAKING_NEWS,
    duration_minutes=60
)

print(f"Stream generiert: {stream['stream_id']}")
print(f"Dauer: {stream['estimated_duration_minutes']} Minuten")
print(f"Audio-Dateien: {len(stream['audio_files'])}")
```

### **get_stream_preview()**

Erstellt eine Vorschau eines Streams ohne Audio-Generierung für schnelle Tests.

```python
async def get_stream_preview(
    station_type: RadioStationType,
    template_name: Optional[str] = None
) -> Dict[str, Any]
```

**Parameter:**
- `station_type` (RadioStationType): Radio Station Typ
- `template_name` (Optional[str]): Content-Template Override

**Response:**
```json
{
  "preview_id": "xyz789",
  "station_id": "bitcoin_og",
  "station_name": "RadioX Bitcoin",
  "template": "bitcoin_focus",
  "generated_at": "2024-01-15T10:30:00Z",
  "content_mix_summary": {
    "total_items": 18,
    "quality_score": 9.2,
    "categories": ["bitcoin", "wirtschaft", "technologie"]
  },
  "script_summary": {
    "total_segments": 10,
    "estimated_duration_seconds": 3420,
    "has_intro": true,
    "has_outro": true,
    "has_weather": false
  },
  "voice_segments": [
    {
      "segment_type": "intro_jingle",
      "text": "Stack sats, stay humble! RadioX Bitcoin mit den wichtigsten Bitcoin News",
      "estimated_duration": 8
    },
    {
      "segment_type": "news_summary",
      "text": "Bitcoin erreicht heute neue Höchststände...",
      "estimated_duration": 45
    }
  ],
  "station_config": {
    "tagline": "Stack Sats, Stay Humble",
    "tone": "energetic",
    "energy_level": "high",
    "voice_profile": {
      "voice_name": "Rachel",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "speed": 1.05
    }
  },
  "ready_for_audio_generation": true
}
```

### **generate_multiple_streams()**

Generiert mehrere Streams parallel für verschiedene Radio Stations.

```python
async def generate_multiple_streams(
    stations: List[RadioStationType],
    duration_minutes: int = 60
) -> Dict[str, Any]
```

**Parameter:**
- `stations` (List[RadioStationType]): Liste von Radio Station Typen
- `duration_minutes` (int): Ziel-Dauer pro Stream

**Response:**
```json
{
  "batch_id": "batch_456",
  "generated_at": "2024-01-15T10:30:00Z",
  "total_streams": 3,
  "successful_streams": 2,
  "failed_streams": 1,
  "streams": {
    "breaking_news": {...},
    "bitcoin_og": {...},
    "zueri_style": {"status": "failed", "error": "..."}
  },
  "summary": {
    "total_duration_minutes": 120,
    "total_audio_files": 24,
    "stations_generated": ["breaking_news", "bitcoin_og"]
  }
}
```

### **get_available_stations()**

Gibt alle verfügbaren Radio Stations zurück.

```python
def get_available_stations() -> List[Dict[str, Any]]
```

**Response:**
```json
[
  {
    "station_id": "breaking_news",
    "display_name": "RadioX Breaking News",
    "tagline": "Immer aktuell, immer informiert",
    "description": "Eilmeldungen und aktuelle Ereignisse",
    "target_audience": "News Junkies, Politiker, Journalisten",
    "tone": "professional",
    "energy_level": "high",
    "top_content": "weltpolitik (35%)",
    "voice_name": "JARVIS",
    "special_features": {
      "weather": true,
      "traffic": false,
      "bitcoin_price": false,
      "breaking_news": true
    }
  }
]
```

---

## 📻 **Radio Stations API**

### **RadioStationType Enum**

```python
class RadioStationType(str, Enum):
    BREAKING_NEWS = "breaking_news"
    ZUERI_STYLE = "zueri_style"
    BITCOIN_OG = "bitcoin_og"
    TRADFI_NEWS = "tradfi_news"
    TECH_INSIDER = "tech_insider"
    SWISS_LOCAL = "swiss_local"
```

### **Station Management Functions**

#### **get_station()**
```python
def get_station(station_type: RadioStationType) -> RadioStationConfig
```

Holt eine spezifische Radio Station Konfiguration.

#### **get_default_station()**
```python
def get_default_station() -> RadioStationConfig
```

Gibt die Standard-Radio Station zurück (Breaking News).

#### **list_stations()**
```python
def list_stations() -> List[RadioStationConfig]
```

Listet alle verfügbaren Radio Stations auf.

#### **get_station_by_id()**
```python
def get_station_by_id(station_id: str) -> Optional[RadioStationConfig]
```

Holt eine Radio Station anhand der ID.

#### **get_station_summary()**
```python
def get_station_summary() -> Dict[str, any]
```

Erstellt eine Übersicht aller Radio Stations.

**Response:**
```json
{
  "total_stations": 6,
  "default_station": "RadioX Breaking News",
  "stations": [
    {
      "id": "breaking_news",
      "name": "RadioX Breaking News",
      "tagline": "Immer aktuell, immer informiert",
      "target_audience": "News Junkies",
      "top_content": "weltpolitik (35%)",
      "tone": "professional",
      "energy": "high",
      "voice_name": "JARVIS",
      "special_features": ["Wetter", "Eilmeldungen"]
    }
  ]
}
```

### **Voice Profile Configuration**

```python
class VoiceProfile(BaseModel):
    voice_name: str
    voice_id: Optional[str] = None  # ElevenLabs Voice ID
    speed: float = 1.0              # 0.7 - 1.2
    stability: float = 0.5          # 0.0 - 1.0
    similarity_boost: float = 0.75  # 0.0 - 1.0
    style: float = 0.0              # 0.0 - 1.0
    use_speaker_boost: bool = True
```

**ElevenLabs Voice IDs:**
- **JARVIS**: `dmLlPcdDHenQXbfM5tee` (Breaking News)
- **Adam**: `pNInz6obpgDQGcFmaJgB` (Business)
- **Bella**: `EXAVITQu4vr4xnSDxMaL` (Züri, Tech, Schweiz)
- **Rachel**: `21m00Tcm4TlvDq8ikWAM` (Bitcoin)

### **Content Profile Configuration**

```python
class ContentProfile(BaseModel):
    bitcoin: int = 0
    wirtschaft: int = 0
    technologie: int = 0
    weltpolitik: int = 0
    sport: int = 0
    lokale_news_schweiz: int = 0
    wissenschaft: int = 0
    entertainment: int = 0
    
    def validate_total(self) -> bool:
        """Validiert dass Content-Mix 100% ergibt"""
        total = sum([
            self.bitcoin, self.wirtschaft, self.technologie,
            self.weltpolitik, self.sport, self.lokale_news_schweiz,
            self.wissenschaft, self.entertainment
        ])
        return total == 100
```

### **Voice Prompt Generation**

```python
def get_voice_prompt_for_station(station: RadioStationConfig) -> str
```

Generiert Voice-Prompt für ElevenLabs basierend auf Station.

**Beispiel-Prompts:**
- **Professional**: "Sprechen Sie als professioneller Nachrichtensprecher für RadioX Breaking News. Klar, autoritativ und vertrauenswürdig."
- **Energetic**: "Sprechen Sie mit Energie und Begeisterung für RadioX Bitcoin. Dynamisch und mitreißend."
- **Casual**: "Sprechen Sie freundlich und entspannt für RadioX Züri. Natürlich und zugänglich."

---

## 🔧 **Content Services API**

### **ContentMixer Class**

```python
from src.services.content_mixer import ContentMixer

mixer = ContentMixer()
```

#### **create_comprehensive_content_mix()**

```python
async def create_comprehensive_content_mix(
    stream_template: str,
    target_duration_minutes: int = 60
) -> Dict[str, Any]
```

### **NewsSummarizer Class**

```python
from src.services.news_summarizer import NewsSummarizer

summarizer = NewsSummarizer()
```

#### **create_radio_script()**

```python
async def create_radio_script(
    content_mix: Dict[str, Any],
    station_config: RadioStationConfig
) -> Dict[str, Any]
```

### **VoiceGenerator Class**

```python
from src.services.voice_generator import VoiceGenerator

voice_gen = VoiceGenerator()
```

#### **generate_complete_stream()**

```python
async def generate_complete_stream(
    radio_script: Dict[str, Any],
    station_config: RadioStationConfig,
    stream_id: str
) -> Dict[str, Any]
```

---

## 🗄️ **Database Models**

### **Supabase Tables**

#### **radio_stations**
```sql
CREATE TABLE radio_stations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    station_id VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    tagline VARCHAR(200),
    target_audience TEXT,
    
    -- Voice Profile
    voice_name VARCHAR(100),
    voice_id VARCHAR(100),
    voice_speed DECIMAL(3,2) DEFAULT 1.0,
    voice_stability DECIMAL(3,2) DEFAULT 0.5,
    voice_similarity_boost DECIMAL(3,2) DEFAULT 0.75,
    voice_style DECIMAL(3,2) DEFAULT 0.0,
    voice_speaker_boost BOOLEAN DEFAULT true,
    
    -- Content Profile (Prozent)
    content_bitcoin INTEGER DEFAULT 0,
    content_wirtschaft INTEGER DEFAULT 0,
    content_technologie INTEGER DEFAULT 0,
    content_weltpolitik INTEGER DEFAULT 0,
    content_sport INTEGER DEFAULT 0,
    content_lokale_news INTEGER DEFAULT 0,
    content_wissenschaft INTEGER DEFAULT 0,
    content_entertainment INTEGER DEFAULT 0,
    
    -- Tonalität & Stil
    tone VARCHAR(50),
    energy_level VARCHAR(50),
    formality VARCHAR(50),
    
    -- Radio-spezifische Einstellungen
    intro_jingle TEXT,
    outro_jingle TEXT,
    news_format VARCHAR(50),
    segment_style VARCHAR(50),
    
    -- Musik & Audio
    music_genres JSONB,
    audio_branding VARCHAR(50),
    
    -- Features
    weather_updates BOOLEAN DEFAULT false,
    traffic_updates BOOLEAN DEFAULT false,
    bitcoin_price_updates BOOLEAN DEFAULT false,
    breaking_news_priority BOOLEAN DEFAULT false,
    
    -- Meta
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **streams**
```sql
CREATE TABLE streams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stream_id VARCHAR(50) UNIQUE NOT NULL,
    station_id VARCHAR(50) REFERENCES radio_stations(station_id),
    template_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    
    -- Stream Metadaten
    duration_minutes INTEGER,
    total_segments INTEGER,
    estimated_duration_seconds INTEGER,
    
    -- Generation Pipeline
    content_mix_data JSONB,
    radio_script_data JSONB,
    voice_generation_data JSONB,
    
    -- Audio Files
    audio_files JSONB,
    
    -- Timestamps
    generated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Quality Metrics
    quality_score DECIMAL(3,2),
    content_freshness_score DECIMAL(3,2)
);
```

#### **content_categories**
```sql
CREATE TABLE content_categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category_id VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    emoji VARCHAR(10),
    color_hex VARCHAR(7),
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0
);
```

---

## ⚠️ **Error Handling**

### **Standard Error Response**

```json
{
  "status": "failed",
  "error": "Detailed error message",
  "error_code": "STREAM_GENERATION_FAILED",
  "timestamp": "2024-01-15T10:30:00Z",
  "phases_completed": ["content_mix", "radio_script"],
  "retry_possible": true
}
```

### **Error Codes**

- `CONTENT_MIX_FAILED` - Content-Mix Erstellung fehlgeschlagen
- `NEWS_SUMMARIZER_FAILED` - GPT-4 Summarization fehlgeschlagen
- `VOICE_GENERATION_FAILED` - ElevenLabs TTS fehlgeschlagen
- `AUDIO_MIX_FAILED` - Audio-Mixing fehlgeschlagen
- `STATION_NOT_FOUND` - Radio Station nicht gefunden
- `INVALID_CONTENT_PROFILE` - Content-Profil ungültig (nicht 100%)
- `API_RATE_LIMIT` - API Rate Limit erreicht
- `INSUFFICIENT_CONTENT` - Nicht genügend Content verfügbar

### **Exception Handling**

```python
try:
    stream = await generator.generate_stream(
        station_type=RadioStationType.BREAKING_NEWS
    )
except ContentMixError as e:
    print(f"Content-Mix Fehler: {e}")
except VoiceGenerationError as e:
    print(f"Voice-Generation Fehler: {e}")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
```

---

## 🚦 **Rate Limiting**

### **API Limits**

- **ElevenLabs**: 1000 Zeichen/Minute (abhängig vom Plan)
- **OpenAI GPT-4**: 10,000 Tokens/Minute
- **Spotify**: 100 Requests/Minute
- **Twitter/X**: 300 Requests/15min

### **Internal Rate Limiting**

```python
# Stream Generator verwendet Semaphore für parallele Streams
semaphore = asyncio.Semaphore(2)  # Max 2 gleichzeitige Streams

# Retry-Logic mit exponential backoff
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def api_call_with_retry():
    # API Call
    pass
```

---

## 🔐 **Authentication**

### **Environment Variables**

```env
# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# Spotify
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Twitter/X
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

### **API Key Validation**

```python
from config.settings import get_settings

settings = get_settings()

# Automatische Validierung beim Start
if not settings.elevenlabs_api_key:
    raise ValueError("ElevenLabs API Key fehlt")
```

---

## 📊 **Performance Metrics**

### **Stream Generation Metrics**

```json
{
  "generation_time_seconds": 45.2,
  "content_mix_time": 12.1,
  "summarization_time": 18.7,
  "voice_generation_time": 14.4,
  "api_calls": {
    "elevenlabs": 12,
    "openai": 3,
    "spotify": 5
  },
  "quality_scores": {
    "content_relevance": 8.5,
    "voice_quality": 9.2,
    "overall": 8.8
  }
}
```

---

## 🧪 **Testing**

### **Unit Tests**

```python
import pytest
from src.services.stream_generator import StreamGenerator
from src.models.radio_stations import RadioStationType

@pytest.mark.asyncio
async def test_stream_generation():
    generator = StreamGenerator()
    
    stream = await generator.generate_stream(
        station_type=RadioStationType.BREAKING_NEWS,
        duration_minutes=30
    )
    
    assert stream["status"] == "completed"
    assert stream["estimated_duration_minutes"] == 30
    assert len(stream["audio_files"]) > 0
```

### **Integration Tests**

```python
@pytest.mark.asyncio
async def test_full_pipeline():
    # Test komplette Pipeline von Content-Mix bis Audio
    pass
```

---

## 📚 **Code Examples**

### **Einfacher Stream**

```python
from src.services.stream_generator import StreamGenerator
from src.models.radio_stations import RadioStationType

async def generate_breaking_news():
    generator = StreamGenerator()
    
    stream = await generator.generate_stream(
        station_type=RadioStationType.BREAKING_NEWS,
        duration_minutes=60
    )
    
    print(f"Stream ID: {stream['stream_id']}")
    print(f"Audio-Dateien: {len(stream['audio_files'])}")
    
    return stream

# Verwendung
stream = await generate_breaking_news()
```

### **Batch-Generierung**

```python
async def generate_all_stations():
    generator = StreamGenerator()
    
    stations = [
        RadioStationType.BREAKING_NEWS,
        RadioStationType.BITCOIN_OG,
        RadioStationType.ZUERI_STYLE
    ]
    
    batch = await generator.generate_multiple_streams(
        stations=stations,
        duration_minutes=30
    )
    
    print(f"Batch ID: {batch['batch_id']}")
    print(f"Erfolgreiche Streams: {batch['successful_streams']}")
    
    return batch
```

### **Station-Konfiguration**

```python
from src.models.radio_stations import get_station, RadioStationType

def explore_station():
    station = get_station(RadioStationType.BREAKING_NEWS)
    
    print(f"Station: {station.display_name}")
    print(f"Tagline: {station.tagline}")
    print(f"Voice: {station.voice_profile.voice_name}")
    print(f"Content-Mix: {station.content_profile.dict()}")
    
    return station
```

---

**RadioX API Documentation** - *Complete Reference Guide* 📻✨ 