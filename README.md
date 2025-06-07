# RadioX - AI Radio Station Generator

<div align="center">

![Release](https://img.shields.io/badge/release-v3.1-brightgreen)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Chat](https://img.shields.io/badge/chat-on%20discord-7289da)
![API](https://img.shields.io/badge/api-reference-orange)
![Report](https://img.shields.io/badge/go%20report-A+-brightgreen)

**🎙️ Vollautomatisierte AI-Radio-Station mit KI-generierten Shows, Audio und Cover-Art**

[🚀 Quick Start](#-quick-start) • [📚 Documentation](docs/) • [🎭 Live Demo](#-live-demo) • [🤝 Contributing](docs/developer-guide/contributing.md)

</div>

---

## ✨ Features

🎙️ **AI-Generated Shows** - Marcel & Jarvis Dialoge mit GPT-4  
🔊 **Professional Audio** - ElevenLabs V3 TTS mit emotionalen Tags  
🎨 **Dynamic Cover Art** - DALL-E 3 generierte Cover mit MP3-Embedding  
📰 **Real-time News** - 25+ RSS-Feeds aus Schweiz & International  
₿ **Crypto Integration** - Live Bitcoin/Crypto-Daten von CoinMarketCap  
🌤️ **Weather Updates** - Lokale Wetter-Integration für Schweizer Städte  
🕐 **Smart Scheduling** - Automatische Stil-Anpassung nach Tageszeit  
🌐 **Multi-language** - English V3 & German Support  

## 🚀 Quick Start

```bash
# 1. Clone & Setup
git clone https://github.com/your-org/RadioX.git
cd RadioX/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure Environment
cp env_template.txt .env
# Add your API keys (OpenAI, ElevenLabs, etc.)

# 3. Generate Your First Show
python production/radiox_master.py --action generate_broadcast --generate-audio
```

**🎯 That's it!** Your AI radio show is ready in `backend/output/`

## 📚 Documentation

| 📖 Guide | 🎯 For | 📝 Description |
|----------|--------|----------------|
| **[📋 Documentation Index](docs/)** | Everyone | Complete navigation to all guides |
| **[🎙️ Show Generation](docs/user-guide/show-generation.md)** | Users | How to create radio shows |
| **[🎤 Voice Configuration](docs/user-guide/voice-configuration.md)** | Users | Setup voices & audio settings |
| **[🏗️ Architecture](docs/developer-guide/architecture.md)** | Developers | System design & components |
| **[🔧 Development](docs/developer-guide/development.md)** | Developers | Setup development environment |
| **[🚀 Production](docs/deployment/production.md)** | DevOps | Deploy to production |

## 🎭 Live Demo

```bash
# 🌅 Morning Show (energetic, 8 min)
python production/radiox_master.py --action generate_broadcast --time 08:00

# 🌙 Night Show (relaxed, 15 min) 
python production/radiox_master.py --action generate_broadcast --time 23:00 --language de

# 🎨 Full Production (with audio + cover)
python production/radiox_master.py --action generate_broadcast --generate-audio
```

## 🏗️ Architecture

```
📻 RadioX - Enterprise AI Radio Platform
├── 🎭 AI Script Generation (GPT-4)
├── 🔊 Audio Production (ElevenLabs V3)
├── 🎨 Cover Art Creation (DALL-E 3)
├── 📊 Data Collection (RSS, Crypto, Weather)
├── 🗄️ Database (Supabase)
└── 🌐 Web Interface (Next.js)
```

**[📖 Detailed Architecture →](docs/developer-guide/architecture.md)**

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer-guide/contributing.md) for details.

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔄 Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 & DALL-E 3
- **ElevenLabs** for V3 TTS Technology
- **Supabase** for Database & Backend
- **Swiss Media** for RSS Feed Sources

---

<div align="center">

**Made with ❤️ by the RadioX Team**

[📚 Documentation](docs/) • [🐛 Report Bug](https://github.com/your-org/RadioX/issues) • [💡 Request Feature](https://github.com/your-org/RadioX/issues)

</div>
