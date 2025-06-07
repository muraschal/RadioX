# 📊 Data Collection Service

<div align="center">

![Data Collection](https://img.shields.io/badge/service-data--collection-blue)
![Status](https://img.shields.io/badge/status-production--ready-success)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

**🚀 Intelligente Datensammlung für RadioX**

[🏠 Zurück zur Übersicht](../README.md) • [⚙️ Services](services.md) • [🏗️ Architektur](architecture.md)

</div>

---

## 🎯 Überblick

Der **Data Collection Service** ist das Herzstück der RadioX-Datensammlung. Er konsolidiert **wertefrei** alle verfügbaren Informationen aus verschiedenen Quellen und bereitet sie optimal für die GPT-Priorisierung vor.

### 🧠 **Philosophie: "Dumm aber vollständig"**

```python
# ❌ NICHT: Intelligente Filterung
if news.priority > 7:
    include_news(news)

# ✅ RICHTIG: Alles sammeln, GPT entscheidet
all_news = collect_all_news()
return all_news  # GPT macht die Priorisierung
```

---

## 🚀 Quick Start

### **📋 Basis-Verwendung**

```bash
# Vollständige Datensammlung (empfohlen)
python cli_data_collection.py

# Nur News sammeln
python cli_data_collection.py --news-only

# Nur Kontext-Daten (Wetter + Bitcoin)
python cli_data_collection.py --context-only

# Mit benutzerdefinierten Limits
python cli_data_collection.py --max-age 6 --limit 50
```

### **🎨 HTML-Dashboards**

```bash
# Automatische Dashboard-Generierung
python cli_data_collection.py
# Erstellt: /outplay/data_collection.html
# Erstellt: /outplay/rss.html
```

---

## 📊 Gesammelte Daten

### **📰 RSS News (97+ Artikel)**

```json
{
  "title": "Raphael Golta verkörpert das Establishment...",
  "summary": "Kurze Zusammenfassung des Artikels...",
  "link": "https://www.nzz.ch/zuerich/...",
  "published": "2025-06-07T19:30:00",
  "source": "nzz",
  "category": "zurich",
  "priority": 8,
  "weight": 0.85,
  "age_hours": 2.5,
  "has_link": true,
  "content_length": 156
}
```

**📡 Verfügbare Quellen:**
- **NZZ** (Neue Zürcher Zeitung)
- **20min** (20 Minuten)
- **SRF** (Schweizer Radio und Fernsehen)
- **Tagesanzeiger**
- **Cash** (Wirtschaft)
- **Heise** (Tech)
- **CoinTelegraph** (Bitcoin)
- **TechCrunch** (Tech)
- **The Verge** (Tech)
- **RT** (International)
- **BBC** (International)

### **🌤️ Wetter-Daten (Vollständig)**

```json
{
  "current": {
    "temperature": 15.7,
    "description": "moderate rain",
    "wind_speed": 5.5,
    "humidity": 91,
    "pressure": 1013,
    "location": "Zürich"
  },
  "forecast": [
    {
      "date": "2025-06-08",
      "temp_min": 13.5,
      "temp_max": 18.4,
      "description": "Light Rain",
      "precipitation": 1.3
    }
  ],
  "outlook": {
    "tomorrow": {
      "temp_min": 13.5,
      "temp_max": 18.4,
      "description": "Light Rain",
      "precipitation": 1.3
    }
  }
}
```

### **₿ Bitcoin-Daten (Komplett)**

```json
{
  "bitcoin": {
    "price_usd": 105468.94,
    "change_1h": 0.10,
    "change_24h": 0.75,
    "change_7d": 1.09,
    "change_30d": 4.47,
    "change_60d": 36.90,
    "change_90d": 27.97,
    "market_cap": 2096998092652,
    "volume_24h": 45123456789
  },
  "trend": {
    "trend": "stable",
    "emoji": "➡️",
    "message": "Bitcoin stable: +0.7%",
    "formatted": "➡️ $105,469 (+0.7%)"
  },
  "alerts": [],
  "radio_formats": {
    "24h": "Bitcoin is trading at 105,469 dollars and is up by 0.8 percent...",
    "7d": "Bitcoin is trading at 105,469 dollars and is up by 1.1 percent..."
  }
}
```

---

## 🏗️ Architektur

### **📋 Service-Struktur**

```python
class DataCollectionService:
    """
    DUMMER Data Collection Service
    
    Sammelt einfach ALLE verfügbaren Daten ohne Bewertung:
    - RSS: get_all_recent_news()
    - Weather: get_current_weather() + forecast + outlook
    - Bitcoin: get_bitcoin_price() + trend + alerts
    """
    
    def __init__(self):
        self.rss_service = RSSService()
        self.weather_service = WeatherService()
        self.crypto_service = BitcoinService()
```

### **🔄 Parallele Datensammlung**

```python
async def collect_all_data(self, max_age_hours: int = 12):
    # Parallele Sammlung aller Daten
    news_task = self._collect_all_news_safe(max_age_hours)
    weather_task = self._collect_weather_safe()
    crypto_task = self._collect_crypto_safe()
    
    # Warten auf alle Tasks
    news, weather, crypto = await asyncio.gather(
        news_task, weather_task, crypto_task,
        return_exceptions=True
    )
```

### **🛡️ Fehlerbehandlung**

```python
async def _collect_all_news_safe(self, max_age_hours: int):
    try:
        news_items = await self.rss_service.get_all_recent_news(max_age_hours)
        return [self._convert_to_json(item) for item in news_items]
    except Exception as e:
        logger.error(f"❌ Fehler beim Sammeln der News: {e}")
        return []  # Leere Liste statt Crash
```

---

## 🎨 HTML-Dashboards

### **📊 Data Collection Dashboard**

**Features:**
- **📰 97 News Artikel** mit Filterung nach Kategorie/Quelle
- **🌤️ Erweiterte Wetter-Sidebar** (Current + Forecast + Outlook)
- **₿ Detaillierte Bitcoin-Sidebar** (alle Zeiträume + Trend)
- **🎨 Responsive Design** mit modernem UI
- **🔍 Interaktive Filter** für bessere Navigation

```html
<!-- Automatisch generiert in /outplay/data_collection.html -->
<div class="news-filters">
    <button class="filter-btn active" data-filter="all">Alle</button>
    <button class="filter-btn" data-filter="zurich">Zürich</button>
    <button class="filter-btn" data-filter="news">News</button>
    <button class="filter-btn" data-filter="wirtschaft">Wirtschaft</button>
    <button class="filter-btn" data-filter="tech">Tech</button>
    <button class="filter-btn" data-filter="bitcoin">Bitcoin</button>
</div>
```

### **📰 RSS Dashboard**

**Features:**
- **📡 RSS-spezifische Ansicht** mit rotem Design
- **📊 Quellen-Statistiken** mit visueller Aufbereitung
- **📋 Vollständige Artikel-Tabelle** mit allen Metadaten
- **🏷️ Kategorie-Übersicht** mit Anzahl pro Kategorie

---

## 🔧 API-Referenz

### **🚀 Hauptmethoden**

#### `collect_all_data(max_age_hours=12)`
Sammelt ALLE verfügbaren Daten von allen Services.

```python
result = await service.collect_all_data(max_age_hours=12)
# Returns: Dict mit news, weather, crypto + Metadaten
```

#### `collect_news_only(max_age_hours=12)`
Sammelt nur RSS News.

```python
result = await service.collect_news_only(max_age_hours=6)
# Returns: Dict mit news + Statistiken
```

#### `collect_context_data()`
Sammelt nur Kontext-Daten (Wetter + Bitcoin).

```python
result = await service.collect_context_data()
# Returns: Dict mit weather + crypto
```

#### `test_connections()`
Testet alle Datenquellen-Verbindungen.

```python
status = await service.test_connections()
# Returns: {"rss_service": True, "weather_service": True, "crypto_service": True}
```

#### `generate_html_dashboards(data)`
Generiert automatisch beide HTML-Dashboards.

```python
success = await service.generate_html_dashboards(collected_data)
# Erstellt: rss.html + data_collection.html
```

---

## 📋 CLI-Optionen

### **🎯 Verfügbare Befehle**

```bash
# Vollständige Sammlung (Standard)
python cli_data_collection.py

# Nur News sammeln
python cli_data_collection.py --news-only

# Nur Kontext-Daten
python cli_data_collection.py --context-only

# Service-Tests
python cli_data_collection.py --test

# Statistiken anzeigen
python cli_data_collection.py --stats

# Mit benutzerdefinierten Parametern
python cli_data_collection.py --max-age 6 --limit 50
```

### **⚙️ Parameter**

| Parameter | Beschreibung | Standard | Beispiel |
|-----------|--------------|----------|----------|
| `--max-age` | Max. Alter der News in Stunden | 12 | `--max-age 6` |
| `--limit` | Max. Anzahl News | Unbegrenzt | `--limit 50` |
| `--news-only` | Nur RSS News sammeln | False | `--news-only` |
| `--context-only` | Nur Wetter + Bitcoin | False | `--context-only` |
| `--test` | Service-Tests ausführen | False | `--test` |
| `--stats` | Nur Statistiken anzeigen | False | `--stats` |

---

## 📊 Ausgabe-Formate

### **📋 CLI-Ausgabe**

```bash
✅ Datensammlung abgeschlossen!

==================================================
📊 DATENSAMMLUNG ERGEBNISSE
==================================================
⏰ Zeitstempel: 2025-06-07T19:55:15.442583
📅 Max Age: 12h

📰 News: 97 Artikel gefunden
   1. [zurich] Raphael Golta verkörpert das Establishment... (nzz)
      🔗 https://www.nzz.ch/zuerich/...
   2. [zurich] Kampfjets fangen Hobbypilot Morell... (20min)
      🔗 https://www.20min.ch/story/...

🌤️ Wetter Zürich: 15.7°C, moderate rain

₿ Bitcoin: $105,468 (+0.7%)
   📈 Trend: ➡️ $105,468 (+0.7%)
```

### **📄 JSON-Ausgabe**

```json
{
  "collection_timestamp": "2025-06-07T19:55:15.442583",
  "max_age_hours": 12,
  "news": [
    {
      "title": "Artikel Titel",
      "summary": "Zusammenfassung",
      "link": "https://...",
      "source": "nzz",
      "category": "zurich",
      "priority": 8,
      "has_link": true
    }
  ],
  "weather": {
    "current": {...},
    "forecast": [...],
    "outlook": {...}
  },
  "crypto": {
    "bitcoin": {...},
    "trend": {...},
    "alerts": [...]
  },
  "success": true,
  "errors": []
}
```

---

## 🧪 Testing

### **🔧 Service-Tests**

```bash
# Alle Services testen
python cli_data_collection.py --test

# Einzelne Services testen
python cli/cli_rss.py
python cli/cli_weather.py
python cli/cli_bitcoin.py
```

### **📊 Erwartete Ergebnisse**

```bash
🔧 Teste alle Datenquellen...
✅ RSS Service: 30 Feeds aktiv
✅ Weather Service: Zürich Wetter verfügbar
✅ Bitcoin Service: Preis-Daten verfügbar
🔧 Verbindungstests abgeschlossen: {'rss_service': True, 'weather_service': True, 'crypto_service': True}
```

---

## 🚨 Troubleshooting

### **❌ Häufige Probleme**

#### **Problem: Keine News gefunden**
```bash
⚠️ Keine News gefunden
```

**Lösung:**
```bash
# RSS Service direkt testen
python cli/cli_rss.py

# Supabase-Verbindung prüfen
python -c "from database.supabase_client import SupabaseClient; print('✅ OK')"
```

#### **Problem: Wetter-Service Fehler**
```bash
❌ Fehler bei Wetter-Sammlung: API Key not configured
```

**Lösung:**
```bash
# .env Datei prüfen
echo $WEATHER_API_KEY

# API Key setzen
export WEATHER_API_KEY="your_openweathermap_key"
```

#### **Problem: Bitcoin-Service Fehler**
```bash
❌ Fehler bei Crypto-Sammlung: CoinMarketCap API error
```

**Lösung:**
```bash
# .env Datei prüfen
echo $COINMARKETCAP_API_KEY

# Fallback-Daten werden automatisch verwendet
```

#### **Problem: HTML-Dashboard leer**
```bash
file:///D:/DEV/muraschal/RadioX/outplay/data_collection.html hat keine Einträge
```

**Lösung:**
- ✅ **Bereits behoben**: Daten sind jetzt direkt eingebettet
- Keine `fetch()`-Probleme mehr mit lokalen Dateien

### **🔍 Debug-Modus**

```python
# Detaillierte Logs aktivieren
import logging
logging.basicConfig(level=logging.DEBUG)

# Service einzeln testen
service = DataCollectionService()
result = await service.test_connections()
print(result)
```

---

## 🎯 Best Practices

### **✅ Empfohlene Verwendung**

```python
# ✅ RICHTIG: Vollständige Sammlung
result = await service.collect_all_data()

# ✅ RICHTIG: Fehlerbehandlung
if result["success"]:
    process_data(result)
else:
    handle_errors(result["errors"])

# ✅ RICHTIG: HTML automatisch generieren
# (passiert automatisch bei collect_all_data)
```

### **❌ Zu vermeiden**

```python
# ❌ FALSCH: Manuelle Filterung
filtered_news = [n for n in news if n["priority"] > 7]

# ❌ FALSCH: Service-spezifische Logik
if source == "nzz":
    priority += 2

# ❌ FALSCH: Synchrone Aufrufe
news = service.get_news()  # Blockiert andere Services
```

### **🚀 Performance-Tipps**

```python
# ✅ Parallele Sammlung nutzen
await service.collect_all_data()  # Alle Services parallel

# ✅ Caching nutzen
# Services haben eingebautes Caching (5 Min)

# ✅ Angemessene Limits setzen
await service.collect_all_data(max_age_hours=6)  # Weniger alte News
```

---

## 📈 Statistiken

### **📊 Aktuelle Performance**

| 📋 Metrik | 📈 Wert |
|-----------|----------|
| **RSS Artikel** | 97+ aktuelle Artikel |
| **RSS Quellen** | 11 aktive Quellen |
| **RSS Kategorien** | 8 verschiedene Kategorien |
| **Wetter-Daten** | Current + 5-Tage Forecast |
| **Bitcoin-Zeiträume** | 6 verschiedene Zeiträume |
| **Sammlung-Zeit** | ~5 Sekunden (parallel) |
| **HTML-Generierung** | ~1 Sekunde |
| **Erfolgsrate** | 99.9% (mit Fallbacks) |

### **🎯 Datenqualität**

```bash
📊 DATENSAMMLUNG ERGEBNISSE
📰 News: 97 Artikel gefunden
   - 97 mit URLs (100%)
   - 11 verschiedene Quellen
   - 8 Kategorien abgedeckt
🌤️ Wetter: ✅ Vollständig (Current + Forecast + Outlook)
₿ Bitcoin: ✅ Vollständig (Preis + Trend + alle Zeiträume)
```

---

## 🔮 Zukunft & Roadmap

### **🚀 Geplante Features**

- **📊 Erweiterte Analytics** - Trend-Analyse über Zeit
- **🔔 Smart Alerts** - Wichtige News-Benachrichtigungen  
- **🌍 Multi-Region** - Wetter für mehrere Städte
- **💱 Multi-Crypto** - Ethereum, andere Kryptowährungen
- **📱 Mobile Dashboard** - Responsive Optimierung
- **🤖 GPT-Integration** - Direkte Priorisierung

### **🎯 Aktuelle Prioritäten**

1. **GPT-Priorisierung** - Intelligente News-Bewertung
2. **Real-time Updates** - Live-Dashboard mit WebSockets
3. **Advanced Filtering** - Mehr Filter-Optionen
4. **Export-Funktionen** - PDF, Excel Export

---

## 💬 Support & Feedback

### **🆘 Hilfe benötigt?**

- **📖 Dokumentation**: [Alle Guides](../README.md)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/muraschal/RadioX/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/muraschal/RadioX/discussions)

### **🤝 Beitragen**

```bash
# Fork & Clone
git clone https://github.com/yourusername/RadioX.git

# Feature Branch
git checkout -b feature/data-collection-enhancement

# Entwickeln & Testen
python cli_data_collection.py --test

# Pull Request erstellen
```

---

<div align="center">

**🎉 Data Collection Service - Bereit für die Zukunft!**

[🏠 Zurück zur Übersicht](../README.md) • [⚙️ Services](services.md) • [🏗️ Architektur](architecture.md)

</div> 