#!/usr/bin/env python3

"""
RadioX Dual Speaker Fixed - Korrigiertes Zwei-Sprecher System
Marcel (Links) + Jarvis (Rechts) = Separate Audio mit korrektem Timing
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


class DualSpeakerFixed:
    """Korrigiertes Zwei-Sprecher Radio-System für RadioX"""
    
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
            "position": "left",
            "timing": 0,
            "duration": 4
        })
        
        segments.append({
            "speaker": "jarvis", 
            "type": "intro",
            "text": "Hier sind eure aktuellen News aus Zürich und der Welt.",
            "position": "right",
            "timing": 4,
            "duration": 4
        })
        
        segments.append({
            "speaker": "marcel",
            "type": "intro", 
            "text": "Ich bin Marcel...",
            "position": "left",
            "timing": 8,
            "duration": 2
        })
        
        segments.append({
            "speaker": "jarvis",
            "type": "intro",
            "text": "...und ich bin Jarvis. Heute haben wir einiges für euch!",
            "position": "right",
            "timing": 10,
            "duration": 4
        })
        
        # 2. NEWS-SEGMENTE (Abwechselnd)
        timing_offset = 14
        for i, item in enumerate(content_items[:3]):  # Top 3 News
            
            # Marcel macht lokale/allgemeine News
            if item.get('category') in ['lokale_news_schweiz', 'zurich', 'schweiz']:
                speaker = "marcel"
                position = "left"
                intro = f"Meldung {i+1}:"
            else:
                speaker = "jarvis" 
                position = "right"
                intro = f"Tech-Update {i+1}:"
            
            # News-Segment
            news_text = f"{intro} {item['title']}. {item['summary'][:150]}"
            segments.append({
                "speaker": speaker,
                "type": "news",
                "title": item['title'],
                "text": news_text,
                "position": position,
                "source": item['source_name'],
                "timing": timing_offset,
                "duration": 12
            })
            timing_offset += 12
            
            # Dialog-Reaktion vom anderen Sprecher
            if speaker == "marcel":
                reaction_speaker = "jarvis"
                reaction_pos = "right"
                reactions = [
                    "Interessant, Marcel. Das zeigt wieder wie wichtig lokale Themen sind.",
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
                    "position": reaction_pos,
                    "timing": timing_offset,
                    "duration": 4
                })
                timing_offset += 4
        
        # 3. BITCOIN (Jarvis übernimmt)
        segments.append({
            "speaker": "jarvis",
            "type": "bitcoin",
            "text": f"Moment, Marcel - ich übernehme mal die Krypto-News. Bitcoin-Fans, aufgepasst! Der Bitcoin steht bei {btc_data.price_usd:,.0f} US-Dollar, das sind {btc_data.change_24h:+.1f}% in 24 Stunden.",
            "position": "right",
            "timing": timing_offset,
            "duration": 8
        })
        timing_offset += 8
        
        segments.append({
            "speaker": "marcel", 
            "type": "reaction",
            "text": "Wow, da geht's ordentlich zur Sache auf dem Kryptomarkt!",
            "position": "left",
            "timing": timing_offset,
            "duration": 4
        })
        timing_offset += 4
        
        # 4. WETTER (Jarvis - Tech-Daten)
        weather_text = weather_data.get('radio_current', 'Wetter nicht verfügbar')
        
        segments.append({
            "speaker": "marcel",
            "type": "transition", 
            "text": "Und wie sieht's mit dem Wetter aus, Jarvis?",
            "position": "left",
            "timing": timing_offset,
            "duration": 3
        })
        timing_offset += 3
        
        segments.append({
            "speaker": "jarvis",
            "type": "weather",
            "text": f"Aktuell in Zürich: {weather_text}",
            "position": "right",
            "timing": timing_offset,
            "duration": 6
        })
        timing_offset += 6
        
        segments.append({
            "speaker": "marcel",
            "type": "reaction",
            "text": "Perfekt für einen Abendspaziergang!",
            "position": "left",
            "timing": timing_offset,
            "duration": 3
        })
        timing_offset += 3
        
        # 5. OUTRO (Dialog)
        segments.append({
            "speaker": "marcel",
            "type": "outro",
            "text": f"Das waren eure News um {time_str} Uhr...",
            "position": "left",
            "timing": timing_offset,
            "duration": 3
        })
        timing_offset += 3
        
        segments.append({
            "speaker": "jarvis",
            "type": "outro", 
            "text": "...bis zum nächsten Mal bei RadioX!",
            "position": "right",
            "timing": timing_offset,
            "duration": 3
        })
        
        return {
            "segments": segments,
            "metadata": {
                "broadcast_time": time_str,
                "time_of_day": time_of_day,
                "total_segments": len(segments),
                "marcel_segments": len([s for s in segments if s["speaker"] == "marcel"]),
                "jarvis_segments": len([s for s in segments if s["speaker"] == "jarvis"]),
                "estimated_duration": timing_offset + 3
            }
        }
    
    def generate_clean_speaker_texts(self, script):
        """Generiert saubere Texte für jeden Sprecher (OHNE Tags)"""
        
        marcel_segments = []
        jarvis_segments = []
        
        for segment in script["segments"]:
            if segment["speaker"] == "marcel":
                marcel_segments.append(segment["text"])
            else:
                jarvis_segments.append(segment["text"])
        
        # Saubere Texte ohne Tags
        marcel_text = " ... ".join(marcel_segments)  # Pausen zwischen Segmenten
        jarvis_text = " ... ".join(jarvis_segments)  # Pausen zwischen Segmenten
        
        return {
            "marcel": marcel_text,
            "jarvis": jarvis_text,
            "marcel_segments": marcel_segments,
            "jarvis_segments": jarvis_segments
        }
    
    def save_complete_script(self, script, content_items, weather_data, btc_data, output_dir):
        """Speichert das komplette Script als TXT-Datei"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        script_file = Path(output_dir) / f"RadioX_DualSpeaker_Fixed_Script_{timestamp}.txt"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX DUAL SPEAKER FIXED BROADCAST SCRIPT\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏰ Broadcast Zeit: {script['metadata']['broadcast_time']} Uhr {script['metadata']['time_of_day']}\n")
            f.write(f"🎭 Total Segmente: {script['metadata']['total_segments']}\n")
            f.write(f"⏱️ Geschätzte Dauer: {script['metadata']['estimated_duration']} Sekunden\n")
            f.write("\n")
            
            f.write("👥 SPRECHER-KONFIGURATION:\n")
            f.write("-" * 40 + "\n")
            f.write("🎤 MARCEL (Links): Hauptmoderator (lokal, warm, Zürich-fokussiert)\n")
            f.write("🤖 JARVIS (Rechts): Tech-Moderator (präzise, Bitcoin, Wetter, Analysen)\n")
            f.write("\n")
            
            f.write("📊 CONTENT-QUELLEN:\n")
            f.write("-" * 40 + "\n")
            for i, item in enumerate(content_items, 1):
                f.write(f"{i}. {item['title']} ({item['source_name']})\n")
            f.write(f"🌤️ Wetter: {weather_data['current'].temperature:.1f}°C in Zürich\n")
            f.write(f"₿ Bitcoin: ${btc_data.price_usd:,.0f} ({btc_data.change_24h:+.1f}%)\n")
            f.write("\n")
            
            f.write("🎬 DIALOG-SCRIPT (Timing + Dauer):\n")
            f.write("=" * 60 + "\n")
            
            for i, segment in enumerate(script["segments"], 1):
                speaker_icon = "🎤" if segment["speaker"] == "marcel" else "🤖"
                position = "L" if segment["position"] == "left" else "R"
                timing = segment.get("timing", 0)
                duration = segment.get("duration", 3)
                
                f.write(f"\n[{timing:02d}s-{timing+duration:02d}s] {i:2d}. {speaker_icon} {segment['speaker'].upper()} ({position}):\n")
                f.write(f"     {segment['text']}\n")
                
                if segment.get('title'):
                    f.write(f"     📰 Quelle: {segment.get('source', 'N/A')}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("🎧 AUDIO-MIXING ANWEISUNGEN:\n")
            f.write("- Marcel = Links (70% Pan)\n")
            f.write("- Jarvis = Rechts (70% Pan)\n")
            f.write("- Timing aus Script verwenden\n")
            f.write("- Separate Audio-Dateien überlagern\n")
            f.write("- Final Mix als RadioX_DualSpeaker_Stereo_[timestamp].mp3\n")
            f.write("\n")
            f.write("🔧 TECHNISCHE DETAILS:\n")
            f.write("- Marcel Audio: Nur Marcel's Segmente\n")
            f.write("- Jarvis Audio: Nur Jarvis's Segmente\n")
            f.write("- KEINE Tags oder Pause-Ansagen\n")
            f.write("- Saubere Audio-Trennung\n")
        
        return script_file


async def generate_fixed_dual_speaker_broadcast():
    """Hauptfunktion für korrigiertes Zwei-Sprecher Broadcast"""
    
    print("🎙️ RADIOX DUAL SPEAKER FIXED BROADCAST")
    print("=" * 60)
    print("👥 Marcel (Links) + Jarvis (Rechts) - KORRIGIERT")
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
    dual_system = DualSpeakerFixed()
    
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
    
    # SCHRITT 3: SCRIPT SPEICHERN
    print("📝 SCHRITT 3: SCRIPT SPEICHERN")
    print("-" * 40)
    
    output_dir = "D:/DEV/muraschal/RadioX/output"
    
    script_file = dual_system.save_complete_script(
        script=script,
        content_items=content_items,
        weather_data=weather_data,
        btc_data=btc_data,
        output_dir=output_dir
    )
    
    print(f"✅ Script gespeichert: {script_file.name}")
    print()
    
    # SCHRITT 4: SAUBERE SPRECHER-TEXTE GENERIEREN
    print("🔀 SCHRITT 4: SAUBERE SPRECHER-TEXTE")
    print("-" * 40)
    
    speaker_data = dual_system.generate_clean_speaker_texts(script)
    
    print(f"🎤 Marcel Text: {len(speaker_data['marcel'])} Zeichen")
    print(f"🤖 Jarvis Text: {len(speaker_data['jarvis'])} Zeichen")
    print(f"🎤 Marcel Segmente: {len(speaker_data['marcel_segments'])}")
    print(f"🤖 Jarvis Segmente: {len(speaker_data['jarvis_segments'])}")
    print()
    
    print("🎤 MARCEL'S SAUBERER TEXT:")
    print("=" * 50)
    print(speaker_data['marcel'][:200] + "...")
    print("=" * 50)
    print()
    
    print("🤖 JARVIS'S SAUBERER TEXT:")
    print("=" * 50)
    print(speaker_data['jarvis'][:200] + "...")
    print("=" * 50)
    print()
    
    # SCHRITT 5: AUDIO GENERIERUNG (Sauber getrennt)
    print("🎵 SCHRITT 5: SAUBERE AUDIO GENERIERUNG")
    print("-" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    print("🎤 Generiere Marcel's Audio (NUR Marcel, KEINE Tags)...")
    print(f"   Text: {speaker_data['marcel'][:100]}...")
    
    print("🤖 Generiere Jarvis's Audio (NUR Jarvis, KEINE Tags)...")
    print(f"   Text: {speaker_data['jarvis'][:100]}...")
    
    print()
    print("🎉 DUAL SPEAKER BROADCAST FIXED!")
    print("=" * 60)
    print(f"📝 Script: {script_file.name}")
    print("🎤 Marcel Audio: Bereit für ElevenLabs")
    print("🤖 Jarvis Audio: Bereit für ElevenLabs")
    print()
    print("✅ VERBESSERUNGEN:")
    print("   - KEINE [PAUSE] oder [JARVIS] Tags mehr")
    print("   - Saubere Trennung der Sprecher-Texte")
    print("   - Korrekte Timing-Informationen")
    print("   - Separate Audio-Generierung")
    print()
    print("🎧 NÄCHSTE SCHRITTE:")
    print("   1. Marcel Audio mit ElevenLabs generieren")
    print("   2. Jarvis Audio mit ElevenLabs generieren")
    print("   3. Audio-Mixing mit Timing aus Script")
    print("   4. Stereo-Positioning (Marcel Links, Jarvis Rechts)")
    
    return {
        "script": script,
        "speaker_data": speaker_data,
        "script_file": script_file
    }


if __name__ == "__main__":
    asyncio.run(generate_fixed_dual_speaker_broadcast()) 