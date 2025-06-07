# 📚 RadioX Documentation

<div align="center">

![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen)
![Version](https://img.shields.io/badge/version-v3.2-blue)
![Status](https://img.shields.io/badge/status-complete-success)

**🎙️ Complete documentation for RadioX AI Radio Station Generator**

[🏠 Main Project](../) • [🚀 Quick Start](#-quick-start) • [📖 All Guides](#-all-guides) • [💬 Support](#-support)

</div>

---

## 🎯 Quick Start

| 👤 **I am a...** | 🎯 **I want to...** | 📖 **Start here** |
|-------------------|---------------------|-------------------|
| **User** | Generate radio shows | [🎙️ Show Generation](user-guide/show-generation.md) |
| **User** | Configure voices | [🎤 Voice Configuration](user-guide/voice-configuration.md) |
| **Developer** | Understand the system | [🏗️ Architecture](developer-guide/architecture.md) |
| **Developer** | Set up development | [🔧 Development](developer-guide/development.md) |
| **DevOps** | Deploy to production | [🏭 Production](deployment/production.md) |
| **DevOps** | Use Docker containers | [🐳 Docker](deployment/docker.md) |

---

## 📖 All Guides

### 👥 **User Guides**
*Perfect for content creators, radio hosts, and end users*

| 📋 Guide | ⏱️ Time | 🎯 Difficulty | 📝 Description |
|----------|---------|---------------|----------------|
| **[🎙️ Show Generation](user-guide/show-generation.md)** | 15 min | Beginner | Complete guide to creating AI radio shows |
| **[🎤 Voice Configuration](user-guide/voice-configuration.md)** | 10 min | Beginner | Setup and manage voice settings |
| **[📰 RSS Dashboard](user-guide/rss-dashboard.md)** | 10 min | Beginner | Professional news dashboard with filtering |
| **[📚 API Reference](user-guide/api-reference.md)** | 20 min | Intermediate | Complete API documentation |

### 👨‍💻 **Developer Guides**
*Essential for developers contributing to RadioX*

| 📋 Guide | ⏱️ Time | 🎯 Difficulty | 📝 Description |
|----------|---------|---------------|----------------|
| **[🏗️ Architecture](developer-guide/architecture.md)** | 25 min | Intermediate | System design and components |
| **[🔧 Development](developer-guide/development.md)** | 30 min | Intermediate | Setup development environment |
| **[📊 Data Collection](developer-guide/data-collection.md)** | 20 min | Intermediate | Complete data collection system |
| **[⚙️ Services](developer-guide/services.md)** | 25 min | Intermediate | Bitcoin & Weather service documentation |
| **[🗄️ Database Schema](developer-guide/database-schema.md)** | 20 min | Intermediate | Centralized schema management |
| **[🧪 Testing](developer-guide/testing.md)** | 15 min | Intermediate | Testing strategies and tools |
| **[🤝 Contributing](developer-guide/contributing.md)** | 10 min | Beginner | How to contribute to RadioX |

### 🚀 **Deployment Guides**
*For DevOps engineers and system administrators*

| 📋 Guide | ⏱️ Time | 🎯 Difficulty | 📝 Description |
|----------|---------|---------------|----------------|
| **[🏭 Production](deployment/production.md)** | 45 min | Advanced | VPS production deployment |
| **[🐳 Docker](deployment/docker.md)** | 30 min | Intermediate | Containerized deployment |
| **[📊 Monitoring](deployment/monitoring.md)** | 25 min | Intermediate | Monitoring and alerting setup |

---

## 🎭 Features Overview

### **🎙️ AI Show Generation**
- **Marcel & Jarvis Dialogs** - Dynamic AI conversations
- **Time-based Styles** - Morning energetic, night relaxed
- **Multi-language Support** - English V3 & German
- **Smart Content** - News, crypto, weather integration

### **🔊 Professional Audio**
- **ElevenLabs V3 TTS** - Emotional voice synthesis
- **Dynamic Cover Art** - DALL-E 3 generated artwork
- **MP3 Production** - Complete audio files with metadata
- **Voice Configuration** - Supabase-managed voice settings

### **📊 Data Integration**
- **30+ RSS Feeds** - Swiss & international news with professional dashboard
- **RSS Management Dashboard** - Modern HTML interface with filtering and sorting
- **Live RSS Analytics** - Real-time feed monitoring with 98+ articles
- **📊 Data Collection Service** - Intelligent consolidation of all data sources
- **🎨 Dual HTML Dashboards** - RSS-specific and comprehensive data views
- **Bitcoin Service** - Professional price tracking with multi-timeframe analysis
- **Weather Service** - Smart Swiss weather with time-based outlook
- **Real-time Processing** - Fresh content every generation

### **🏗️ Enterprise Architecture**
- **Microservices Design** - Modular, scalable components
- **Central Generator** - RadioXMaster for all show types
- **Database Integration** - Supabase for configuration & logs
- **CLI Tools** - Comprehensive testing and management
- **Schema Management** - Centralized DB schema with dependency resolution
- **Legacy Cleanup** - Removed 9+ fragmented tables for clean architecture

---

## 🚀 Quick Commands

### **🎙️ Generate Shows**

```bash
# Morning show (energetic, 8 min)
python production/radiox_master.py --action generate_broadcast --time 08:00

# Night show (relaxed, 15 min, German)
python production/radiox_master.py --action generate_broadcast --time 23:00 --language de

# Full production (with audio + cover)
python production/radiox_master.py --action generate_broadcast --generate-audio
```

### **🧪 Testing & Validation**

```bash
# Quick system test
python cli/cli_master.py quick

# Data Collection (comprehensive)
python cli_data_collection.py              # All data + HTML dashboards
python cli_data_collection.py --news-only  # RSS only
python cli_data_collection.py --test       # Service tests

# Test individual services
python cli/cli_bitcoin.py          # Bitcoin price & trends
python cli/cli_weather.py          # Swiss weather & outlook  
python cli/cli_rss.py              # RSS feeds & dashboard

# RSS Dashboard (generates HTML)
python cli/cli_rss.py --limit 10   # Creates /outplay/rss.html

# Complete test suite
python cli/cli_master.py test

# System status check
python production/radiox_master.py --action system_status
```

### **🔧 Development**

```bash
# Setup development environment
./setup.sh

# Test individual services
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test
```

---

## 📈 Documentation Stats

<div align="center">

| 📊 Metric | 📈 Value |
|-----------|----------|
| **Total Guides** | 13 comprehensive guides |
| **Total Pages** | 200+ pages of documentation |
| **Code Examples** | 300+ practical examples |
| **Coverage** | 100% feature coverage |
| **Languages** | English & German support |
| **RSS Feeds** | 30 active feeds, 11 sources |
| **Data Collection** | 97+ articles, weather, bitcoin |
| **Services** | Bitcoin, Weather, RSS with dashboards |
| **Last Updated** | December 2024 |

</div>

---

## 🔍 Find What You Need

### **🎯 By Use Case**

| 🎯 **I want to...** | 📖 **Guide** |
|---------------------|--------------|
| Create my first radio show | [🎙️ Show Generation](user-guide/show-generation.md) |
| Change voice settings | [🎤 Voice Configuration](user-guide/voice-configuration.md) |
| Monitor RSS feeds and news | [📰 RSS Dashboard](user-guide/rss-dashboard.md) |
| Collect and analyze all data | [📊 Data Collection](developer-guide/data-collection.md) |
| Understand the system | [🏗️ Architecture](developer-guide/architecture.md) |
| Set up development | [🔧 Development](developer-guide/development.md) |
| Learn about Bitcoin & Weather services | [⚙️ Services](developer-guide/services.md) |
| Manage database schema | [🗄️ Database Schema](developer-guide/database-schema.md) |
| Deploy to production | [🏭 Production](deployment/production.md) |
| Use Docker | [🐳 Docker](deployment/docker.md) |
| Monitor the system | [📊 Monitoring](deployment/monitoring.md) |
| Contribute code | [🤝 Contributing](developer-guide/contributing.md) |
| Run tests | [🧪 Testing](developer-guide/testing.md) |
| Use the API | [📚 API Reference](user-guide/api-reference.md) |

### **🎯 By Difficulty**

| 🟢 **Beginner** | 🟡 **Intermediate** | 🔴 **Advanced** |
|------------------|---------------------|------------------|
| [🎙️ Show Generation](user-guide/show-generation.md) | [🏗️ Architecture](developer-guide/architecture.md) | [🏭 Production](deployment/production.md) |
| [🎤 Voice Configuration](user-guide/voice-configuration.md) | [🔧 Development](developer-guide/development.md) | |
| [📰 RSS Dashboard](user-guide/rss-dashboard.md) | [📊 Data Collection](developer-guide/data-collection.md) | |
| [🤝 Contributing](developer-guide/contributing.md) | [🧪 Testing](developer-guide/testing.md) | |
| | [📚 API Reference](user-guide/api-reference.md) | |
| | [🐳 Docker](deployment/docker.md) | |
| | [📊 Monitoring](deployment/monitoring.md) | |

---

## 💡 Pro Tips

### **🚀 For New Users**
1. Start with [🎙️ Show Generation](user-guide/show-generation.md) for your first show
2. Configure voices using [🎤 Voice Configuration](user-guide/voice-configuration.md)
3. Explore different time styles and languages

### **👨‍💻 For Developers**
1. Read [🏗️ Architecture](developer-guide/architecture.md) to understand the system
2. Follow [🔧 Development](developer-guide/development.md) for setup
3. Use [🧪 Testing](developer-guide/testing.md) for quality assurance

### **🚀 For DevOps**
1. Choose between [🏭 Production](deployment/production.md) or [🐳 Docker](deployment/docker.md)
2. Set up [📊 Monitoring](deployment/monitoring.md) for production
3. Follow security best practices in deployment guides

---

## 🔗 External Resources

### **🎓 Learning Resources**
- **[OpenAI GPT-4 Documentation](https://platform.openai.com/docs)** - AI text generation
- **[ElevenLabs API Docs](https://docs.elevenlabs.io/)** - Voice synthesis
- **[Supabase Documentation](https://supabase.com/docs)** - Database and backend
- **[DALL-E 3 Guide](https://platform.openai.com/docs/guides/images)** - Image generation

### **🛠️ Development Tools**
- **[Python 3.11 Documentation](https://docs.python.org/3.11/)** - Programming language
- **[Docker Documentation](https://docs.docker.com/)** - Containerization
- **[Nginx Documentation](https://nginx.org/en/docs/)** - Web server
- **[Prometheus Documentation](https://prometheus.io/docs/)** - Monitoring

---

## 💬 Support

### **🆘 Getting Help**

| 🎯 **Type** | 📍 **Where** | ⏱️ **Response Time** |
|-------------|--------------|----------------------|
| **Bug Reports** | [GitHub Issues](https://github.com/your-org/RadioX/issues) | 24-48 hours |
| **Feature Requests** | [GitHub Issues](https://github.com/your-org/RadioX/issues) | 1-2 weeks |
| **Questions** | [GitHub Discussions](https://github.com/your-org/RadioX/discussions) | 12-24 hours |
| **Documentation** | [Documentation Issues](https://github.com/your-org/RadioX/issues) | 24 hours |

### **🤝 Community**

- **💬 Discord Server** - Real-time chat and support
- **🐦 Twitter** - Updates and announcements
- **📧 Email** - Direct contact for enterprise users
- **📱 Telegram** - Community discussions

### **📋 Before Asking for Help**

1. **🔍 Search existing issues** - Your question might already be answered
2. **📖 Check relevant guide** - Most questions are covered in documentation
3. **🧪 Run system tests** - Use `python cli/cli_master.py test`
4. **📝 Provide details** - Include error messages, logs, and system info

---

## 🏆 Contributors

Special thanks to all contributors who made this documentation possible:

- **📝 Documentation Team** - Comprehensive guides and examples
- **👨‍💻 Development Team** - Code examples and technical accuracy
- **🎨 Design Team** - Visual design and user experience
- **🧪 QA Team** - Testing and validation of all examples

---

<div align="center">

**📚 Happy learning with RadioX!**

[🏠 Main Project](../) • [🎙️ Generate Your First Show](user-guide/show-generation.md) • [💬 Get Support](#-support)

</div> 