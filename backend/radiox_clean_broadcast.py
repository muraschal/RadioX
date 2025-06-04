#!/usr/bin/env python3

"""
RadioX Clean Broadcast - Sauberes Zwei-Sprecher System
Jarvis (Cool Start) + Marcel = KEINE Pause-Tags mehr!
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


class CleanBroadcast:
    """Sauberes Broadcast-System ohne Pause-Tags"""
    
    def __init__(self):
        # Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Deine Stimme (Deutsch)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis AI Style (Cool!)
        
        # Output-Verzeichnis
        self.output_dir = Path("D:/DEV/muraschal/RadioX/output")
        self.output_dir.mkdir(exist_ok=True)
        
    async def collect_latest_content(self):
        """Sammelt die neuesten Inhalte mit Fehlerbehandlung"""
        
        print("📊 SAMMLE NEUESTE INHALTE")
        print("-" * 40)
        
        content = {
            "news": [],
            "weather": None,
            "bitcoin": None,
            "errors": []
        }
        
        # RSS News sammeln
        try:
            print("📰 Sammle RSS News...")
            rss_parser = RSSParser()
            zueri_news = await rss_parser.get_zueri_style_feed()
            content["news"] = zueri_news[:4]  # Top 4 für mehr Auswahl
            print(f"✅ {len(content['news'])} News gesammelt")
            
            # Debug: Zeige News-Kategorien
            for i, news in enumerate(content["news"], 1):
                print(f"   {i}. {news.title[:50]}... ({news.category})")
                
        except Exception as e:
            error_msg = f"RSS News Fehler: {str(e)}"
            content["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        # Wetter sammeln
        try:
            print("🌤️ Sammle Wetter...")
            weather_service = WeatherService()
            weather_data = await weather_service.get_weather_for_station("zurich")
            content["weather"] = weather_data
            print(f"✅ Wetter: {weather_data['current'].temperature:.1f}°C")
            
        except Exception as e:
            error_msg = f"Wetter Fehler: {str(e)}"
            content["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            # Fallback Wetter
            content["weather"] = {
                "current": type('obj', (object,), {"temperature": 20.0})(),
                "radio_current": "Wetter nicht verfügbar"
            }
        
        # Bitcoin sammeln
        try:
            print("₿ Sammle Bitcoin...")
            btc_service = CoinMarketCapService()
            btc_data = await btc_service.get_bitcoin_price()
            content["bitcoin"] = btc_data
            print(f"✅ Bitcoin: ${btc_data.price_usd:,.0f} ({btc_data.change_24h:+.1f}%)")
            
        except Exception as e:
            error_msg = f"Bitcoin Fehler: {str(e)}"
            content["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            # Fallback Bitcoin
            content["bitcoin"] = type('obj', (object,), {
                "price_usd": 106000,
                "change_24h": 1.5
            })()
        
        print()
        if content["errors"]:
            print("⚠️ FEHLER AUFGETRETEN:")
            for error in content["errors"]:
                print(f"   - {error}")
            print()
        
        return content
    
    def create_clean_script(self, content):
        """Erstellt Script mit Jarvis als coolem Starter"""
        
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
        timing = 0
        
        # 1. INTRO - JARVIS STARTET COOL! 😎
        segments.append({
            "speaker": "jarvis",
            "text": f"RadioX ist live! Es ist {time_str} Uhr {time_of_day}. Hier ist Jarvis mit den neuesten Updates.",
            "timing": timing,
            "duration": 5
        })
        timing += 5
        
        segments.append({
            "speaker": "marcel",
            "text": "Grüezi! Und ich bin Marcel. Zusammen bringen wir euch die aktuellen News aus Zürich und der Welt.",
            "timing": timing,
            "duration": 5
        })
        timing += 5
        
        segments.append({
            "speaker": "jarvis",
            "text": "Perfekt, Marcel! Los geht's mit den Top-Meldungen.",
            "timing": timing,
            "duration": 3
        })
        timing += 3
        
        # 2. NEWS (Intelligente Zuordnung)
        if content["news"]:
            for i, news in enumerate(content["news"][:3]):  # Top 3
                
                # Sprecher-Zuordnung basierend auf Kategorie
                if news.category in ['zurich', 'schweiz', 'lokale_news_schweiz']:
                    speaker = "marcel"
                    intro = f"Lokale News {i+1}:"
                else:
                    speaker = "jarvis"
                    intro = f"Update {i+1}:"
                
                # News-Text (gekürzt für bessere Verständlichkeit)
                news_text = f"{intro} {news.title}. {news.summary[:120]}"
                
                segments.append({
                    "speaker": speaker,
                    "text": news_text,
                    "timing": timing,
                    "duration": 15,
                    "source": news.source,
                    "category": news.category
                })
                timing += 15
                
                # Dialog-Reaktion (nur bei ersten 2 News)
                if i < 2:
                    if speaker == "marcel":
                        reaction_speaker = "jarvis"
                        reactions = [
                            "Interessant, Marcel! Das bewegt wirklich die Leute.",
                            "Spannende Entwicklung in Zürich, Marcel!"
                        ]
                    else:
                        reaction_speaker = "marcel"
                        reactions = [
                            "Wow, das ist wirklich bemerkenswert, Jarvis!",
                            "Da passiert einiges, Jarvis!"
                        ]
                    
                    segments.append({
                        "speaker": reaction_speaker,
                        "text": reactions[i % len(reactions)],
                        "timing": timing,
                        "duration": 3
                    })
                    timing += 3
        
        # 3. BITCOIN (Jarvis - Tech Expert)
        if content["bitcoin"]:
            segments.append({
                "speaker": "jarvis",
                "text": f"Krypto-Update: Bitcoin steht bei {content['bitcoin'].price_usd:,.0f} US-Dollar, das sind {content['bitcoin'].change_24h:+.1f}% in 24 Stunden.",
                "timing": timing,
                "duration": 8
            })
            timing += 8
            
            segments.append({
                "speaker": "marcel",
                "text": "Die Krypto-Welt bleibt spannend, Jarvis!",
                "timing": timing,
                "duration": 3
            })
            timing += 3
        
        # 4. WETTER
        if content["weather"]:
            weather_text = content["weather"].get("radio_current", "Wetter nicht verfügbar")
            
            segments.append({
                "speaker": "marcel",
                "text": "Wie sieht's mit dem Wetter aus, Jarvis?",
                "timing": timing,
                "duration": 3
            })
            timing += 3
            
            segments.append({
                "speaker": "jarvis",
                "text": f"Aktuell in Zürich: {weather_text}",
                "timing": timing,
                "duration": 6
            })
            timing += 6
            
            segments.append({
                "speaker": "marcel",
                "text": "Perfekt für den Tag!",
                "timing": timing,
                "duration": 2
            })
            timing += 2
        
        # 5. OUTRO - JARVIS BEENDET COOL
        segments.append({
            "speaker": "marcel",
            "text": f"Das waren die News um {time_str} Uhr, Marcel hier.",
            "timing": timing,
            "duration": 3
        })
        timing += 3
        
        segments.append({
            "speaker": "jarvis",
            "text": "Und Jarvis. Bleibt dran bei RadioX - wir sind zurück mit mehr Updates!",
            "timing": timing,
            "duration": 4
        })
        timing += 4
        
        return {
            "segments": segments,
            "metadata": {
                "broadcast_time": time_str,
                "time_of_day": time_of_day,
                "total_duration": timing,
                "marcel_segments": len([s for s in segments if s["speaker"] == "marcel"]),
                "jarvis_segments": len([s for s in segments if s["speaker"] == "jarvis"]),
                "news_count": len(content["news"]) if content["news"] else 0,
                "errors": content["errors"]
            }
        }
    
    def generate_clean_speaker_texts(self, script):
        """Generiert SAUBERE Texte für jeden Sprecher (OHNE Pause-Tags!)"""
        
        marcel_texts = []
        jarvis_texts = []
        
        for segment in script["segments"]:
            if segment["speaker"] == "marcel":
                marcel_texts.append(segment["text"])
            else:
                jarvis_texts.append(segment["text"])
        
        # SAUBERE Texte - DIREKT zusammenfügen ohne "..." Tags
        marcel_clean = " ".join(marcel_texts)  # Nur Leerzeichen zwischen Segmenten
        jarvis_clean = " ".join(jarvis_texts)  # Nur Leerzeichen zwischen Segmenten
        
        return {
            "marcel": marcel_clean,
            "jarvis": jarvis_clean,
            "marcel_segments": marcel_texts,
            "jarvis_segments": jarvis_texts
        }
    
    def save_script(self, script, content):
        """Speichert das Script als TXT-Datei"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        script_file = self.output_dir / f"RadioX_Clean_Script_{timestamp}.txt"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX CLEAN BROADCAST SCRIPT\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏰ Broadcast Zeit: {script['metadata']['broadcast_time']} Uhr {script['metadata']['time_of_day']}\n")
            f.write(f"⏱️ Gesamtdauer: {script['metadata']['total_duration']} Sekunden\n")
            f.write(f"📰 News Anzahl: {script['metadata']['news_count']}\n")
            f.write("\n")
            
            # Fehler anzeigen falls vorhanden
            if script['metadata']['errors']:
                f.write("⚠️ AUFGETRETENE FEHLER:\n")
                f.write("-" * 40 + "\n")
                for error in script['metadata']['errors']:
                    f.write(f"❌ {error}\n")
                f.write("\n")
            
            f.write("👥 SPRECHER-VERTEILUNG:\n")
            f.write("-" * 40 + "\n")
            f.write(f"🤖 JARVIS (Cool Starter): {script['metadata']['jarvis_segments']} Segmente\n")
            f.write(f"🎤 MARCEL (Lokal Expert): {script['metadata']['marcel_segments']} Segmente\n")
            f.write("\n")
            
            # Content-Quellen
            if content["news"]:
                f.write("📊 NEWS-QUELLEN:\n")
                f.write("-" * 40 + "\n")
                for i, news in enumerate(content["news"], 1):
                    f.write(f"{i}. {news.title} ({news.source} - {news.category})\n")
                f.write("\n")
            
            # Wetter & Bitcoin
            if content["weather"]:
                f.write(f"🌤️ Wetter: {content['weather']['current'].temperature:.1f}°C in Zürich\n")
            if content["bitcoin"]:
                f.write(f"₿ Bitcoin: ${content['bitcoin'].price_usd:,.0f} ({content['bitcoin'].change_24h:+.1f}%)\n")
            f.write("\n")
            
            # Script-Segmente
            f.write("🎬 SCRIPT-SEGMENTE:\n")
            f.write("=" * 60 + "\n")
            
            for i, segment in enumerate(script["segments"], 1):
                speaker_icon = "🤖" if segment["speaker"] == "jarvis" else "🎤"
                timing = segment["timing"]
                duration = segment["duration"]
                
                f.write(f"\n[{timing:02d}s-{timing+duration:02d}s] {i:2d}. {speaker_icon} {segment['speaker'].upper()}:\n")
                f.write(f"     {segment['text']}\n")
                
                if segment.get('source'):
                    f.write(f"     📰 Quelle: {segment['source']} ({segment.get('category', 'N/A')})\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("🔧 AUDIO-VERBESSERUNGEN:\n")
            f.write("- KEINE Pause-Tags mehr!\n")
            f.write("- Jarvis startet cool\n")
            f.write("- Saubere Text-Trennung\n")
            f.write("- Direkte Leerzeichen statt '...'\n")
        
        return script_file


async def generate_clean_broadcast():
    """Hauptfunktion für sauberen Broadcast"""
    
    print("🎙️ RADIOX CLEAN BROADCAST")
    print("=" * 60)
    print("🤖 Jarvis startet cool + KEINE Pause-Tags!")
    print(f"⏰ Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # System initialisieren
    broadcast = CleanBroadcast()
    
    # SCHRITT 1: Neueste Inhalte sammeln
    content = await broadcast.collect_latest_content()
    
    # SCHRITT 2: Script erstellen
    print("🎭 ERSTELLE SAUBERES SCRIPT")
    print("-" * 40)
    
    script = broadcast.create_clean_script(content)
    
    print("✅ Sauberes Script erstellt:")
    print(f"   Gesamtdauer: {script['metadata']['total_duration']} Sekunden")
    print(f"   🤖 Jarvis Segmente: {script['metadata']['jarvis_segments']} (Cool Starter!)")
    print(f"   🎤 Marcel Segmente: {script['metadata']['marcel_segments']} (Lokal Expert)")
    print(f"   News verarbeitet: {script['metadata']['news_count']}")
    print()
    
    # SCHRITT 3: Script speichern
    print("📝 SPEICHERE SCRIPT")
    print("-" * 40)
    
    script_file = broadcast.save_script(script, content)
    print(f"✅ Script gespeichert: {script_file.name}")
    print()
    
    # SCHRITT 4: SAUBERE Sprecher-Texte generieren
    print("🔀 GENERIERE SAUBERE SPRECHER-TEXTE")
    print("-" * 40)
    
    speaker_texts = broadcast.generate_clean_speaker_texts(script)
    
    print(f"🤖 Jarvis Text: {len(speaker_texts['jarvis'])} Zeichen")
    print(f"🎤 Marcel Text: {len(speaker_texts['marcel'])} Zeichen")
    print()
    
    print("🤖 JARVIS'S SAUBERER TEXT (Cool Starter):")
    print("=" * 50)
    print(speaker_texts['jarvis'][:150] + "...")
    print("=" * 50)
    print()
    
    print("🎤 MARCEL'S SAUBERER TEXT (Lokal Expert):")
    print("=" * 50)
    print(speaker_texts['marcel'][:150] + "...")
    print("=" * 50)
    print()
    
    # SCHRITT 5: Bereit für Audio-Generierung
    print("🎵 BEREIT FÜR SAUBERE AUDIO-GENERIERUNG")
    print("-" * 40)
    print("✅ KEINE Pause-Tags mehr!")
    print("✅ Jarvis startet cool")
    print("✅ Saubere Text-Trennung")
    print("✅ Timing-Informationen verfügbar")
    print()
    
    print("🎉 CLEAN BROADCAST FERTIG!")
    print("=" * 60)
    print(f"📝 Script: {script_file.name}")
    print("🤖 Jarvis Audio: Bereit für ElevenLabs (Cool Starter)")
    print("🎤 Marcel Audio: Bereit für ElevenLabs (Lokal Expert)")
    
    if script['metadata']['errors']:
        print()
        print("⚠️ HINWEISE:")
        for error in script['metadata']['errors']:
            print(f"   - {error}")
    
    return {
        "script": script,
        "speaker_texts": speaker_texts,
        "script_file": script_file,
        "content": content
    }


if __name__ == "__main__":
    asyncio.run(generate_clean_broadcast()) 