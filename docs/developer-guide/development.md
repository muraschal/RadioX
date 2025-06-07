# 🔧 Development Guide

<div align="center">

![Developer Guide](https://img.shields.io/badge/guide-developer-purple)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-30%20min-orange)

**🛠️ Complete guide to setting up and developing RadioX**

[🏠 Documentation](../) • [👨‍💻 Developer Guides](../README.md#-developer-guides) • [🏗️ Architecture](architecture.md) • [🧪 Testing](testing.md)

</div>

---

## 🎯 Overview

This guide covers **complete development setup** for RadioX, from environment configuration to development workflows and code quality standards.

### ✨ **What You'll Learn**
- 🔧 **Environment Setup** - Automated .env configuration
- 🏗️ **Development Workflow** - Best practices and patterns
- 🎤 **Voice Configuration** - Supabase-based voice management
- 🛡️ **Code Quality** - Strict architectural guidelines

---

## 🚀 Quick Setup

### **⚡ Automated Setup (Recommended)**

```bash
# 1. Clone and setup
git clone https://github.com/your-org/RadioX.git
cd RadioX

# 2. Run automated setup
./setup.sh

# 3. Configure API keys
nano .env

# 4. Test system
cd backend && python cli/cli_master.py status
```

**🎯 That's it!** Your development environment is ready.

---

## 🔧 Environment Configuration

### **📋 Intelligent .env Management**

RadioX includes an **intelligent setup system** that automatically manages your environment configuration:

#### **🧠 Setup Manager Features:**
- ✅ **Analyzes .env completeness** (23 variables)
- ✅ **Creates automatic backups** before changes
- ✅ **Generates .env from template** if missing
- ✅ **Validates all API keys** (required vs optional)
- ✅ **Provides helpful reports** and next steps

#### **🎯 Setup Modes:**

| Situation | Action | Result |
|-----------|--------|--------|
| **No .env** | CREATE | Template copied |
| **Empty .env** | CREATE | Overwritten with template |
| **Incomplete .env** | REPAIR | Backup + template |
| **Complete .env** | VALIDATE | Status report |

### **🔑 Required API Keys (6)**

| Variable | Service | Purpose |
|----------|---------|---------|
| `SUPABASE_URL` | Supabase | Database connection |
| `SUPABASE_ANON_KEY` | Supabase | Database access |
| `OPENAI_API_KEY` | OpenAI | GPT-4 + DALL-E 3 |
| `ELEVENLABS_API_KEY` | ElevenLabs | Text-to-Speech |
| `COINMARKETCAP_API_KEY` | CoinMarketCap | Crypto data |
| `WEATHER_API_KEY` | OpenWeatherMap | Weather data |

### **⚙️ Optional Keys (17)**

#### **🎤 Voice Configuration:**
```bash
ELEVENLABS_MARCEL_VOICE_ID=your_marcel_voice_id
ELEVENLABS_JARVIS_VOICE_ID=your_jarvis_voice_id
```

#### **🐦 Social Media Integration:**
```bash
TWITTER_BEARER_TOKEN=your_twitter_bearer
X_CLIENT_ID=your_x_client_id
# ... (12 more social media keys)
```

#### **🎵 Music Integration:**
```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
```

---

## 🏗️ Development Architecture

### **📁 Project Structure**

```
RadioX/
├── 🔧 setup_env.py          # Intelligent setup manager
├── ⚡ setup.sh              # Quick setup alias
├── 📋 .env.example          # Complete template (23 vars)
├── 🔑 .env                  # Your configuration
├── 💾 .env.backup          # Automatic backups
└── 📻 backend/
    ├── 🎯 src/services/     # Core business logic
    ├── 🔧 cli/             # Development tools
    ├── 🚀 production/      # Production scripts
    └── ⚙️ config/          # Configuration
```

### **🎯 Service-Oriented Design**

RadioX follows **strict architectural principles**:

```python
# ✅ CORRECT: Extend existing services
class AudioGenerationService:
    async def new_audio_feature(self):
        voice_service = get_voice_config_service()
        voice_config = await voice_service.get_voice_config("marcel")

# ❌ WRONG: Create helper scripts
# def helper_function():  # NEVER!
```

---

## 🎤 Voice Configuration System

### **🎯 Architecture Principle**

```
❌ WRONG: Hardcoded voice configurations
✅ RIGHT: Supabase-based voice management
```

### **📊 Voice Database (Supabase)**

```sql
-- Table: voice_configurations
-- Only 2 standard voices: marcel, jarvis
-- Direct API access (NO MCPs in production!)
-- ElevenLabs API v1 with latest models (v2, v2.5, v3)
```

### **🔧 Voice Service Integration**

```python
# ✅ CORRECT: Use Voice Configuration Service
from src.services.voice_config_service import get_voice_config_service

service = get_voice_config_service()
voice_config = await service.get_voice_config("marcel")

# ❌ WRONG: Hardcoded voices
# voice_config = {"marcel": {"voice_id": "..."}}  # NEVER!
```

### **🖥️ Voice Management CLI**

```bash
# Manage voice configurations
python cli/cli_voice.py list        # Show all voices
python cli/cli_voice.py stats       # Statistics
python cli/cli_voice.py test marcel # Test voice

# ❌ WRONG: New voice scripts
# python voice_helper.py  # NEVER!
```

---

## 🛡️ Code Quality Standards

### **❌ ABSOLUTE PROHIBITIONS - NEVER BREAK:**

#### **🚫 Forbidden File Patterns:**
```bash
# These patterns are ABSOLUTELY FORBIDDEN:
helper_*.py          # Temporary helpers
temp_*.py           # Temporary scripts  
debug_*.py          # Debug scripts
quick_*.py          # Quick-fix scripts
test_*.py           # Ad-hoc tests (except official)
fix_*.py            # Fix scripts
patch_*.py          # Patch scripts
experiment_*.py     # Experiment scripts
random_*.py         # Random scripts
util_*.py           # Utility scripts (except documented)
```

#### **🚫 Forbidden Practices:**
- Temporary scripts for "quick tests"
- Helper functions in separate files
- Code duplication instead of service extension
- Hardcoded paths or values
- Unclean files after development

### **✅ ALLOWED DEVELOPMENT PATTERNS**

#### **📁 Use Existing Architecture:**

```bash
# ✅ Existing CLI Scripts (only these):
cli_master.py       # Master control
cli_audio.py        # Audio testing
cli_image.py        # Image testing
cli_logging.py      # Logging management
cli_overview.py     # System overview
cli_weather.py      # Weather testing
cli_voice.py        # Voice configuration management
```

#### **🔧 Extend Core Services:**
```bash
src/services/
├── audio_generation.py     # Audio logic
├── content_combiner.py     # Final assembly
├── content_logging.py      # Logging system
├── image_generation.py     # Cover art
├── news_aggregation.py     # News collection
├── weather_service.py      # Weather data
└── voice_config_service.py # Voice configuration (Supabase)
```

---

## 🎯 Development Workflows

### **1. Testing New Features**

```bash
# ✅ CORRECT: Use existing test infrastructure
python cli/cli_master.py test
python cli/cli_audio.py --action test
python cli/cli_voice.py test
python cli/cli_logging.py --action workflow

# ❌ WRONG: New test scripts
# python test_my_feature.py  # NEVER!
```

### **2. Voice Development**

```bash
# ✅ CORRECT: Extend voice service
python cli/cli_voice.py list
python cli/cli_voice.py test marcel

# ❌ WRONG: Voice helpers
# python voice_debug.py  # NEVER!
```

### **3. Debugging**

```bash
# ✅ CORRECT: Use existing debug tools
python cli/cli_master.py --action status
python cli/cli_overview.py
python cli/cli_voice.py stats
python cli/cli_logging.py --action reports

# ❌ WRONG: Debug helpers
# python debug_issue.py  # NEVER!
```

### **4. Feature Development**

```python
# ✅ CORRECT: Extend service
class AudioGenerationService:
    async def new_audio_feature(self):
        """New function in existing service"""
        # Use Voice Configuration Service
        voice_service = get_voice_config_service()
        voice_config = await voice_service.get_voice_config("marcel")

# ❌ WRONG: New script
# def helper_function():  # NEVER!
```

---

## 🧪 Testing & Validation

### **🔬 Testing Strategy**

```bash
# Level 1: Individual service tests
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test

# Level 2: Integration tests
python cli/cli_master.py test

# Level 3: System tests
python production/radiox_master.py --action test_services

# Level 4: Production validation
python production/radiox_master.py --action system_status
```

### **🛡️ Quality Enforcement**

#### **Before Every Change:**
1. **Check:** Which existing service is responsible?
2. **Voice-Check:** Does the code use Voice Configuration Service?
3. **Extend:** Extend service with new functionality
4. **Test:** Test with existing CLI tools
5. **Document:** Document changes

#### **After Every Change:**
1. **Cleanup:** Delete all temporary files
2. **Voice-Validation:** Check voice configurations via CLI
3. **Validate:** Check architectural integrity
4. **Test:** Ensure complete functionality
5. **Commit:** Clean commits with clear messages

### **🔍 Code Review Checklist**
- [ ] No temporary scripts created
- [ ] Existing architecture followed
- [ ] Voice Configuration Service used (not hardcoded)
- [ ] Services extended instead of new files
- [ ] CLI structure respected
- [ ] Documentation updated
- [ ] Tests with existing tools
- [ ] Cleaned up after development

---

## ⚠️ Important: MCP vs. Production

### **🏠 Local Development (Cursor)**
```bash
# MCPs allowed for rapid development
# Supabase MCP for quick DB operations in Cursor
```

### **🚀 Production System**
```bash
# Only direct API access
# All services use supabase_client.py for DB connections
# NO MCP dependencies in production code!
```

---

## 🔗 Related Guides

- **🏗️ [Architecture](architecture.md)** - System design and components
- **🧪 [Testing](testing.md)** - Testing strategies and tools
- **🤝 [Contributing](contributing.md)** - Code standards and workflow
- **🚀 [Production](../deployment/production.md)** - Deploy your changes

---

<div align="center">

**🛠️ Ready to develop like a pro!**

[🏠 Documentation](../) • [🏗️ Architecture](architecture.md) • [💬 Get Help](../README.md#-support)

</div> 