#!/usr/bin/env python3

"""
RadioX Dual Speaker Complete - Vollständiges Zwei-Sprecher System
Marcel (Links) + Jarvis (Rechts) = Dynamisches Radio + Kombinierte Ausgabe
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


class DualSpeakerComplete:
    """Vollständiges Zwei-Sprecher Radio-System für RadioX"""
    
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
            "timing": 0
        })
        
        segments.append({
            "speaker": "jarvis", 
            "type": "intro",
            "text": "Hier sind eure aktuellen News aus Zürich und der Welt.",
            "position": "right",
            "timing": 4
        })
        
        segments.append({
            "speaker": "marcel",
            "type": "intro", 
            "text": "Ich bin Marcel...",
            "position": "left",
            "timing": 8
        })
        
        segments.append({
            "speaker": "jarvis",
            "type": "intro",
            "text": "...und ich bin Jarvis. Heute haben wir einiges für euch!",
            "position": "right",
            "timing": 10
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
            segments.append({
                "speaker": speaker,
                "type": "news",
                "title": item['title'],
                "text": f"{intro} {item['title']}. {item['summary'][:150]}",
                "position": position,
                "source": item['source_name'],
                "timing": timing_offset
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
                    "timing": timing_offset
                })
                timing_offset += 4
        
        # 3. BITCOIN (Jarvis übernimmt)
        segments.append({
            "speaker": "jarvis",
            "type": "bitcoin",
            "text": f"Moment, Marcel - ich übernehme mal die Krypto-News. Bitcoin-Fans, aufgepasst! Der Bitcoin steht bei {btc_data.price_usd:,.0f} US-Dollar, das sind {btc_data.change_24h:+.1f}% in 24 Stunden.",
            "position": "right",
            "timing": timing_offset
        })
        timing_offset += 8
        
        segments.append({
            "speaker": "marcel", 
            "type": "reaction",
            "text": "Wow, da geht's ordentlich zur Sache auf dem Kryptomarkt!",
            "position": "left",
            "timing": timing_offset
        })
        timing_offset += 4
        
        # 4. WETTER (Jarvis - Tech-Daten)
        weather_text = weather_data.get('radio_current', 'Wetter nicht verfügbar')
        
        segments.append({
            "speaker": "marcel",
            "type": "transition", 
            "text": "Und wie sieht's mit dem Wetter aus, Jarvis?",
            "position": "left",
            "timing": timing_offset
        })
        timing_offset += 3
        
        segments.append({
            "speaker": "jarvis",
            "type": "weather",
            "text": f"Aktuell in Zürich: {weather_text}",
            "position": "right",
            "timing": timing_offset
        })
        timing_offset += 6
        
        segments.append({
            "speaker": "marcel",
            "type": "reaction",
            "text": "Perfekt für einen Abendspaziergang!",
            "position": "left",
            "timing": timing_offset
        })
        timing_offset += 3
        
        # 5. OUTRO (Dialog)
        segments.append({
            "speaker": "marcel",
            "type": "outro",
            "text": f"Das waren eure News um {time_str} Uhr...",
            "position": "left",
            "timing": timing_offset
        })
        timing_offset += 3
        
        segments.append({
            "speaker": "jarvis",
            "type": "outro", 
            "text": "...bis zum nächsten Mal bei RadioX!",
            "position": "right",
            "timing": timing_offset
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
    
    def save_complete_script(self, script, content_items, weather_data, btc_data, output_dir):
        """Speichert das komplette Script als TXT-Datei"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        script_file = Path(output_dir) / f"RadioX_DualSpeaker_Script_{timestamp}.txt"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX DUAL SPEAKER BROADCAST SCRIPT\n")
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
            
            f.write("🎬 DIALOG-SCRIPT (Timing):\n")
            f.write("=" * 60 + "\n")
            
            for i, segment in enumerate(script["segments"], 1):
                speaker_icon = "🎤" if segment["speaker"] == "marcel" else "🤖"
                position = "L" if segment["position"] == "left" else "R"
                timing = segment.get("timing", 0)
                
                f.write(f"\n[{timing:02d}s] {i:2d}. {speaker_icon} {segment['speaker'].upper()} ({position}):\n")
                f.write(f"     {segment['text']}\n")
                
                if segment.get('title'):
                    f.write(f"     📰 Quelle: {segment.get('source', 'N/A')}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("🎧 AUDIO-MIXING ANWEISUNGEN:\n")
            f.write("- Marcel = Links (70% Pan)\n")
            f.write("- Jarvis = Rechts (70% Pan)\n")
            f.write("- Dialog-Pausen zwischen Sprechern beachten\n")
            f.write("- Final Mix als RadioX_DualSpeaker_Stereo_[timestamp].mp3\n")
        
        return script_file
    
    def generate_combined_text(self, script):
        """Generiert kombinierten Text für Audio-Generierung"""
        
        combined_text = ""
        
        for segment in script["segments"]:
            speaker_prefix = "[MARCEL]" if segment["speaker"] == "marcel" else "[JARVIS]"
            combined_text += f"{speaker_prefix} {segment['text']} [PAUSE] "
        
        return combined_text.strip()
    
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


async def generate_complete_dual_speaker_broadcast():
    """Hauptfunktion für komplettes Zwei-Sprecher Broadcast"""
    
    print("🎙️ RADIOX DUAL SPEAKER COMPLETE BROADCAST")
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
    dual_system = DualSpeakerComplete()
    
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
    
    # SCHRITT 4: SPRECHER-TEXTE TRENNEN
    print("🔀 SCHRITT 4: SPRECHER-TEXTE TRENNEN")
    print("-" * 40)
    
    speaker_texts = dual_system.generate_speaker_texts(script)
    combined_text = dual_system.generate_combined_text(script)
    
    print(f"🎤 Marcel Text: {len(speaker_texts['marcel'])} Zeichen")
    print(f"🤖 Jarvis Text: {len(speaker_texts['jarvis'])} Zeichen")
    print(f"🎭 Kombiniert: {len(combined_text)} Zeichen")
    print()
    
    # SCHRITT 5: AUDIO GENERIERUNG
    print("🎵 SCHRITT 5: AUDIO GENERIERUNG")
    print("-" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    print("🎤 Generiere Marcel's Audio (Links)...")
    try:
        from mcp_ElevenLabs_text_to_speech import mcp_ElevenLabs_text_to_speech
        
        marcel_result = mcp_ElevenLabs_text_to_speech(
            text=speaker_texts["marcel"],
            voice_id="owi9KfbgBi6A987h5eJH",
            stability=0.5,
            similarity_boost=0.8,
            style=0.3,
            use_speaker_boost=True,
            speed=1.0,
            output_directory=output_dir,
            output_format="mp3_44100_128"
        )
        print(f"✅ Marcel Audio: {marcel_result}")
        
    except Exception as e:
        print(f"⚠️ Marcel Audio via MCP nicht verfügbar: {e}")
        marcel_result = "Marcel_Audio_Placeholder.mp3"
    
    print("🤖 Generiere Jarvis's Audio (Rechts)...")
    try:
        jarvis_result = mcp_ElevenLabs_text_to_speech(
            text=speaker_texts["jarvis"],
            voice_id="dmLlPcdDHenQXbfM5tee",
            stability=0.6,
            similarity_boost=0.7,
            style=0.1,
            use_speaker_boost=True,
            speed=1.0,
            output_directory=output_dir,
            output_format="mp3_44100_128"
        )
        print(f"✅ Jarvis Audio: {jarvis_result}")
        
    except Exception as e:
        print(f"⚠️ Jarvis Audio via MCP nicht verfügbar: {e}")
        jarvis_result = "Jarvis_Audio_Placeholder.mp3"
    
    print()
    print("🎧 KOMBINIERTES AUDIO (Optional):")
    print("-" * 40)
    
    print("🎭 Generiere kombiniertes Dual-Speaker Audio...")
    try:
        combined_result = mcp_ElevenLabs_text_to_speech(
            text=combined_text,
            voice_id="owi9KfbgBi6A987h5eJH",  # Marcel als Hauptstimme
            stability=0.5,
            similarity_boost=0.8,
            style=0.2,
            use_speaker_boost=True,
            speed=1.0,
            output_directory=output_dir,
            output_format="mp3_44100_128"
        )
        print(f"✅ Kombiniertes Audio: {combined_result}")
        
    except Exception as e:
        print(f"⚠️ Kombiniertes Audio via MCP nicht verfügbar: {e}")
        combined_result = "Combined_Audio_Placeholder.mp3"
    
    print()
    print("🎉 DUAL SPEAKER BROADCAST KOMPLETT!")
    print("=" * 60)
    print(f"📝 Script: {script_file.name}")
    print(f"🎤 Marcel Audio: {marcel_result}")
    print(f"🤖 Jarvis Audio: {jarvis_result}")
    print(f"🎭 Kombiniert: {combined_result}")
    print()
    print("🎧 NÄCHSTE SCHRITTE:")
    print("   1. Script-TXT für Timing-Referenz verwenden")
    print("   2. Separate Audio-Dateien für Stereo-Mix")
    print("   3. Marcel = Links (70%), Jarvis = Rechts (70%)")
    print("   4. Dialog-Pausen zwischen Sprechern")
    print("   5. Final Mix als RadioX_DualSpeaker_Stereo_[timestamp].mp3")


if __name__ == "__main__":
    asyncio.run(generate_complete_dual_speaker_broadcast()) 