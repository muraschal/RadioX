#!/usr/bin/env python3

"""
RadioX Dual Speaker Broadcast - Zwei-Sprecher System
Marcel (Links) + Jarvis (Rechts) = Dynamisches Radio
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


class DualSpeakerBroadcast:
    """Zwei-Sprecher Radio-System für RadioX"""
    
    def __init__(self):
        # Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Deine Stimme (Deutsch)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis AI Style
        
        # Sprecher-Rollen
        self.marcel_role = "Hauptmoderator (lokal, warm, Zürich-fokussiert)"
        self.jarvis_role = "Tech-Moderator (präzise, Bitcoin, Wetter, Analysen)"
        
    def create_dual_speaker_script(self, content_items, weather_data, btc_data):
        """Erstellt Zwei-Sprecher Script mit Dialog"""
        
        # Aktuelle Zeit
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        # Tageszeit bestimmen
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "am Morgen"
        elif 12 <= hour < 17:
            time_of_day = "am Mittag"
        elif 17 <= hour < 22:
            time_of_day = "am Abend"
        else:
            time_of_day = "in der Nacht"
        
        # Script-Segmente
        segments = []
        
        # 1. INTRO (Dialog)
        segments.append({
            "speaker": "marcel",
            "type": "intro",
            "text": f"Grüezi und willkommen bei RadioX! Es ist {time_str} Uhr {time_of_day}.",
            "position": "left"
        })
        
        segments.append({
            "speaker": "jarvis", 
            "type": "intro",
            "text": "Hier sind eure aktuellen News aus Zürich und der Welt.",
            "position": "right"
        })
        
        segments.append({
            "speaker": "marcel",
            "type": "intro", 
            "text": "Ich bin Marcel...",
            "position": "left"
        })
        
        segments.append({
            "speaker": "jarvis",
            "type": "intro",
            "text": "...und ich bin Jarvis. Heute haben wir einiges für euch!",
            "position": "right"
        })
        
        # 2. NEWS-SEGMENTE (Abwechselnd)
        for i, item in enumerate(content_items[:3]):  # Top 3 News
            
            # Marcel macht lokale/allgemeine News
            if item.get('category') in ['lokale_news_schweiz', 'zurich', 'schweiz']:
                speaker = "marcel"
                position = "left"
                intro = f"Meldung {i+1}: {item['title'][:30]}..."
            else:
                speaker = "jarvis" 
                position = "right"
                intro = f"Tech-Update {i+1}: {item['title'][:30]}..."
            
            # News-Segment
            segments.append({
                "speaker": speaker,
                "type": "news",
                "title": item['title'],
                "text": f"{intro} {item['summary'][:200]}...",
                "position": position,
                "source": item['source_name']
            })
            
            # Dialog-Reaktion vom anderen Sprecher
            if speaker == "marcel":
                reaction_speaker = "jarvis"
                reaction_pos = "right"
                reactions = [
                    "Interessant, Marcel. Das zeigt wieder...",
                    "Spannend! Was denkst du, wie sich das entwickelt?",
                    "Das ist wirklich bemerkenswert, Marcel."
                ]
            else:
                reaction_speaker = "marcel"
                reaction_pos = "left" 
                reactions = [
                    "Wow, Jarvis! Das hätte ich nicht gedacht.",
                    "Krass, da geht's ordentlich zur Sache!",
                    "Das ist ja der Hammer, Jarvis!"
                ]
            
            if i < 2:  # Nicht bei letzter News
                segments.append({
                    "speaker": reaction_speaker,
                    "type": "reaction",
                    "text": reactions[i % len(reactions)],
                    "position": reaction_pos
                })
        
        # 3. BITCOIN (Jarvis übernimmt)
        segments.append({
            "speaker": "jarvis",
            "type": "bitcoin",
            "text": f"Moment, Marcel - ich übernehme mal die Krypto-News. Bitcoin-Fans, aufgepasst! Der Bitcoin steht bei {btc_data.price_usd:,.0f} US-Dollar, das sind {btc_data.change_24h:+.1f}% in 24 Stunden.",
            "position": "right"
        })
        
        segments.append({
            "speaker": "marcel", 
            "type": "reaction",
            "text": "Wow, da geht's ordentlich zur Sache auf dem Kryptomarkt!",
            "position": "left"
        })
        
        # 4. WETTER (Jarvis - Tech-Daten)
        weather_text = weather_data.get('radio_current', 'Wetter nicht verfügbar')
        
        segments.append({
            "speaker": "marcel",
            "type": "transition", 
            "text": "Und wie sieht's mit dem Wetter aus, Jarvis?",
            "position": "left"
        })
        
        segments.append({
            "speaker": "jarvis",
            "type": "weather",
            "text": f"Aktuell in Zürich: {weather_text}",
            "position": "right"
        })
        
        segments.append({
            "speaker": "marcel",
            "type": "reaction",
            "text": "Perfekt für einen Abendspaziergang!",
            "position": "left"
        })
        
        # 5. OUTRO (Dialog)
        segments.append({
            "speaker": "marcel",
            "type": "outro",
            "text": f"Das waren eure News um {time_str} Uhr...",
            "position": "left"
        })
        
        segments.append({
            "speaker": "jarvis",
            "type": "outro", 
            "text": "...bis zum nächsten Mal bei RadioX!",
            "position": "right"
        })
        
        return {
            "segments": segments,
            "metadata": {
                "broadcast_time": time_str,
                "time_of_day": time_of_day,
                "total_segments": len(segments),
                "marcel_segments": len([s for s in segments if s["speaker"] == "marcel"]),
                "jarvis_segments": len([s for s in segments if s["speaker"] == "jarvis"]),
                "estimated_duration": len(segments) * 8  # ~8 Sekunden pro Segment
            }
        }
    
    def generate_speaker_texts(self, script):
        """Trennt Script in separate Texte für jeden Sprecher"""
        
        marcel_text = ""
        jarvis_text = ""
        
        for segment in script["segments"]:
            if segment["speaker"] == "marcel":
                marcel_text += segment["text"] + " "
            else:
                jarvis_text += segment["text"] + " "
        
        return {
            "marcel": marcel_text.strip(),
            "jarvis": jarvis_text.strip()
        }
    
    async def generate_dual_audio(self, marcel_text, jarvis_text, output_dir):
        """Generiert separate Audio-Dateien für beide Sprecher"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        print("🎤 Generiere Marcel's Audio (Links)...")
        marcel_result = mcp_ElevenLabs_text_to_speech(
            text=marcel_text,
            voice_id=self.marcel_voice_id,
            stability=0.5,
            similarity_boost=0.8,
            style=0.3,
            use_speaker_boost=True,
            speed=1.0,
            output_directory=output_dir,
            output_format="mp3_44100_128"
        )
        
        print("🤖 Generiere Jarvis's Audio (Rechts)...")
        jarvis_result = mcp_ElevenLabs_text_to_speech(
            text=jarvis_text,
            voice_id=self.jarvis_voice_id,
            stability=0.6,
            similarity_boost=0.7,
            style=0.1,
            use_speaker_boost=True,
            speed=1.0,
            output_directory=output_dir,
            output_format="mp3_44100_128"
        )
        
        return {
            "marcel_file": marcel_result,
            "jarvis_file": jarvis_result,
            "timestamp": timestamp
        }


