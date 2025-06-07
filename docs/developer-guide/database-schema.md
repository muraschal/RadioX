# 🗄️ Database Schema Guide

<div align="center">

![Developer Guide](https://img.shields.io/badge/guide-developer-purple)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-20%20min-orange)

**🏗️ Complete guide to RadioX database schema management**

[🏠 Documentation](../) • [👨‍💻 Developer Guides](../README.md#-developer-guides) • [🏗️ Architecture](architecture.md) • [🔧 Development](development.md)

</div>

---

## 🎯 Overview

RadioX uses a **centralized schema management system** that replaces all fragmented DB-create scripts with a unified, professional approach.

### ✨ **Schema Management Features**
- 🏗️ **Unified Schema** - All tables in one system
- 🔗 **Dependency Resolution** - Automatic creation order
- 🧪 **Built-in Testing** - Schema integrity validation
- 🧹 **Automated Cleanup** - Old data management
- 📊 **Comprehensive Monitoring** - Schema status tracking
- 🗑️ **Legacy Cleanup** - Removed 9+ old fragmented tables

---

## 🚀 Quick Start

### **⚡ Create Complete Schema**

```bash
# Create all tables with test data
python cli/cli_schema.py create

# Force recreate (deletes existing tables)
python cli/cli_schema.py recreate

# Show schema information
python cli/cli_schema.py info
```

### **🧪 Test & Validate**

```bash
# Test schema integrity
python cli/cli_schema.py test

# Cleanup old data
python cli/cli_schema.py cleanup

# Migrate from old scripts
python cli/cli_schema.py migrate
```

---

## 🏗️ Database Architecture

### **📊 Table Overview (Version 3.2.0)**

| 📋 Table | 📝 Description | 🔗 Dependencies |
|----------|----------------|-----------------|
| **voice_configurations** | ElevenLabs TTS voice settings | None (Base table) |
| **rss_feed_preferences** | RSS feed configurations for news collection | None (Base table) |
| **show_presets** | Flexible show configuration templates | voice_configurations |
| **broadcast_scripts** | Generated radio scripts with metadata | show_presets |
| **used_news** | Tracking of used news articles | broadcast_scripts |
| **broadcast_logs** | System logs for broadcast generation | broadcast_scripts |

### **🔄 Creation Order**

```
voice_configurations → rss_feed_preferences → show_presets → broadcast_scripts → [used_news, broadcast_logs]
```

**Automatic dependency resolution** ensures tables are created in the correct order.

### **🗑️ Legacy Cleanup (December 2024)**

**Removed Legacy Tables:**
- `content_categories`, `content_sources`, `content_rules` (Old content system)
- `streams`, `stream_segments`, `spotify_tracks` (Old stream system)
- `news_content`, `generation_logs` (Old generation system)
- `radio_stations` (Replaced by show_presets)

**Result:** Clean architecture with 6 focused tables instead of 15+ fragmented ones.

---

## 📋 Table Schemas

### **🎤 Voice Configurations**

```sql
CREATE TABLE voice_configurations (
    id SERIAL PRIMARY KEY,
    speaker_name VARCHAR(50) NOT NULL UNIQUE,
    voice_id VARCHAR(100) NOT NULL,
    voice_name VARCHAR(100) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    stability DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    similarity_boost DECIMAL(3,2) NOT NULL DEFAULT 0.80,
    style DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    use_speaker_boost BOOLEAN NOT NULL DEFAULT true,
    model VARCHAR(50) NOT NULL DEFAULT 'eleven_multilingual_v2',
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Purpose:** Stores ElevenLabs voice configurations for Marcel and Jarvis.

**Key Features:**
- Only 2 standard voices: marcel, jarvis
- Supabase-based management (no hardcoded values)
- ElevenLabs V3 model support
- Flexible voice parameter configuration

### **📡 RSS Feed Preferences**

```sql
CREATE TABLE rss_feed_preferences (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    feed_category VARCHAR(50) NOT NULL,
    feed_url TEXT NOT NULL,
    radio_channel VARCHAR(50) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 5,
    weight DECIMAL(3,2) NOT NULL DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    language VARCHAR(10) DEFAULT 'de',
    region VARCHAR(50) DEFAULT 'schweiz',
    content_type VARCHAR(50) DEFAULT 'news',
    target_audience VARCHAR(100) DEFAULT 'general',
    fetch_interval_minutes INTEGER DEFAULT 30,
    max_items_per_fetch INTEGER DEFAULT 10,
    timeout_seconds INTEGER DEFAULT 15,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_fetched_at TIMESTAMPTZ,
    fetch_success_count INTEGER DEFAULT 0,
    fetch_error_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_priority CHECK (priority BETWEEN 1 AND 10),
    CONSTRAINT valid_weight CHECK (weight BETWEEN 0.1 AND 5.0),
    CONSTRAINT valid_timeout CHECK (timeout_seconds BETWEEN 5 AND 60),
    CONSTRAINT unique_feed_per_channel UNIQUE (source_name, feed_category, radio_channel)
);
```

**Purpose:** Centralized RSS feed configuration for news collection.

**Key Features:**
- 23+ active Swiss & international feeds
- Channel-specific feed assignment (zurich, basel, bern)
- Priority and weighting system
- Automatic error tracking and retry logic
- Support for multiple content types (news, crypto, tech)

### **🎭 Show Presets**

```sql
CREATE TABLE show_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preset_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    city_focus TEXT,
    news_categories JSONB NOT NULL DEFAULT '{}',
    news_sources JSONB DEFAULT '[]',
    news_max_age_hours INTEGER DEFAULT 2,
    news_count_target INTEGER DEFAULT 8,
    primary_speaker TEXT NOT NULL,
    secondary_speaker TEXT,
    voice_model TEXT DEFAULT 'eleven_multilingual_v2',
    voice_style_override JSONB DEFAULT '{}',
    duration_minutes INTEGER DEFAULT 60,
    show_style TEXT DEFAULT 'balanced',
    intro_style TEXT DEFAULT 'standard',
    outro_style TEXT DEFAULT 'standard',
    include_weather BOOLEAN DEFAULT true,
    include_traffic BOOLEAN DEFAULT false,
    include_bitcoin_price BOOLEAN DEFAULT true,
    include_music_breaks BOOLEAN DEFAULT true,
    music_genre_preference JSONB DEFAULT '["electronic", "ambient"]',
    is_active BOOLEAN DEFAULT true,
    auto_generate BOOLEAN DEFAULT false,
    generation_schedule TEXT,
    target_audience TEXT DEFAULT 'general',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    CONSTRAINT valid_duration CHECK (duration_minutes BETWEEN 5 AND 180),
    CONSTRAINT valid_news_count CHECK (news_count_target BETWEEN 1 AND 20),
    CONSTRAINT valid_style CHECK (show_style IN ('energetic', 'professional', 'casual', 'local', 'balanced')),
    CONSTRAINT fk_primary_speaker FOREIGN KEY (primary_speaker) 
        REFERENCES voice_configurations(speaker_name)
);
```

**Purpose:** Flexible show configuration templates (replaces old radio_stations table).

**Key Features:**
- JSON-based news category weighting
- Voice configuration integration
- City-specific content focus
- Automated scheduling support
- Comprehensive content mix controls

### **📻 Broadcast Scripts**

```sql
CREATE TABLE broadcast_scripts (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    script_content TEXT NOT NULL,
    script_preview TEXT,
    emotion_score FLOAT DEFAULT 0,
    urgency_level INTEGER DEFAULT 1,
    preset_used TEXT,
    generation_duration_seconds INTEGER,
    word_count INTEGER,
    estimated_duration_minutes INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_preset_used FOREIGN KEY (preset_used) 
        REFERENCES show_presets(preset_name) ON DELETE SET NULL
);
```

**Purpose:** Stores generated radio scripts with comprehensive metadata.

**Key Features:**
- Complete script content storage
- Performance metrics tracking
- Show preset integration
- Emotion and urgency scoring

### **📰 Used News**

```sql
CREATE TABLE used_news (
    id SERIAL PRIMARY KEY,
    news_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    summary TEXT,
    url TEXT,
    category TEXT,
    session_id TEXT,
    emotion_score FLOAT DEFAULT 0,
    urgency_level INTEGER DEFAULT 1,
    word_count INTEGER,
    language TEXT DEFAULT 'en',
    sentiment_score FLOAT,
    used_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_session_id FOREIGN KEY (session_id) 
        REFERENCES broadcast_scripts(session_id) ON DELETE SET NULL
);
```

**Purpose:** Tracks used news articles to prevent repetition.

**Key Features:**
- Duplicate prevention
- Source and category tracking
- Sentiment analysis integration
- Session-based grouping

### **📊 Broadcast Logs**

```sql
CREATE TABLE broadcast_logs (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    data JSONB,
    session_id TEXT,
    level TEXT DEFAULT 'INFO',
    component TEXT,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    CONSTRAINT fk_log_session_id FOREIGN KEY (session_id) 
        REFERENCES broadcast_scripts(session_id) ON DELETE SET NULL
);
```

**Purpose:** System logs for broadcast generation monitoring.

**Key Features:**
- Structured JSON logging
- Performance monitoring
- Error tracking
- Component-based organization

---

## 🛠️ Schema Management CLI

### **📋 Available Commands**

```bash
# Schema Creation
python cli/cli_schema.py create          # Create all tables
python cli/cli_schema.py recreate        # Force recreate (destructive!)

# Information & Testing
python cli/cli_schema.py info            # Show schema status
python cli/cli_schema.py test            # Test schema integrity

# Maintenance
python cli/cli_schema.py cleanup         # Clean old data
python cli/cli_schema.py migrate         # Migrate from old scripts
```

### **🔍 Schema Information**

```bash
$ python cli/cli_schema.py info

📊 RADIOX SCHEMA INFORMATION
============================================
📋 Version: 3.1.0
📊 Tabellen: 5
🔗 Abhängigkeiten aufgelöst: ✅
🔄 Erstellungsreihenfolge: voice_configurations → show_presets → broadcast_scripts → used_news → broadcast_logs

📋 TABELLEN-STATUS:
--------------------------------------------------
✅ VOICE_CONFIGURATIONS
   📝 Voice-Konfigurationen für ElevenLabs TTS
   🔗 Abhängigkeiten: Keine
   📊 Test-Daten: 2 Datensätze
   📈 Sample Rows: 2

✅ SHOW_PRESETS
   📝 Flexible Show-Preset Konfigurationen
   🔗 Abhängigkeiten: voice_configurations
   📊 Test-Daten: 2 Datensätze
   📈 Sample Rows: 2
```

### **🧪 Schema Testing**

```bash
$ python cli/cli_schema.py test

🧪 RADIOX SCHEMA INTEGRITY TEST
============================================
✅ Schema-Version: 3.1.0
✅ Abhängigkeiten aufgelöst
✅ voice_configurations: Existiert
✅ show_presets: Existiert
✅ broadcast_scripts: Existiert
✅ used_news: Existiert
✅ broadcast_logs: Existiert

🎤 TESTE VOICE CONFIGURATION SERVICE:
✅ Voice-Konfigurationen geladen: 2
✅ Marcel & Jarvis verfügbar

🔗 TESTE FOREIGN KEY CONSTRAINTS:
✅ Show-Presets: 2 verfügbar
✅ Broadcast-Scripts: 1 verfügbar

🧹 TESTE CLEANUP-FUNKTIONEN:
✅ Cleanup-Funktionen verfügbar

🎉 ALLE SCHEMA-TESTS ERFOLGREICH!
```

---

## 🧹 Data Cleanup System

### **🔄 Automated Cleanup Functions**

The schema includes built-in cleanup functions for data management:

```sql
-- Cleanup alte used_news (älter als 7 Tage)
SELECT cleanup_old_used_news();

-- Cleanup alte broadcast_logs (älter als 30 Tage)
SELECT cleanup_old_broadcast_logs();

-- Cleanup alte broadcast_scripts (älter als 90 Tage)
SELECT cleanup_old_broadcast_scripts();

-- Master Cleanup (alle Funktionen)
SELECT radiox_cleanup_all();
```

### **📊 Cleanup Policies**

| 📋 Table | ⏰ Retention | 📝 Reason |
|----------|-------------|-----------|
| **used_news** | 7 days | Prevent news repetition |
| **broadcast_logs** | 30 days | System monitoring |
| **broadcast_scripts** | 90 days | Archive old shows |
| **voice_configurations** | Permanent | Core configuration |
| **show_presets** | Permanent | Template library |

### **🔧 Manual Cleanup**

```bash
# Interactive cleanup with confirmation
python cli/cli_schema.py cleanup

# Example output:
🧹 RADIOX DATABASE CLEANUP
============================================
⚠️ Dies löscht alte Daten:
  • used_news älter als 7 Tage
  • broadcast_logs älter als 30 Tage
  • broadcast_scripts älter als 90 Tage

Fortfahren? (y/N): y

✅ Used News gelöscht: 15
✅ Broadcast Logs gelöscht: 234
✅ Broadcast Scripts gelöscht: 8
🕐 Cleanup Zeit: 2024-01-15T10:30:00Z

🎉 CLEANUP ERFOLGREICH!
```

---

## 🔄 Migration from Old Scripts

### **📁 Replaced Scripts**

The new schema manager replaces these fragmented scripts:

```bash
# OLD FRAGMENTED APPROACH (❌ DELETED)
backend/create_supabase_tables.py       # Main tables
backend/create_voice_config_table.py    # Voice configs
backend/create_show_presets_table.py    # Show presets
backend/apply_show_presets_migration.py # Migrations
backend/update_voice_config.py          # Voice updates
backend/check_tables.py                 # Table checking
```

### **🚀 New Unified Approach**

```bash
# NEW CENTRALIZED APPROACH (✅ ACTIVE)
backend/database/schema_manager.py      # Core schema logic
backend/cli/cli_schema.py               # CLI interface
docs/developer-guide/database-schema.md # Documentation
```

### **🔄 Migration Process**

```bash
# Migrate from old scripts to new system
python cli/cli_schema.py migrate

# This will:
# 1. Backup existing data
# 2. Drop old tables
# 3. Create new unified schema
# 4. Insert test data
# 5. Validate integrity
```

---

## 🏗️ Development Integration

### **🔧 Voice Configuration Service**

The schema integrates seamlessly with the Voice Configuration Service:

```python
from src.services.voice_config_service import get_voice_config_service

# Service automatically uses schema-managed voices
service = get_voice_config_service()
marcel_voice = await service.get_voice_config("marcel")
jarvis_voice = await service.get_voice_config("jarvis")
```

### **📊 Show Preset Integration**

```python
# Show presets are automatically available
from database.supabase_client import get_db

db = get_db()
presets = db.client.table('show_presets').select('*').execute()

# Use preset for generation
preset = presets.data[0]
primary_speaker = preset['primary_speaker']  # Links to voice_configurations
```

### **🧪 Testing Integration**

```python
# Schema testing is integrated into main test suite
python cli/cli_master.py test  # Includes schema validation
python cli/cli_schema.py test  # Dedicated schema testing
```

---

## 📊 Performance & Monitoring

### **🔍 Schema Monitoring**

```bash
# Monitor schema health
python cli/cli_schema.py info

# Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public';
```

### **📈 Performance Optimization**

The schema includes optimized indexes:

```sql
-- Voice configurations
CREATE INDEX idx_voice_config_speaker ON voice_configurations(speaker_name);
CREATE INDEX idx_voice_config_active ON voice_configurations(is_active);

-- Show presets
CREATE INDEX idx_show_presets_active ON show_presets(is_active);
CREATE INDEX idx_show_presets_speaker ON show_presets(primary_speaker);

-- Broadcast scripts
CREATE INDEX idx_broadcast_scripts_created_at ON broadcast_scripts(created_at DESC);
CREATE INDEX idx_broadcast_scripts_session_id ON broadcast_scripts(session_id);

-- Used news
CREATE INDEX idx_used_news_used_at ON used_news(used_at DESC);
CREATE INDEX idx_used_news_source ON used_news(source);

-- Broadcast logs
CREATE INDEX idx_broadcast_logs_timestamp ON broadcast_logs(timestamp DESC);
CREATE INDEX idx_broadcast_logs_event_type ON broadcast_logs(event_type);
```

---

## 🚨 Troubleshooting

### **Common Schema Issues**

| 🚨 Issue | 🔍 Diagnosis | ✅ Solution |
|----------|-------------|-------------|
| Table creation fails | Check Supabase connection | Verify .env configuration |
| Foreign key errors | Dependency order wrong | Use `cli_schema.py recreate` |
| Voice service fails | Missing voice configs | Run `cli_schema.py create` |
| Old scripts conflict | Fragmented setup | Run `cli_schema.py migrate` |

### **🔧 Debug Commands**

```bash
# Check schema status
python cli/cli_schema.py info

# Test complete integrity
python cli/cli_schema.py test

# Recreate from scratch
python cli/cli_schema.py recreate

# Check Supabase connection
python cli/cli_master.py status
```

### **📝 Schema Validation**

```bash
# Validate all constraints
SELECT 
    conname,
    contype,
    confrelid::regclass,
    conkey,
    confkey
FROM pg_constraint 
WHERE contype = 'f';

# Check table existence
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE '%radiox%';
```

---

## 🔗 Related Guides

- **🏗️ [Architecture](architecture.md)** - System design and components
- **🔧 [Development](development.md)** - Development environment setup
- **🧪 [Testing](testing.md)** - Testing strategies and validation
- **🎤 [Voice Configuration](../user-guide/voice-configuration.md)** - Voice management

---

<div align="center">

**🗄️ Your database schema is now enterprise-ready!**

[🏠 Documentation](../) • [🏗️ Architecture](architecture.md) • [💬 Get Help](../README.md#-support)

</div> 