# RadioX Environment Setup System

> **🔧 Intelligentes .env Management für RadioX**

Automatisches Setup und Validierung der Environment-Konfiguration mit Smart Backup, Template-Generierung und umfassender Validation.

## 🚀 Quick Start

```bash
# 1. Automatisches Setup ausführen
./setup.sh

# 2. API Keys eintragen in .env
nano .env

# 3. System testen
cd backend && python cli_master.py status
```

## 📋 Übersicht

### **Was macht das Setup-System?**

- ✅ **Prüft .env Existenz** und Vollständigkeit  
- ✅ **Analysiert fehlende API Keys** (Required vs Optional)
- ✅ **Erstellt automatisch Backups** vor jeder Änderung
- ✅ **Generiert .env aus Template** wenn leer/fehlerhaft
- ✅ **Validiert alle 23 Variablen** basierend auf Settings-Klasse
- ✅ **Gibt hilfreiche Reports** und nächste Schritte aus

### **Unterstützte Szenarien:**

| Situation | Setup Action | Ergebnis |
|-----------|--------------|----------|
| **Keine .env** | CREATE | Template kopiert |
| **Leere .env** | CREATE | Mit Template überschrieben |
| **Unvollständige .env** | REPAIR | Backup + Template |
| **Vollständige .env** | VALIDATE | Status-Report |

## 🏗️ Architektur

### **Komponenten:**

```
RadioX/
├── setup_env.py          # 🧠 Intelligenter Setup-Manager
├── setup.sh              # ⚡ Shell-Alias für einfache Verwendung
├── .env.example           # 📋 Vollständiges Template (23 Variablen)
├── .env                   # 🔑 Deine aktuelle Konfiguration
└── .env.backup           # 💾 Automatische Backups
```

### **Setup-Manager Klassen:**

```python
@dataclass
class EnvVariable:
    name: str              # OPENAI_API_KEY
    required: bool         # True/False
    description: str       # "OpenAI API Key für GPT-4 & DALL-E"
    category: str         # "ai", "database", "social", etc.

class EnvSetupManager:
    def setup_env()        # Hauptfunktion
    def _analyze_env_file() # Status-Analyse
    def _create_env_from_example() # Template-Copy
    def _repair_env_file() # Backup + Reparatur
    def _validate_and_report() # Validation Report
```

## 📊 Environment Variablen

### **🔑 ERFORDERLICHE KEYS (6):**

| Variable | Service | Zweck |
|----------|---------|-------|
| `SUPABASE_URL` | Supabase | Datenbank-Verbindung |
| `SUPABASE_ANON_KEY` | Supabase | Database Access |
| `OPENAI_API_KEY` | OpenAI | GPT-4 + DALL-E 3 |
| `ELEVENLABS_API_KEY` | ElevenLabs | Text-to-Speech |
| `COINMARKETCAP_API_KEY` | CoinMarketCap | Crypto-Daten |
| `WEATHER_API_KEY` | OpenWeather | Wetter-Daten |

### **⚙️ OPTIONALE KEYS (17):**

#### **🎤 Voice Configuration:**
- `ELEVENLABS_MARCEL_VOICE_ID` - Marcel Voice-ID
- `ELEVENLABS_JARVIS_VOICE_ID` - Jarvis Voice-ID  

#### **🐦 Social Media:**
- `TWITTER_BEARER_TOKEN` - Twitter Bearer Token
- `TWITTER_API_KEY` - Twitter API Key
- `TWITTER_API_SECRET` - Twitter API Secret
- `TWITTER_ACCESS_TOKEN` - Twitter Access Token
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter Access Secret
- `X_CLIENT_ID` - X API Client ID
- `X_CLIENT_SECRET` - X API Client Secret
- `X_BEARER_TOKEN` - X API Bearer Token
- `X_ACCESS_TOKEN` - X API Access Token
- `X_ACCESS_TOKEN_SECRET` - X API Access Secret

#### **🌤️ Additional Weather:**
- `SRF_WEATHER_API_KEY` - SRF Weather API

#### **🎵 Music Integration:**
- `SPOTIFY_CLIENT_ID` - Spotify Client ID
- `SPOTIFY_CLIENT_SECRET` - Spotify Client Secret
- `SPOTIFY_REDIRECT_URI` - Spotify Redirect URI

#### **⚙️ System:**
- `SUPABASE_SERVICE_ROLE_KEY` - Enhanced DB Access
- `ENVIRONMENT` - development/production
- `LOG_LEVEL` - INFO/DEBUG/WARNING
- `DEBUG` - true/false

## 🎯 Setup-Modi im Detail

### **1. 🆕 CREATE MODE**

**Situation:** Keine .env oder leere .env vorhanden