async def generate_dual_speaker_broadcast():
    """Hauptfunktion für Zwei-Sprecher Broadcast"""
    
    print("🎙️ RADIOX DUAL SPEAKER BROADCAST")
    print("=" * 60)
    print("👥 Marcel (Links) + Jarvis (Rechts)")
    print(f"⏰ Produktion gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # SCHRITT 1: CONTENT SAMMELN
    print("📊 SCHRITT 1: CONTENT SAMMELN")
    print("-" * 40)
    
    # RSS News sammeln
    rss_parser = RSSParser()
    zueri_news = await rss_parser.get_zueri_style_feed()
    top_news = zueri_news[:3]  # Top 3 für Dialog
    
    print(f"✅ {len(top_news)} Top News gesammelt")
    
    # Wetter sammeln
    weather_service = WeatherService()
    weather_data = await weather_service.get_weather_for_station("zurich")
    print(f"✅ Wetter: {weather_data['current'].temperature:.1f}°C")
    
    # Bitcoin sammeln
    btc_service = CoinMarketCapService()
    btc_data = await btc_service.get_bitcoin_price()
    print(f"✅ Bitcoin: ${btc_data.price_usd:,.0f} ({btc_data.change_24h:+.1f}%)")
    print()
    
    # SCHRITT 2: DUAL-SPEAKER SCRIPT ERSTELLEN
    print("🎭 SCHRITT 2: DUAL-SPEAKER SCRIPT")
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
    
    # Dual Speaker System initialisieren
    dual_system = DualSpeakerBroadcast()
    
    # Script erstellen
    script = dual_system.create_dual_speaker_script(
        content_items=content_items,
        weather_data=weather_data,
        btc_data=btc_data
    )
    
    print("✅ Dual-Speaker Script erstellt:")
    print(f"   Total Segmente: {script['metadata']['total_segments']}")
    print(f"   Marcel Segmente: {script['metadata']['marcel_segments']}")
    print(f"   Jarvis Segmente: {script['metadata']['jarvis_segments']}")
    print(f"   Geschätzte Dauer: {script['metadata']['estimated_duration']} Sekunden")
    print()
    
    # SCHRITT 3: SCRIPT ANZEIGEN
    print("📻 SCHRITT 3: DIALOG-SCRIPT PREVIEW")
    print("-" * 40)
    
    for i, segment in enumerate(script["segments"], 1):
        speaker_icon = "🎤" if segment["speaker"] == "marcel" else "🤖"
        position = "L" if segment["position"] == "left" else "R"
        
        print(f"{i:2d}. {speaker_icon} {segment['speaker'].upper()} ({position}): {segment['text'][:80]}...")
    
    print()
    
    # SCHRITT 4: SPRECHER-TEXTE TRENNEN
    print("🔀 SCHRITT 4: SPRECHER-TEXTE TRENNEN")
    print("-" * 40)
    
    speaker_texts = dual_system.generate_speaker_texts(script)
    
    print("🎤 MARCEL'S KOMPLETTER TEXT:")
    print("=" * 60)
    print(speaker_texts["marcel"])
    print("=" * 60)
    print()
    
    print("🤖 JARVIS'S KOMPLETTER TEXT:")
    print("=" * 60)
    print(speaker_texts["jarvis"])
    print("=" * 60)
    print()
    
    # SCHRITT 5: AUDIO GENERIERUNG
    print("🎵 SCHRITT 5: DUAL AUDIO GENERIERUNG")
    print("-" * 40)
    
    output_dir = "/d/DEV/muraschal/RadioX/output"
    
    try:
        audio_results = await dual_system.generate_dual_audio(
            marcel_text=speaker_texts["marcel"],
            jarvis_text=speaker_texts["jarvis"],
            output_dir=output_dir
        )
        
        print("✅ DUAL SPEAKER BROADCAST ERFOLGREICH!")
        print(f"🎤 Marcel Audio: {audio_results['marcel_file']}")
        print(f"🤖 Jarvis Audio: {audio_results['jarvis_file']}")
        print()
        print("🎧 NÄCHSTE SCHRITTE:")
        print("   1. Audio-Mixing für Stereo-Positioning")
        print("   2. Marcel = Links (70%), Jarvis = Rechts (70%)")
        print("   3. Dialog-Timing anpassen")
        print("   4. Final Mix als RadioX_DualSpeaker_[timestamp].mp3")
        
    except Exception as e:
        print(f"❌ Audio-Generierung Fehler: {e}")
        
        # Fallback: Texte speichern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        marcel_file = Path(output_dir) / f"RadioX_Marcel_{timestamp}.txt"
        jarvis_file = Path(output_dir) / f"RadioX_Jarvis_{timestamp}.txt"
        
        with open(marcel_file, 'w', encoding='utf-8') as f:
            f.write(f"RadioX Marcel (Links) - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            f.write(speaker_texts["marcel"])
        
        with open(jarvis_file, 'w', encoding='utf-8') as f:
            f.write(f"RadioX Jarvis (Rechts) - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            f.write(speaker_texts["jarvis"])
        
        print(f"📁 Texte gespeichert: {marcel_file.name}, {jarvis_file.name}")


if __name__ == "__main__":
    asyncio.run(generate_dual_speaker_broadcast()) 