# 🧪 Testing Guide

<div align="center">

![Developer Guide](https://img.shields.io/badge/guide-developer-purple)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-15%20min-orange)

**🔬 Complete guide to testing strategies and tools in RadioX**

[🏠 Documentation](../) • [👨‍💻 Developer Guides](../README.md#-developer-guides) • [🏗️ Architecture](architecture.md) • [🔧 Development](development.md)

</div>

---

## 🎯 Overview

RadioX implements a **4-level testing strategy** from unit tests to production validation, ensuring reliability at every layer of the system.

### ✨ **Testing Philosophy**
- 🔬 **Unit Tests** - Individual service validation
- 🔗 **Integration Tests** - Service interaction testing
- 🎯 **System Tests** - End-to-end workflow validation
- 🚀 **Production Tests** - Live environment monitoring

---

## 🔬 4-Level Testing Strategy

### **Level 1: Unit Tests**

**Purpose:** Test individual services in isolation

```bash
# Test specific services
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test
python cli/cli_broadcast.py test
python cli/cli_image.py test
python cli/cli_weather.py test
```

**What's Tested:**
- API connectivity
- Service initialization
- Basic functionality
- Error handling

### **Level 2: Integration Tests**

**Purpose:** Test service interactions and data flow

```bash
# Master CLI integration testing
python cli/cli_master.py test

# Specific integration workflows
python cli/cli_master.py quick
python cli/cli_overview.py
```

**What's Tested:**
- Service-to-service communication
- Data transformation pipelines
- Configuration management
- Voice configuration integration

### **Level 3: System Tests**

**Purpose:** End-to-end workflow validation

```bash
# Complete system test
python production/radiox_master.py --action test_services

# Broadcast generation test
python production/radiox_master.py --action generate_broadcast --news-count 2

# Audio generation test
python production/radiox_master.py --action generate_broadcast --generate-audio --news-count 1
```

**What's Tested:**
- Complete broadcast generation
- Audio production pipeline
- Cover art generation
- Database integration

### **Level 4: Production Tests**

**Purpose:** Live environment validation

```bash
# System status check
python production/radiox_master.py --action system_status

# News analysis validation
python production/radiox_master.py --action analyze_news

# Cleanup functionality
python production/radiox_master.py --action cleanup --cleanup-days 7
```

**What's Tested:**
- Production environment health
- API key validation
- Database connectivity
- System performance metrics

---

## 🛠️ Testing Tools & Commands

### **🎛️ Master CLI Testing**

```bash
# Quick end-to-end test (fast)
python cli/cli_master.py quick

# Complete service test suite
python cli/cli_master.py test

# System status overview
python cli/cli_master.py status
```

### **🔊 Audio Testing**

```bash
# Test ElevenLabs connection
python cli/cli_audio.py test

# Test voice configuration
python cli/cli_voice.py test marcel
python cli/cli_voice.py test jarvis

# Voice statistics
python cli/cli_voice.py stats
```

### **📰 Data Collection Testing**

```bash
# Test RSS feeds
python cli/cli_rss.py test

# Test crypto data
python cli/cli_crypto.py test

# Test weather service
python cli/cli_weather.py test
```

### **🎨 Image Generation Testing**

```bash
# Test DALL-E integration
python cli/cli_image.py test

# Test cover art generation
python cli/cli_image.py generate --prompt "morning radio show"
```

---

## 🧪 Test Scenarios

### **🌅 Morning Show Test**

```bash
# Test morning style generation
python production/radiox_master.py \
  --action generate_broadcast \
  --time 08:00 \
  --news-count 2 \
  --generate-audio
```

**Expected Results:**
- Energetic, motivational script
- 8-minute duration
- Morning-themed cover art
- High-quality audio output

### **🌙 Night Show Test**

```bash
# Test night style generation
python production/radiox_master.py \
  --action generate_broadcast \
  --time 23:00 \
  --news-count 2 \
  --language de \
  --generate-audio
```

**Expected Results:**
- Calm, relaxed script
- 15-minute duration
- Night-themed cover art
- German language output

### **🔄 Multi-Language Test**

```bash
# Test English generation
python production/radiox_master.py --action generate_broadcast --language en --news-count 1

# Test German generation
python production/radiox_master.py --action generate_broadcast --language de --news-count 1
```

### **📊 Performance Test**

```bash
# Test with maximum news
python production/radiox_master.py \
  --action generate_broadcast \
  --news-count 6 \
  --max-age 3 \
  --generate-audio
```

---

## 🔍 Test Validation

### **✅ Success Criteria**

#### **Unit Tests:**
- [ ] All services return `True` for test methods
- [ ] API connections established successfully
- [ ] No exceptions during initialization

#### **Integration Tests:**
- [ ] Data flows correctly between services
- [ ] Voice configurations load from Supabase
- [ ] Content processing completes without errors

#### **System Tests:**
- [ ] Complete broadcast generated
- [ ] Audio file created (MP3 format)
- [ ] Cover art embedded in MP3
- [ ] Script saved to output directory

#### **Production Tests:**
- [ ] All API keys validated
- [ ] Database connectivity confirmed
- [ ] System metrics within normal ranges

### **❌ Failure Indicators**

| 🚨 Issue | 🔍 Cause | ✅ Solution |
|----------|----------|-------------|
| Service test fails | Missing API key | Check `.env` configuration |
| Audio generation fails | ElevenLabs quota | Check account credits |
| Image generation fails | OpenAI API issue | Verify API key and credits |
| Database errors | Supabase connection | Check URL and keys |
| Voice config errors | Missing voice IDs | Update voice configuration |

---

## 📊 Test Reports

### **🎯 CLI Test Output Example**

```bash
$ python cli/cli_master.py test

🧪 RadioX Master Test Suite
===========================

📊 Data Collection Services:
   ✅ RSS Service: 25 feeds accessible
   ✅ Crypto Service: Bitcoin data retrieved
   ✅ Weather Service: Zurich weather available

🔊 Audio Services:
   ✅ ElevenLabs API: Connected
   ✅ Voice Config: Marcel & Jarvis loaded
   ✅ Audio Generation: Test successful

🎨 Image Services:
   ✅ OpenAI DALL-E: Connected
   ✅ Cover Generation: Test successful

🗄️ Database Services:
   ✅ Supabase: Connected
   ✅ Tables: All accessible

🎉 ALL TESTS PASSED! System ready for production.
```

### **📈 System Status Report**

```bash
$ python production/radiox_master.py --action system_status

📊 RadioX System Status Report
==============================

🔑 API Keys Status:
   ✅ OpenAI: Valid (GPT-4 & DALL-E access)
   ✅ ElevenLabs: Valid (12,450 characters remaining)
   ✅ CoinMarketCap: Valid (Pro plan)
   ✅ Weather API: Valid (1,000 calls/day)

🗄️ Database Status:
   ✅ Supabase: Connected (eu-central-1)
   ✅ Tables: 5/5 accessible
   ✅ Recent Activity: 23 broadcasts in last 7 days

📊 Performance Metrics:
   ⏱️ Avg Generation Time: 45 seconds
   🎵 Avg Audio Duration: 12 minutes
   📁 Storage Used: 2.3 GB
   🔄 Success Rate: 98.7%

🎉 SYSTEM HEALTHY! Ready for production use.
```

---

## 🚨 Troubleshooting Tests

### **Common Test Failures**

#### **🔊 Audio Test Failures**

```bash
# Diagnose ElevenLabs issues
python cli/cli_audio.py test --verbose

# Check voice configuration
python cli/cli_voice.py list
python cli/cli_voice.py stats
```

#### **📰 Data Collection Failures**

```bash
# Test individual RSS feeds
python cli/cli_rss.py test --source "srf"

# Check crypto API
python cli/cli_crypto.py test --verbose

# Validate weather service
python cli/cli_weather.py test --city zurich
```

#### **🗄️ Database Connection Issues**

```bash
# Test Supabase connection
python cli/cli_master.py status

# Check table accessibility
python backend/check_tables.py
```

### **🔧 Debug Commands**

```bash
# Verbose testing with debug output
python cli/cli_master.py test --verbose

# Check system logs
python cli/cli_logging.py --action reports

# Monitor system performance
python cli/cli_overview.py --detailed
```

---

## 💡 Testing Best Practices

### **🎯 Development Testing**

1. **Start Small:** Begin with unit tests for new features
2. **Test Early:** Run tests during development, not after
3. **Use Real Data:** Test with actual news feeds and API responses
4. **Voice Testing:** Always test voice changes with actual audio generation
5. **Clean Environment:** Use fresh `.env` for testing

### **⚡ Quick Testing Workflows**

```bash
# Daily development workflow
python cli/cli_master.py quick

# Before committing changes
python cli/cli_master.py test

# Before production deployment
python production/radiox_master.py --action test_services

# After production deployment
python production/radiox_master.py --action system_status
```

### **🔄 Continuous Testing**

```bash
# Automated testing script
#!/bin/bash
echo "🧪 Running RadioX Test Suite..."

# Level 1: Unit Tests
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test

# Level 2: Integration Tests
python cli/cli_master.py test

# Level 3: System Test
python production/radiox_master.py --action generate_broadcast --news-count 1

echo "✅ All tests completed!"
```

---

## 🔗 Related Guides

- **🏗️ [Architecture](architecture.md)** - Understand the system design
- **🔧 [Development](development.md)** - Development setup and workflows
- **🤝 [Contributing](contributing.md)** - Code standards and workflow
- **🚀 [Production](../deployment/production.md)** - Deploy tested code

---

<div align="center">

**🧪 Test with confidence, deploy with certainty!**

[🏠 Documentation](../) • [🔧 Development](development.md) • [💬 Get Help](../README.md#-support)

</div> 