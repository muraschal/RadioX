# 🎙️ Show Generation Guide

<div align="center">

![User Guide](https://img.shields.io/badge/guide-user-blue)
![Difficulty](https://img.shields.io/badge/difficulty-beginner-green)
![Time](https://img.shields.io/badge/time-10%20min-orange)

**🎭 Complete guide to generating AI radio shows with RadioX**

[🏠 Documentation](../) • [👤 User Guides](../README.md#-user-guides) • [🎤 Voice Config](voice-configuration.md) • [📡 API Reference](api-reference.md)

</div>

---

## 🎯 Overview

RadioX uses **one central generator** (`radiox_master.py`) that automatically adapts to different times of day, creating the perfect show for any moment.

### ✨ **Key Features**
- 🕐 **Smart Time Detection** - Automatically knows what time it is
- 🎭 **Auto Style Adaptation** - Morning energetic, night relaxed
- 🌍 **Multi-language** - English V3 & German support
- 🎨 **Complete Production** - Script + Audio + Cover Art

---

## 🚀 Quick Start

### **🎬 Generate Your First Show**

```bash
# Basic show (script only)
python production/radiox_master.py --action generate_broadcast

# Full production (script + audio + cover)
python production/radiox_master.py --action generate_broadcast --generate-audio
```

**🎯 That's it!** Your show is ready in `backend/output/`

---

## 🕐 Automatic Style Detection

RadioX **automatically detects** the perfect style based on current time:

| 🕐 Time Range | 🎭 Style | 📝 Characteristics | ⏱️ Duration |
|---------------|----------|-------------------|-------------|
| **🌅 05:00-11:59** | Morning | Energetic, motivational, positive news | 8 min |
| **🌞 12:00-16:59** | Afternoon | Professional, business-focused, analytical | 10 min |
| **🌆 17:00-21:59** | Evening | Relaxed, conversational, entertainment | 12 min |
| **🌙 22:00-04:59** | Night | Calm, introspective, fewer breaking news | 15 min |

### **🎭 Character Personalities by Time**

#### **🌅 Morning Style**
- **Marcel:** Excited, passionate, energetic
- **Jarvis:** Witty, sharp, informative
- **Content:** Positive news, weather focus, motivational

#### **🌞 Afternoon Style**  
- **Marcel:** Friendly, engaging, professional
- **Jarvis:** Analytical, precise, business-focused
- **Content:** Economic news, tech updates, higher news density

#### **🌆 Evening Style**
- **Marcel:** Thoughtful, warm, conversational
- **Jarvis:** Philosophical, deep, entertaining
- **Content:** Entertainment, sports, longer discussions

#### **🌙 Night Style**
- **Marcel:** Calm, reflective, soothing
- **Jarvis:** Mysterious, contemplative, gentle
- **Content:** Relaxed topics, fewer breaking news, atmospheric

---

## 🎛️ Customization Options

### **⏰ Override Time Style**

```bash
# Force night style during day
python production/radiox_master.py --action generate_broadcast --time 23:00

# Force morning energy in evening  
python production/radiox_master.py --action generate_broadcast --time 08:00
```

### **📰 Control News Amount**

```bash
# Relaxed show (2 news)
python production/radiox_master.py --action generate_broadcast --news-count 2

# Intensive show (6 news)
python production/radiox_master.py --action generate_broadcast --news-count 6
```

### **🌍 Language Selection**

```bash
# English V3 (default)
python production/radiox_master.py --action generate_broadcast --language en

# German
python production/radiox_master.py --action generate_broadcast --language de
```

### **📍 Regional Focus**

```bash
# Zurich focus (default)
python production/radiox_master.py --action generate_broadcast --channel zurich

# Basel focus
python production/radiox_master.py --action generate_broadcast --channel basel

# Bern focus
python production/radiox_master.py --action generate_broadcast --channel bern
```

---

## 🎨 Complete Parameter Reference

### **🔧 Basic Parameters**

| Parameter | Default | Description | Examples |
|-----------|---------|-------------|----------|
| `--time HH:MM` | Current time | Override time for style | `08:00`, `22:45` |
| `--channel` | `zurich` | Regional focus | `zurich`, `basel`, `bern` |
| `--language` | `en` | Show language | `en`, `de` |
| `--news-count N` | `4` | Number of news stories | `2`, `4`, `6` |
| `--max-age N` | `1` | Max news age (hours) | `1`, `3`, `6` |
| `--generate-audio` | `false` | Create audio + cover | Flag (no value) |

### **🎯 Advanced Usage**

```bash
# Perfect morning commute show
python production/radiox_master.py \
  --action generate_broadcast \
  --time 07:30 \
  --news-count 5 \
  --generate-audio \
  --language de

# Relaxed evening show
python production/radiox_master.py \
  --action generate_broadcast \
  --time 20:00 \
  --news-count 3 \
  --max-age 2 \
  --generate-audio

# Late night chill session
python production/radiox_master.py \
  --action generate_broadcast \
  --time 23:30 \
  --news-count 2 \
  --language de
```

---

## 📁 Output Structure

After generation, find your content in:

```
backend/output/
├── audio/
│   └── RadioX_Final_YYYYMMDD_HHMMSS.mp3    # 4-5MB complete show
├── covers/  
│   └── RadioX_Cover_YYYYMMDD_HHMMSS.png    # 1024x1024 time-specific cover
└── scripts/
    └── RadioX_Script_YYYYMMDD_HHMMSS.txt   # Generated dialogue script
```

### **🎵 Audio Features**
- **Format:** MP3, 128kbps, stereo
- **Duration:** 8-15 minutes (style-dependent)
- **Voices:** Marcel (enthusiastic) & Jarvis (analytical)
- **Cover:** Embedded album art
- **Quality:** Professional radio-ready

---

## 🎭 Show Examples

### **🌅 Morning Rush (07:00)**
```bash
python production/radiox_master.py --action generate_broadcast --time 07:00 --generate-audio
```
**Result:** High-energy 8-minute show with 4-5 news, weather focus, motivational tone

### **🍽️ Lunch Break (12:30)**
```bash
python production/radiox_master.py --action generate_broadcast --time 12:30 --news-count 4
```
**Result:** Professional 10-minute show with business news, analytical discussions

### **🌆 After Work (18:30)**
```bash
python production/radiox_master.py --action generate_broadcast --time 18:30 --news-count 3
```
**Result:** Relaxed 12-minute show with entertainment, sports, longer conversations

### **🌙 Late Night (23:15)**
```bash
python production/radiox_master.py --action generate_broadcast --time 23:15 --news-count 2 --language de
```
**Result:** Calm 15-minute German show with atmospheric content, fewer breaking news

---

## 🔧 Troubleshooting

### **❌ Common Issues**

| 🚨 Problem | 🔍 Cause | ✅ Solution |
|------------|----------|-------------|
| No audio generated | Missing API keys | Check `.env` file, verify ElevenLabs key |
| Script too short | Not enough news | Increase `--max-age` or check RSS feeds |
| Wrong language | Language parameter | Use `--language de` for German |
| No cover art | OpenAI API issue | Verify OpenAI key, check credits |

### **🧪 Test Commands**

```bash
# Test all services
python production/radiox_master.py --action test_services

# Test news collection only
python production/radiox_master.py --action analyze_news

# Check system status
python production/radiox_master.py --action system_status
```

---

## 💡 Pro Tips

### **🎯 Best Practices**

1. **🕐 Use Real Time:** Let the system auto-detect for authentic shows
2. **📰 Adjust News Count:** 2-3 for relaxed, 4-6 for intensive
3. **🎨 Generate Audio:** Always use `--generate-audio` for complete experience
4. **🌍 Match Language:** Use German for Swiss-focused content
5. **📍 Pick Right Channel:** Match your target audience location

### **⚡ Quick Workflows**

```bash
# Development testing (fast)
python production/radiox_master.py --action generate_broadcast --news-count 2

# Production ready (complete)
python production/radiox_master.py --action generate_broadcast --generate-audio

# Scheduled automation (cron)
0 6,12,18 * * * cd /app && python production/radiox_master.py --action generate_broadcast --generate-audio
```

---

## 🔗 Related Guides

- **🎤 [Voice Configuration](voice-configuration.md)** - Setup voices & audio settings
- **📡 [API Reference](api-reference.md)** - Use RadioX programmatically  
- **🏗️ [Architecture](../developer-guide/architecture.md)** - Understand the system design
- **🚀 [Production](../deployment/production.md)** - Deploy for live use

---

<div align="center">

**🎙️ Ready to create amazing radio shows!**

[🏠 Documentation](../) • [🎤 Voice Setup](voice-configuration.md) • [💬 Get Help](../README.md#-support)

</div> 