```bash
📍 Status: ❌ .env Datei existiert nicht
🎯 Aktion: Erstelle .env aus .env.example
✅ Ergebnis: Vollständige .env mit allen 23 Variablen

📝 NÄCHSTE SCHRITTE:
1. Öffne .env und trage deine API Keys ein
2. Minimale Anforderungen:
   • SUPABASE_URL: Supabase Projekt URL
   • SUPABASE_ANON_KEY: Supabase Anonymous Key
   • OPENAI_API_KEY: OpenAI API Key für GPT-4 & DALL-E
   • ELEVENLABS_API_KEY: ElevenLabs API Key für Text-to-Speech
   • COINMARKETCAP_API_KEY: CoinMarketCap API Key für Crypto-Daten
   • WEATHER_API_KEY: Weather API Key

3. Teste mit: cd backend && python cli_master.py status
```

### **2. 🔧 REPAIR MODE**

**Situation:** .env unvollständig oder fehlerhaft

```bash
📍 Status: ⚠️ 4 erforderliche Variable(n) fehlen
🎯 Aktion: Backup + Überschreibung mit Template
💾 Backup erstellt: /Users/user/RadioX/.env.backup
✅ .env repariert!

📝 NÄCHSTE SCHRITTE:
1. Trage deine API Keys in .env ein
2. Übertrage ggf. Werte aus dem Backup
```

### **3. ✅ VALIDATE MODE**

**Situation:** .env vollständig konfiguriert

```bash
📍 Status: ✅ .env vollständig (3 optionale fehlen)

✅ .env Validierung:

🔑 ERFORDERLICHE API KEYS:
   ✅ SUPABASE_URL: Supabase Projekt URL
   ✅ SUPABASE_ANON_KEY: Supabase Anonymous Key
   ✅ OPENAI_API_KEY: OpenAI API Key für GPT-4 & DALL-E
   ✅ ELEVENLABS_API_KEY: ElevenLabs API Key für Text-to-Speech
   ✅ COINMARKETCAP_API_KEY: CoinMarketCap API Key für Crypto-Daten
   ✅ WEATHER_API_KEY: Weather API Key

📊 OPTIONALE KEYS:
   ✅ 8/17 optionale Keys konfiguriert

🎉 SETUP VOLLSTÄNDIG! System ist einsatzbereit.
🧪 Teste mit: cd backend && python cli_master.py status
```

## 🧰 Technische Features

### **🔒 Automatisches Backup-System**

```python
def _repair_env_file(self):
    # Backup vor jeder Änderung
    backup_file = self.env_file.with_suffix('.env.backup')
    shutil.copy2(self.env_file, backup_file)
    print(f"💾 Backup erstellt: {backup_file}")
    
    # Reparatur mit Template
    shutil.copy2(self.env_example_file, self.env_file)
```

### **🔍 Intelligentes Parsing**

```python
def _load_env_file(self) -> Dict[str, str]:
    env_vars = {}
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    return env_vars
```

### **✨ Template-Erkennung**

```python
def is_placeholder_value(value: str) -> bool:
    """Erkennt Placeholder-Werte wie 'your_key_here'"""
    return value.startswith("your_") or not value.strip()

# Verwendung im Validation
if value and not is_placeholder_value(value):
    status = "✅ Konfiguriert"
else:
    status = "❌ Placeholder/Leer"
```

### **📊 Status-Kategorisierung**

```python
# Alle Variablen kategorisiert
env_variables = [
    EnvVariable("SUPABASE_URL", True, "Supabase Projekt URL", "database"),
    EnvVariable("OPENAI_API_KEY", True, "OpenAI API Key", "ai"),
    EnvVariable("TWITTER_BEARER_TOKEN", False, "Twitter Bearer", "social"),
    # ... 20 weitere
]

# Automatische Required/Optional Trennung
required_vars = [v for v in env_variables if v.required]
optional_vars = [v for v in env_variables if not v.required]
```

## 🚀 Integration & Workflows

### **🔗 CLI-Integration**

Das Setup-System ist vollständig in das RadioX CLI integriert:

```bash
# Automatische .env Validation bei jedem CLI-Start
cd backend && python cli_master.py status
# → Lädt Settings und validiert .env automatisch

# Settings-System in Services
from config.settings import get_settings
settings = get_settings()  # Zeigt .env Status beim Laden
```

### **🏗️ Development Workflow**

#### **Für neue Entwickler:**
```bash
# 1. Repository klonen
git clone https://github.com/your-repo/RadioX.git
cd RadioX

# 2. Einmaliges automatisches Setup
./setup.sh

# 3. API Keys eintragen (siehe .env.example Kommentare)
nano .env

# 4. Backend Setup & Test
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python cli_master.py status

# ✅ Ready to develop!
```

#### **Für bestehende Entwickler:**
```bash
# Quick Health-Check bei Problemen
./setup.sh  # Repariert automatisch falls nötig

# Status-Check
cd backend && python cli_master.py status
```

### **🤖 CI/CD Integration**

