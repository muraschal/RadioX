# 📡 API Reference

<div align="center">

![User Guide](https://img.shields.io/badge/guide-user-blue)
![Difficulty](https://img.shields.io/badge/difficulty-beginner-green)
![Time](https://img.shields.io/badge/time-5%20min-orange)

**📡 Complete API reference for RadioX programmatic usage**

[🏠 Documentation](../) • [👤 User Guides](../README.md#-user-guides) • [🎙️ Show Generation](show-generation.md) • [🎤 Voice Config](voice-configuration.md)

</div>

---

## 🎯 Overview

RadioX provides a **command-line API** through `radiox_master.py` for programmatic control of all radio generation features.

### ✨ **Key Features**
- 🎛️ **Complete Control** - All parameters configurable
- 🔄 **Batch Processing** - Generate multiple shows
- 📊 **Status Monitoring** - System health checks
- 🧪 **Testing Interface** - Service validation

---

## 🚀 Core API Commands

### **🎙️ Generate Broadcast**

```bash
python production/radiox_master.py --action generate_broadcast [OPTIONS]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--time` | `HH:MM` | Current time | Target time for style detection |
| `--channel` | `string` | `zurich` | Regional focus (`zurich`, `basel`, `bern`) |
| `--language` | `string` | `en` | Language (`en`, `de`) |
| `--news-count` | `integer` | `4` | Number of news stories |
| `--max-age` | `integer` | `1` | Max news age in hours |
| `--generate-audio` | `flag` | `false` | Generate audio + cover |

**Examples:**

```bash
# Basic broadcast
python production/radiox_master.py --action generate_broadcast

# Full production with audio
python production/radiox_master.py --action generate_broadcast --generate-audio

# Custom time and language
python production/radiox_master.py --action generate_broadcast --time 22:45 --language de

# High-intensity news show
python production/radiox_master.py --action generate_broadcast --news-count 6 --max-age 3
```

---

## 📊 System Management

### **🔍 System Status**

```bash
python production/radiox_master.py --action system_status
```

**Returns:**
- API key status
- Service health
- Database connectivity
- Recent broadcast metrics

### **🧪 Test Services**

```bash
python production/radiox_master.py --action test_services
```

**Tests:**
- Data collection services
- Content processing
- Broadcast generation
- Audio generation
- System monitoring

### **📰 Analyze News Only**

```bash
python production/radiox_master.py --action analyze_news [OPTIONS]
```

**Parameters:**
- `--channel` - Regional focus
- `--max-age` - News age limit

**Use Case:** Check available news without generating broadcast

---

## 🧹 Maintenance Commands

### **🗑️ Cleanup Old Data**

```bash
python production/radiox_master.py --action cleanup --cleanup-days 7
```

**Parameters:**
- `--cleanup-days` - Age threshold for cleanup (default: 7)

**Cleans:**
- Old broadcast files
- Temporary audio files
- Expired database entries

---

## 📊 Response Format

### **✅ Success Response**

```json
{
  "success": true,
  "broadcast": {
    "session_id": "uuid-string",
    "script_content": "MARCEL: Welcome to...",
    "broadcast_style": "Morning",
    "estimated_duration_minutes": 8,
    "generation_timestamp": "2024-01-01T12:00:00"
  },
  "audio_files": {
    "final_mp3": "path/to/final.mp3",
    "cover_art": "path/to/cover.png"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### **❌ Error Response**

```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## 🔄 Batch Processing

### **📅 Scheduled Generation**

```bash
# Cron job for regular broadcasts
0 6,12,18 * * * cd /app && python production/radiox_master.py --action generate_broadcast --generate-audio

# Hourly news analysis
0 * * * * cd /app && python production/radiox_master.py --action analyze_news
```

### **🔁 Multiple Shows**

```bash
#!/bin/bash
# Generate shows for different times
for time in "06:00" "12:00" "18:00" "22:00"; do
  python production/radiox_master.py \
    --action generate_broadcast \
    --time $time \
    --generate-audio
done
```

---

## 🧪 Development API

### **🔧 CLI Testing Interface**

```bash
# Master CLI for development
python cli/cli_master.py [ACTION]
```

**Actions:**
- `quick` - Fast end-to-end test
- `test` - All service tests
- `status` - System overview

### **🎯 Individual Service Testing**

```bash
# Test specific services
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test
python cli/cli_broadcast.py test
```

---

## 🔗 Integration Examples

### **🐍 Python Integration**

```python
import subprocess
import json

def generate_radio_show(time="08:00", language="en", audio=True):
    """Generate radio show programmatically"""
    
    cmd = [
        "python", "production/radiox_master.py",
        "--action", "generate_broadcast",
        "--time", time,
        "--language", language
    ]
    
    if audio:
        cmd.append("--generate-audio")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return {"success": True, "output": result.stdout}
    else:
        return {"success": False, "error": result.stderr}

# Usage
show = generate_radio_show(time="22:45", language="de", audio=True)
print(show)
```

### **🐳 Docker Integration**

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Generate show on container start
CMD ["python", "production/radiox_master.py", "--action", "generate_broadcast", "--generate-audio"]
```

### **☸️ Kubernetes CronJob**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: radiox-generator
spec:
  schedule: "0 6,12,18 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: radiox
            image: radiox/master:latest
            command:
            - python
            - production/radiox_master.py
            - --action
            - generate_broadcast
            - --generate-audio
          restartPolicy: OnFailure
```

---

## 🔧 Configuration API

### **⚙️ Environment Variables**

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
COINMARKETCAP_API_KEY=your_coinmarketcap_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional Voice Configuration
ELEVENLABS_MARCEL_VOICE_ID=custom_marcel_id
ELEVENLABS_JARVIS_VOICE_ID=custom_jarvis_id
```

### **🎛️ Runtime Configuration**

All parameters can be overridden at runtime:

```bash
# Override default settings
python production/radiox_master.py \
  --action generate_broadcast \
  --news-count 8 \
  --max-age 6 \
  --channel basel \
  --language de \
  --generate-audio
```

---

## 📈 Monitoring API

### **📊 System Metrics**

```bash
# Get system status
python production/radiox_master.py --action system_status
```

**Returns:**
- Service health status
- API key validation
- Database connectivity
- Recent performance metrics

### **📝 Log Analysis**

```bash
# Check logs directory
ls -la logs/

# View recent logs
tail -f logs/radiox_master_*.log
```

---

## 🔗 Related Guides

- **🎙️ [Show Generation](show-generation.md)** - User-friendly show creation
- **🎤 [Voice Configuration](voice-configuration.md)** - Audio setup
- **🏗️ [Architecture](../developer-guide/architecture.md)** - System design
- **🚀 [Production](../deployment/production.md)** - Deployment setup

---

<div align="center">

**📡 Ready for programmatic radio generation!**

[🏠 Documentation](../) • [🎙️ Show Generation](show-generation.md) • [💬 Get Help](../README.md#-support)

</div> 