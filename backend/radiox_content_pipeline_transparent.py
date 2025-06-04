#!/usr/bin/env python3

"""
RadioX Content Pipeline - Transparente Analyse
Zeigt 1:1 die Produktions-Pipeline: Content → GPT → Voice
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


async def show_production_pipeline():
    """Zeigt die komplette Produktions-Pipeline transparent"""
    
    print("🎙️ RADIOX PRODUKTIONS-PIPELINE")
    print("=" * 80)
    print(f"⏰ Pipeline gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🏔️ Station: Züri Style (Produktion)")
    print()
    
    # SCHRITT 1: ECHTE DATEN SAMMELN
    print("📊 SCHRITT 1: CONTENT SAMMELN")
    print("-" * 50)
    
    # RSS News sammeln
    rss_parser = RSSParser()
    zueri_news = await rss_parser.get_zueri_style_feed()
    
    # Top 5 News für vollständige Analyse
    top_news = zueri_news[:5]
    
    print(f"✅ {len(top_news)} Top News gesammelt:")
    for i, news in enumerate(top_news, 1):
        print(f"   {i}. {news.source}: {news.title}")
    
    # Wetter sammeln
    weather_service = WeatherService()
    weather_data = await weather_service.get_weather_for_station("zurich")
    
    print(f"✅ Wetter: {weather_data.get('location')} - {weather_data['current'].temperature:.1f}°C")
    print()
    
    # SCHRITT 2: VOLLSTÄNDIGE CONTENT-ANALYSE
    print("📋 SCHRITT 2: VOLLSTÄNDIGE CONTENT-ANALYSE")
    print("-" * 50)
    
    # Content-Items formatieren
    content_items = []
    for news in top_news:
        content_items.append({
            'title': news.title,
            'summary': news.summary,
            'source_name': news.source,
            'category': news.category
        })
    
    print("📰 KOMPLETTE NEWS-INHALTE:")
    print("=" * 80)
    for i, item in enumerate(content_items, 1):
        print(f"📰 ARTIKEL {i}:")
        print(f"   QUELLE: {item['source_name']}")
        print(f"   KATEGORIE: {item['category']}")
        print(f"   TITEL: {item['title']}")
        print(f"   VOLLTEXT:")
        print(f"   {item['summary']}")
        print()
        print("-" * 60)
        print()
    
    print("🌤️ WETTER-VOLLTEXT:")
    print(f"   {weather_data.get('radio_current', 'Nicht verfügbar')}")
    print("=" * 80)
    print()
    
    # SCHRITT 3: GPT-PIPELINE ANALYSE
    print("🤖 SCHRITT 3: GPT-PIPELINE")
    print("-" * 50)
    
    # Züri Style Station holen
    zueri_station = get_station(RadioStationType.ZUERI_STYLE)
    
    # News Summarizer initialisieren
    news_summarizer = NewsSummarizer()
    
    print(f"📻 RADIOX SENDER: {zueri_station.display_name}")
    print(f"   Ton: {zueri_station.tone}")
    print(f"   Stil: {zueri_station.segment_style}")
    print(f"   Voice-ID: {zueri_station.voice_profile.voice_id}")
    print(f"   Voice-Name: {zueri_station.voice_profile.voice_name}")
    print()
    
    # SYSTEM-PROMPT ERSTELLEN
    system_prompt = news_summarizer._create_system_prompt(zueri_station)
    
    print("📝 SYSTEM-PROMPT (Produktions-Regeln):")
    print("=" * 80)
    print(system_prompt)
    print("=" * 80)
    print()
    
    # USER-PROMPT ERSTELLEN
    user_prompt = news_summarizer._create_user_prompt(
        content_items=content_items,
        weather_data=weather_data,
        station=zueri_station
    )
    
    print("📨 USER-PROMPT (Produktions-Daten):")
    print("=" * 80)
    print(user_prompt)
    print("=" * 80)
    print()
    
    # SCHRITT 4: GPT PRODUKTIONS-VEREDELUNG
    print("🎙️ SCHRITT 4: GPT PRODUKTIONS-VEREDELUNG")
    print("-" * 50)
    
    print("🔄 Sende an GPT-4o (Produktions-Modus)...")
    print("   Model: gpt-4o")
    print("   Temperature: 0.1")
    print("   Max Tokens: 2000")
    print()
    
    # Echte GPT-Antwort holen
    try:
        response = news_summarizer.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        gpt_response = response.choices[0].message.content.strip()
        
        print("🤖 GPT-4o PRODUKTIONS-ANTWORT:")
        print("=" * 80)
        print(gpt_response)
        print("=" * 80)
        print()
        
        # Token-Verbrauch zeigen
        usage = response.usage
        print(f"💰 PRODUKTIONS-KOSTEN:")
        print(f"   Input Tokens: {usage.prompt_tokens}")
        print(f"   Output Tokens: {usage.completion_tokens}")
        print(f"   Total Tokens: {usage.total_tokens}")
        print(f"   Geschätzte Kosten: ${(usage.total_tokens * 0.00001):.4f}")
        print()
        
    except Exception as e:
        print(f"❌ GPT-Fehler: {e}")
        gpt_response = "GPT-Antwort nicht verfügbar"
    
    # SCHRITT 5: PRODUKTIONS-SCRIPT ERSTELLEN
    print("✨ SCHRITT 5: PRODUKTIONS-SCRIPT")
    print("-" * 50)
    
    try:
        # Verwende die echte Produktions-Pipeline
        radio_script = await news_summarizer.create_radio_script_simple(
            content_items=content_items,
            station_type="zueri_style",
            weather_data=weather_data
        )
        
        print("📻 FINALES PRODUKTIONS-SCRIPT:")
        print("=" * 80)
        
        print("🎵 INTRO:")
        print(f"   {radio_script.get('intro', 'N/A')}")
        print()
        
        print("📰 NEWS-SEGMENTE (PRODUKTIONS-QUALITÄT):")
        for i, segment in enumerate(radio_script.get('segments', []), 1):
            print(f"   {i}. QUELLE: {segment.get('source', 'N/A')}")
            print(f"      RADIO-TEXT:")
            print(f"      {segment.get('text', 'N/A')}")
            print()
        
        if 'weather' in radio_script:
            print("🌤️ WETTER-SEGMENT:")
            print(f"   {radio_script['weather'].get('text', 'N/A')}")
            print()
        
        print("🎵 OUTRO:")
        print(f"   {radio_script.get('outro', 'N/A')}")
        print()
        
        # Produktions-Metadata
        metadata = radio_script.get('metadata', {})
        print("📊 PRODUKTIONS-METADATA:")
        print(f"   Geschätzte Dauer: {metadata.get('estimated_duration_seconds', 0)} Sekunden")
        print(f"   Total Items: {metadata.get('total_items', 0)}")
        print(f"   Pipeline-Modus: {metadata.get('mode', 'N/A')}")
        print(f"   AI-Model: {metadata.get('model_used', 'N/A')}")
        print(f"   Voice-ID: {zueri_station.voice_profile.voice_id}")
        print(f"   Bereit für ElevenLabs: ✅")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Produktions-Script Fehler: {e}")
    
    print()
    print("🚀 PRODUKTIONS-PIPELINE ÜBERSICHT:")
    print("=" * 80)
    print("1. 📊 Content sammeln (RSS, Wetter, Bitcoin)")
    print("2. 🎯 Station-spezifische Aufbereitung")
    print("3. 📝 GPT-4o Produktions-Veredelung")
    print("4. ✨ Radio-Script Strukturierung")
    print("5. 🎙️ ElevenLabs Voice-Generierung")
    print("6. 📻 Broadcast-ready Audio")
    print()
    print("🔗 PIPELINE: 'RadioX Content-to-Voice Production Pipeline'")
    print("🏗️ ARCHITEKTUR: RSS → GPT → ElevenLabs → Broadcast")
    print("💰 KOSTEN PRO STREAM: ~$0.01 (GPT) + ~$0.10 (ElevenLabs)")


if __name__ == "__main__":
    asyncio.run(show_production_pipeline()) 