```yaml
# GitHub Actions Beispiel
- name: Setup Environment
  run: |
    python3 setup_env.py
    # API Keys aus GitHub Secrets eintragen
    echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env
    echo "ELEVENLABS_API_KEY=${{ secrets.ELEVENLABS_API_KEY }}" >> .env
    # ... weitere Secrets

- name: Validate Setup
  run: |
    cd backend
    python cli_master.py status
```

## 🛠️ Troubleshooting

### **❓ Häufige Probleme**

| Problem | Diagnose | Lösung |
|---------|----------|---------|
| `python command not found` | Python 3 nicht installiert/im PATH | `python3 setup_env.py` verwenden |
| `Permission denied: ./setup.sh` | Execute-Bit fehlt | `chmod +x setup.sh` |
| `.env existiert aber Keys fehlen` | Unvollständige Konfiguration | `./setup.sh` repariert automatisch |
| `Setup läuft aber findet Template nicht` | Falsches Verzeichnis | In RadioX Root-Verzeichnis wechseln |
| `Backup überschrieben` | Mehrfache Reparaturen | Backups heißen `.env.backup` |

### **🔍 Debug-Modi**

```bash
# 1. Detaillierte Setup-Analyse
python3 setup_env.py
# → Zeigt Status, fehlende Keys, Empfehlungen

# 2. Manual Settings Check
python3 -c "
from backend.src.config.settings import get_settings
settings = get_settings()
print('✅ Settings loaded successfully')
"

# 3. CLI System Status  
cd backend && python cli_master.py status
# → Vollständiger System-Check

# 4. .env File direkt anschauen
head -20 .env  # Erste 20 Zeilen
grep -v '^#' .env | grep '='  # Nur aktive Variablen
```

### **⚠️ Bekannte Limitations**

| Feature | Unterstützt | Grund |
|---------|-------------|--------|
| Standard .env Format | ✅ | Vollständig |
| Kommentare | ✅ | Werden preserviert |
| Multi-line Values | ❌ | Parser-Limitation |
| Complex Quoting | ❌ | Security/Simplicity |
| Variable Expansion | ❌ | Not needed für RadioX |

## 📈 Advanced Usage

### **🔧 Custom Setup Scripts**

```python
# Eigenes Setup-Script für Deployment
from setup_env import EnvSetupManager

manager = EnvSetupManager()

# Programmatisches Setup
result = manager.setup_env()
if result["success"]:
    print("✅ Setup erfolgreich")
else:
    print(f"❌ Setup Fehler: {result['error']}")

# Custom Validation
env_content = manager._load_env_file()
all_required_present = all(
    var.name in env_content and env_content[var.name].strip()
    for var in manager.env_variables if var.required
)
```

### **📊 Custom Reports**

```python
# Erweiterte Status-Reports
def generate_setup_report():
    manager = EnvSetupManager()
    env_content = manager._load_env_file()
    
    report = {
        "required_missing": [],
        "optional_configured": [],
        "placeholder_values": []
    }
    
    for var in manager.env_variables:
        value = env_content.get(var.name, "")
        if var.required and not value:
            report["required_missing"].append(var.name)
        elif not var.required and value:
            report["optional_configured"].append(var.name)
        if value.startswith("your_"):
            report["placeholder_values"].append(var.name)
    
    return report
```

### **🎯 API Key Cost Optimization**

```python
# Cost-aware Setup für verschiedene Use-Cases
SETUP_PROFILES = {
    "minimal": ["SUPABASE_URL", "SUPABASE_ANON_KEY"],  # Nur DB
    "development": ["SUPABASE_*", "OPENAI_API_KEY"],   # Basic Development  
    "production": ["SUPABASE_*", "OPENAI_*", "ELEVENLABS_*", "COINMARKETCAP_*"],
    "full": "*"  # Alle 23 Variablen
}

def setup_for_profile(profile: str):
    """Setup nur für spezifischen Use-Case"""
    # Implementation für verschiedene Setup-Profile
```

## 📚 Weiterführende Dokumentation

- **[README.md](README.md)** - Vollständige RadioX Dokumentation
- **[backend/src/config/settings.py](backend/src/config/settings.py)** - Settings-Klasse Source
- **[.env.example](.env.example)** - Vollständiges Template mit Kommentaren
- **[backend/cli_master.py](backend/cli_master.py)** - CLI-Integration

---

## 🎉 Fazit

Das RadioX Environment Setup System bietet:

- ✅ **Foolproof Setup** - Funktioniert immer, auch bei kaputten .env
- ✅ **Zero-Config** - Ein Kommando für vollständiges Setup
- ✅ **Smart Backup** - Sichere Reparatur ohne Datenverlust  
- ✅ **Clear Guidance** - Präzise Anweisungen für nächste Schritte
- ✅ **Production Ready** - CI/CD Integration & Team-Workflows

**Mit `./setup.sh` ist RadioX in < 30 Sekunden einsatzbereit! 🚀** 