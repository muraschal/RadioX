#!/usr/bin/env python3

"""
RadioX 19 Uhr Broadcast - Produktions-Pipeline
Generiert komplette 19 Uhr Ansage als MP3 für Broadcast
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.rss_parser import RSSParser
from src.services.weather_service import WeatherService
from src.services.coinmarketcap_service import CoinMarketCapService
from src.services.news_summarizer import NewsSummarizer
from src.models.radio_stations import RadioStationType, get_station


async def generate_19uhr_broadcast():
    """Generiert die komplette 19 Uhr Ansage als MP3"""
    
    print("🎙️ RADIOX 19 UHR BROADCAST PRODUKTION")
    print("=" * 60)
    print(f"⏰ Produktion gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📻 Station: Züri Style")
    print("🎯 Ziel: Broadcast-ready MP3")
    print()
    
    # SCHRITT 1: CONTENT SAMMELN
    print("📊 SCHRITT 1: CONTENT SAMMELN")
    print("-" * 40)
    
    # RSS News sammeln
    rss_parser = RSSParser()
    zueri_news = await rss_parser.get_zueri_style_feed()
    
    # Top 4 News für 19 Uhr
    top_news = zueri_news[:4]
    
    print(f"✅ {len(top_news)} Top News gesammelt:")
    for i, news in enumerate(top_news, 1):
        print(f"   {i}. {news.source}: {news.title[:60]}...")
    
    # Wetter sammeln
    weather_service = WeatherService()
    weather_data = await weather_service.get_weather_for_station("zurich")
    
    print(f"✅ Wetter: {weather_data.get('location')} - {weather_data['current'].temperature:.1f}°C")
    
    # Bitcoin sammeln
    btc_service = CoinMarketCapService()
    btc_data = await btc_service.get_bitcoin_price()
    
    print(f"✅ Bitcoin: ${btc_data.price_usd:,.0f} ({btc_data.change_24h:+.1f}%)")
    print()
    
    # SCHRITT 2: RADIO-SCRIPT ERSTELLEN
    print("📝 SCHRITT 2: RADIO-SCRIPT ERSTELLEN")
    print("-" * 40)
    
    # Content-Items formatieren
    content_items = []
    for news in top_news:
        content_items.append({
            'title': news.title,
            'summary': news.summary,
            'source_name': news.source,
            'category': news.category
        })
    
    # Bitcoin als News-Item hinzufügen
    content_items.append({
        'title': f'Bitcoin bei ${btc_data.price_usd:,.0f}',
        'summary': f'Bitcoin steht aktuell bei ${btc_data.price_usd:,.0f} US-Dollar, das entspricht einer Veränderung von {btc_data.change_24h:+.1f}% in den letzten 24 Stunden.',
        'source_name': 'CoinMarketCap',
        'category': 'bitcoin'
    })
    
    # News Summarizer
    news_summarizer = NewsSummarizer()
    
    # Radio-Script erstellen
    radio_script = await news_summarizer.create_radio_script_simple(
        content_items=content_items,
        station_type="zueri_style",
        weather_data=weather_data
    )
    
    print("✅ Radio-Script erstellt:")
    print(f"   Intro: {radio_script['intro'][:50]}...")
    print(f"   Segmente: {len(radio_script['segments'])}")
    print(f"   Wetter: {'✅' if 'weather' in radio_script else '❌'}")
    print(f"   Outro: {radio_script['outro'][:50]}...")
    print()
    
    # SCHRITT 3: KOMPLETTEN TEXT ZUSAMMENSTELLEN
    print("🎙️ SCHRITT 3: BROADCAST-TEXT ZUSAMMENSTELLEN")
    print("-" * 40)
    
    # Kompletten Radio-Text zusammenstellen
    full_text = radio_script['intro'] + " "
    
    # News-Segmente hinzufügen
    for segment in radio_script['segments']:
        full_text += segment['text'] + " "
    
    # Wetter hinzufügen
    if 'weather' in radio_script:
        full_text += radio_script['weather']['text'] + " "
    
    # Outro hinzufügen
    full_text += radio_script['outro']
    
    print("📻 KOMPLETTER BROADCAST-TEXT:")
    print("=" * 60)
    print(full_text)
    print("=" * 60)
    print()
    
    # Text-Statistiken
    word_count = len(full_text.split())
    estimated_duration = (word_count / 150) * 60  # 150 Wörter/Minute
    
    print(f"📊 TEXT-STATISTIKEN:")
    print(f"   Wörter: {word_count}")
    print(f"   Zeichen: {len(full_text)}")
    print(f"   Geschätzte Dauer: {estimated_duration:.1f} Sekunden")
    print()
    
    # SCHRITT 4: ELEVENLABS AUDIO GENERIERUNG
    print("🎵 SCHRITT 4: ELEVENLABS AUDIO GENERIERUNG")
    print("-" * 40)
    
    # Station für Voice-Konfiguration
    zueri_station = get_station(RadioStationType.ZUERI_STYLE)
    voice_id = zueri_station.voice_profile.voice_id
    voice_name = zueri_station.voice_profile.voice_name
    
    print(f"🎤 Voice: {voice_name}")
    print(f"🆔 Voice-ID: {voice_id}")
    print()
    
    # Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"RadioX_ZueriStyle_19Uhr_{timestamp}.mp3"
    output_path = f"../output/{filename}"
    
    print(f"📁 Output: {filename}")
    print("🔄 Generiere Audio mit ElevenLabs...")
    
    try:
        # ElevenLabs Text-to-Speech mit MCP
        print("🔄 Rufe ElevenLabs MCP auf...")
        
        # Verwende die MCP ElevenLabs Funktion direkt
        result = mcp_ElevenLabs_text_to_speech(
            text=full_text,
            voice_id=voice_id,
            stability=0.5,
            similarity_boost=0.8,
            style=0.2,
            use_speaker_boost=True,
            speed=1.0,
            output_directory="../output",
            output_format="mp3_44100_128"
        )
        
        print("✅ Audio erfolgreich generiert!")
        print(f"📁 Datei: {filename}")
        print()
        
        # SCHRITT 5: BROADCAST-READY BESTÄTIGUNG
        print("🚀 SCHRITT 5: BROADCAST-READY")
        print("-" * 40)
        
        print("✅ 19 UHR ANSAGE ERFOLGREICH ERSTELLT!")
        print(f"📻 Datei: {filename}")
        print(f"⏱️ Dauer: ~{estimated_duration:.1f} Sekunden")
        print(f"🎤 Voice: {voice_name} (Deutsch optimiert)")
        print(f"📊 Content: {len(radio_script['segments'])} News + Wetter + Bitcoin")
        print(f"🕖 Sendezeit: 19:00 Uhr")
        print()
        print("🎙️ BEREIT FÜR BROADCAST!")
        
    except Exception as e:
        print(f"❌ ElevenLabs Fehler: {e}")
        print("💡 Fallback: Text wurde erstellt, Audio-Generierung über MCP erforderlich")
        
        # Text als Fallback speichern
        text_filename = f"RadioX_ZueriStyle_19Uhr_{timestamp}.txt"
        text_path = Path("../output") / text_filename
        
        # Output-Verzeichnis erstellen falls nicht vorhanden
        text_path.parent.mkdir(exist_ok=True)
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"RadioX Züri Style - 19 Uhr Ansage\n")
            f.write(f"Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Voice: {voice_name} ({voice_id})\n")
            f.write("=" * 60 + "\n\n")
            f.write(full_text)
        
        print(f"📁 Text gespeichert: {text_filename}")
        print("🎤 Für Audio-Generierung verwende ElevenLabs MCP mit diesem Text!")


if __name__ == "__main__":
    asyncio.run(generate_19uhr_broadcast()) 