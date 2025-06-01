# RadioX 🎙️🚀

**RadioX** ist ein AI-basiertes, voll konfigurierbares Radiosystem im Stil von GTA & Cyberpunk – personalisiert, modular, radikal anders.

## 💡 Idee
Ein individuell generierbarer Radiosender, der automatisch aus Musik, AI-generierten Voice-Overs, News und Pseudo-Werbung einen durchgehenden Stream produziert – abgestimmt auf die Präferenzen des Users.

## 🔧 Features
- 🎵 Musik-Input via Spotify API (Playlists oder Trends)
- 🗣 ElevenLabs Voice-TTS (mehrsprachig, verschiedene Sprecher)
- 📰 Nachrichten-Snippets & Werbung über GPT und RSS
- 🐦 **X (Twitter) Integration für Bitcoin OG News Breaks**
- 🤖 Personas: unterschiedliche Moderationsstile pro User
- 📦 Audio-Mix als MP3 oder Live-Stream (für Tesla, YouTube etc.)

## 🐦 X Integration - Bitcoin OG News Breaks

RadioX integriert **Live-Tweets von Bitcoin OGs** für authentische News Breaks im Cyberpunk-Stil.

### 🎯 VIP Accounts
Kuratierte Liste von Bitcoin-Influencern und Thought Leaders:
- **@saylor** - MicroStrategy CEO, Bitcoin Maximalist
- **@jack** - Twitter Gründer, Bitcoin Advocate  
- **@elonmusk** - Tesla CEO, Crypto Wildcard
- **@APompliano** - Bitcoin Podcaster & Investor
- **@PeterMcCormack** - What Bitcoin Did Host
- **@nvk** - Coinkite CEO, Hardware Security
- **@lopp** - Bitcoin Security Expert
- **@starkness** - Lightning Labs CEO
- **@pierre_rochard** - Bitcoin Developer & Educator

### 🔥 Content-Pipeline
```text
[X API] → [Tweet Filtering] → [Relevance Scoring] → [AI Summary] → [Voice Generation] → [Radio Integration]
```

### 🎙️ News Break Format
```
"Breaking aus dem Bitcoin-Space: Michael Saylor tweetet gerade über 
MicroStrategy's neueste Bitcoin-Käufe. Hier der O-Ton..."

[AI-generierte Zusammenfassung des Tweets]

"Das war euer Update aus der Bitcoin-Matrix. Weiter geht's mit Musik..."
```

### ⚙️ Technische Features
- **Real-time Monitoring**: Kontinuierliche Überwachung der VIP-Accounts
- **Relevance Scoring**: AI-basierte Bewertung der Tweet-Wichtigkeit
- **Auto-Summarization**: GPT-4 generiert Radio-taugliche Zusammenfassungen
- **Persona Integration**: News Breaks im Stil der gewählten Radio-Persona
- **Rate Limiting**: Respektvolle API-Nutzung mit Twitter Rate Limits
- **Fallback Content**: Backup-News bei API-Ausfällen

### 🎛️ Konfiguration
```yaml
x_integration:
  enabled: true
  update_interval: 300  # 5 Minuten
  max_tweets_per_hour: 12
  relevance_threshold: 0.7
  personas:
    maximalist: "Frech, direkt, Bitcoin-maximalistisch"
    cyberpunk: "Dystopisch, tech-fokussiert, Matrix-Style"
    retro: "80s Nostalgie mit Bitcoin-Twist"
```

// ... existing code ...
