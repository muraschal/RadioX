# 🎤 Voice Configuration Guide

<div align="center">

![User Guide](https://img.shields.io/badge/guide-user-blue)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-15%20min-orange)

**🔊 Complete guide to configuring voices and audio in RadioX**

[🏠 Documentation](../) • [👤 User Guides](../README.md#-user-guides) • [🎙️ Show Generation](show-generation.md) • [📡 API Reference](api-reference.md)

</div>

---

## 🎯 Overview

RadioX uses **ElevenLabs V3 TTS** for professional-quality voice generation with two distinct AI personalities: **Marcel** (enthusiastic human host) and **Jarvis** (analytical AI assistant).

### ✨ **Key Features**
- 🎭 **Dual Personalities** - Marcel & Jarvis with distinct characteristics
- 🔊 **V3 Technology** - Latest ElevenLabs V3 with emotional tags
- 🌍 **Multi-language** - English (primary) & German support
- 🎨 **Auto-Embedding** - Cover art automatically embedded in MP3

---

## 🎭 Default Voice Configuration

### **🎤 Primary English Voices (V3 Optimized)**

| 🎭 Character | 🔊 Voice | 🆔 Voice ID | 📝 Personality |
|--------------|----------|-------------|----------------|
| **Marcel** | Rachel | `21m00Tcm4TlvDq8ikWAM` | Enthusiastic, passionate host |
| **Jarvis** | Bella | `EXAVITQu4vr4xnSDxMaL` | Analytical, witty AI assistant |

### **🔄 Alternative English Voices**

| 🎭 Character | 🔊 Voice | 🆔 Voice ID | 📝 Style |
|--------------|----------|-------------|----------|
| **Marcel Alt** | Adam | `pNInz6obpgDQGcFmaJgB` | Confident, professional |
| **Jarvis Alt** | Josh | `TxGEqnHWrfWFTfGW9XjX` | Deep, authoritative |

### **🇩🇪 German Fallback Voices**

| 🎭 Character | 🔊 Voice | 🆔 Voice ID | 📝 Notes |
|--------------|----------|-------------|----------|
| **Marcel DE** | Custom | `your_marcel_de_id` | Configure in `.env` |
| **Jarvis DE** | Custom | `your_jarvis_de_id` | Configure in `.env` |

---

## ⚙️ Configuration Setup

### **🔧 Environment Variables**

Add these to your `.env` file:

```bash
# ElevenLabs API (Required)
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Voice IDs (Optional - defaults to Rachel/Bella)
ELEVENLABS_MARCEL_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_JARVIS_VOICE_ID=EXAVITQu4vr4xnSDxMaL

# German Voice IDs (Optional)
ELEVENLABS_MARCEL_DE_VOICE_ID=your_german_marcel_id
ELEVENLABS_JARVIS_DE_VOICE_ID=your_german_jarvis_id
```

### **🎛️ Voice Settings (Auto-Configured)**

RadioX automatically optimizes these settings:

```python
voice_settings = {
    "stability": 0.75,        # Consistent voice quality
    "similarity_boost": 0.85, # Voice similarity to original
    "style": 0.65,           # Emotional expressiveness
    "use_speaker_boost": True # Enhanced clarity
}
```

---

## 🎭 V3 Emotional Tags

RadioX uses **ElevenLabs V3 emotional tags** for natural expression:

### **🎪 Available Emotional Tags**

| 🎭 Tag | 📝 Usage | 🎯 Best For |
|--------|----------|-------------|
| `[excited]` | High energy, enthusiasm | Breaking news, Bitcoin gains |
| `[sarcastic]` | Dry humor, wit | Jarvis responses, irony |
| `[whispers]` | Intimate, secretive | Confidential info, asides |
| `[laughs]` | Natural laughter | Funny moments, reactions |
| `[curious]` | Questioning, interested | Exploring topics |
| `[impressed]` | Amazed, surprised | Remarkable news |

### **📝 Script Format Example**

```
MARCEL: [excited] Welcome to RadioX! Amazing Bitcoin news today!
JARVIS: [sarcastic] Obviously predictable, Marcel.
MARCEL: [laughs] You're such a party pooper! [laughs harder]
JARVIS: [whispers] Between you and me, this is actually impressive.
```

---

## 🔊 Audio Quality Settings

### **🎵 Output Specifications**

| 🎛️ Setting | 📊 Value | 📝 Description |
|------------|----------|----------------|
| **Format** | MP3 | Universal compatibility |
| **Bitrate** | 128 kbps | Radio-quality, small file size |
| **Sample Rate** | 44.1 kHz | CD-quality audio |
| **Channels** | Stereo | Full stereo experience |
| **Duration** | 8-15 min | Time-dependent |

### **🎨 Cover Art Integration**

- **Resolution:** 1024x1024 pixels
- **Format:** PNG → embedded as MP3 album art
- **Style:** Time-specific DALL-E 3 generation
- **Embedding:** Automatic with mutagen library

---

## 🛠️ Custom Voice Setup

### **🎤 Using Your Own Voices**

1. **Create ElevenLabs Account**
   - Sign up at [elevenlabs.io](https://elevenlabs.io)
   - Get your API key

2. **Clone or Create Voices**
   - Use ElevenLabs voice cloning
   - Or select from their voice library

3. **Get Voice IDs**
   ```bash
   # List available voices
   curl -X GET "https://api.elevenlabs.io/v1/voices" \
        -H "xi-api-key: YOUR_API_KEY"
   ```

4. **Update Configuration**
   ```bash
   # Add to .env
   ELEVENLABS_MARCEL_VOICE_ID=your_custom_marcel_id
   ELEVENLABS_JARVIS_VOICE_ID=your_custom_jarvis_id
   ```

### **🧪 Test Your Voices**

```bash
# Test voice configuration
python cli/cli_audio.py test

# Generate test audio
python production/radiox_master.py --action generate_broadcast --news-count 2 --generate-audio
```

---

## 🌍 Language Configuration

### **🇺🇸 English (Default)**
- **Primary:** Rachel (Marcel) + Bella (Jarvis)
- **Quality:** V3 optimized with emotional tags
- **Style:** Natural American English

### **🇩🇪 German (Fallback)**
- **Setup:** Requires custom German voice IDs
- **Usage:** `--language de` parameter
- **Quality:** Standard TTS (V3 tags may vary)

### **🔄 Language Switching**

```bash
# English show (default)
python production/radiox_master.py --action generate_broadcast --generate-audio

# German show
python production/radiox_master.py --action generate_broadcast --language de --generate-audio
```

---

## 🔧 Troubleshooting

### **❌ Common Voice Issues**

| 🚨 Problem | 🔍 Cause | ✅ Solution |
|------------|----------|-------------|
| No audio generated | Missing API key | Add `ELEVENLABS_API_KEY` to `.env` |
| Wrong voice used | Incorrect voice ID | Verify voice IDs in ElevenLabs dashboard |
| Poor audio quality | Low credits/quota | Check ElevenLabs account credits |
| German voices not working | Missing German voice IDs | Add German voice IDs to `.env` |
| Robotic sound | V3 not enabled | Ensure using V3-compatible voices |

### **🧪 Diagnostic Commands**

```bash
# Test ElevenLabs connection
python cli/cli_audio.py test

# Check voice configuration
python cli/cli_master.py status

# Generate test audio
python cli/cli_audio.py test --voice-test
```

### **📊 Voice Quality Optimization**

```python
# Optimal settings for radio
voice_settings = {
    "stability": 0.75,        # Higher = more consistent
    "similarity_boost": 0.85, # Higher = more like original
    "style": 0.65,           # Higher = more expressive
    "use_speaker_boost": True # Always enable for clarity
}
```

---

## 💡 Pro Tips

### **🎯 Voice Selection Best Practices**

1. **🎭 Character Matching**
   - Marcel: Choose warm, enthusiastic voices
   - Jarvis: Select analytical, precise voices

2. **🌍 Language Consistency**
   - Use native speakers for each language
   - Test pronunciation of technical terms

3. **🔊 Quality Optimization**
   - Use V3-compatible voices when possible
   - Enable speaker boost for radio clarity
   - Test with actual news content

### **⚡ Quick Voice Tests**

```bash
# Quick voice test
python cli/cli_audio.py test

# Full production test
python production/radiox_master.py --action generate_broadcast --news-count 1 --generate-audio

# Compare different voices
# 1. Change voice IDs in .env
# 2. Generate test show
# 3. Compare audio quality
```

---

## 🔗 Related Guides

- **🎙️ [Show Generation](show-generation.md)** - Create radio shows with your voices
- **📡 [API Reference](api-reference.md)** - Programmatic voice control
- **🏗️ [Architecture](../developer-guide/architecture.md)** - Audio system design
- **🚀 [Production](../deployment/production.md)** - Deploy with custom voices

---

<div align="center">

**🎤 Your voices are ready for professional radio!**

[🏠 Documentation](../) • [🎙️ Show Generation](show-generation.md) • [💬 Get Help](../README.md#-support)

</div> 