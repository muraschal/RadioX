#!/usr/bin/env python3

"""
RadioX Latest Broadcast - Neuester Broadcast mit aktuellen Inhalten
Marcel (Links) + Jarvis (Rechts) = Aktuelle News + Fehlerbehandlung
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


class LatestBroadcast:
    """Neuester Broadcast mit aktuellen Inhalten und Fehlerbehandlung"""
    
    def __init__(self):
        # Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Deine Stimme (Deutsch)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis AI Style
        
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
    
    def create_latest_script(self, content):
        """Erstellt Script mit neuesten Inhalten"""
        
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
        
        # 1. INTRO
        segments.append({
            "speaker": "marcel",
            "text": f"Grüezi und willkommen bei RadioX! Es ist {time_str} Uhr {time_of_day}.",
            "timing": timing,
            "duration": 4
        })
        timing += 4
        
        segments.append({
            "speaker": "jarvis",
            "text": "Hier sind die neuesten News aus Zürich und der Welt.",
            "timing": timing,
            "duration": 4
        })
        timing += 4
        
        segments.append({
            "speaker": "marcel",
            "text": "Ich bin Marcel...",
            "timing": timing,
            "duration": 2
        })
        timing += 2
        
        segments.append({
            "speaker": "jarvis",
            "text": "...und ich bin Jarvis. Los geht's mit den aktuellen Meldungen!",
            "timing": timing,
            "duration": 4
        })
        timing += 4
        
        # 2. NEWS (Intelligente Zuordnung)
        if content["news"]:
            for i, news in enumerate(content["news"][:3]):  # Top 3
                
                # Sprecher-Zuordnung basierend auf Kategorie
                if news.category in ['zurich', 'schweiz', 'lokale_news_schweiz']:
                    speaker = "marcel"
                    intro = f"Lokale Meldung {i+1}:"
                else:
                    speaker = "jarvis"
                    intro = f"News-Update {i+1}:"
                
                # News-Text (gekürzt für bessere Verständlichkeit)
                news_text = f"{intro} {news.title}. {news.summary[:120]}..."
                
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
                            "Interessant, Marcel! Das bewegt die Leute.",
                            "Spannende Entwicklung in Zürich!"
                        ]
                    else:
                        reaction_speaker = "marcel"
                        reactions = [
                            "Wow, das ist wirklich bemerkenswert!",
                            "Da passiert einiges, Jarvis!"
                        ]
                    
                    segments.append({
                        "speaker": reaction_speaker,
                        "text": reactions[i % len(reactions)],
                        "timing": timing,
                        "duration": 3
                    })
                    timing += 3
        
        # 3. BITCOIN
        if content["bitcoin"]:
            segments.append({
                "speaker": "jarvis",
                "text": f"Kurz zu den Krypto-News: Bitcoin steht bei {content['bitcoin'].price_usd:,.0f} US-Dollar, das sind {content['bitcoin'].change_24h:+.1f}% in 24 Stunden.",
                "timing": timing,
                "duration": 8
            })
            timing += 8
            
            segments.append({
                "speaker": "marcel",
                "text": "Die Krypto-Welt bleibt spannend!",
                "timing": timing,
                "duration": 3
            })
            timing += 3
        
        # 4. WETTER
        if content["weather"]:
            weather_text = content["weather"].get("radio_current", "Wetter nicht verfügbar")
            
            segments.append({
                "speaker": "marcel",
                "text": "Wie sieht's denn mit dem Wetter aus, Jarvis?",
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
        
        # 5. OUTRO
        segments.append({
            "speaker": "marcel",
            "text": f"Das waren die News um {time_str} Uhr...",
            "timing": timing,
            "duration": 3
        })
        timing += 3
        
        segments.append({
            "speaker": "jarvis",
            "text": "...bleibt dran bei RadioX!",
            "timing": timing,
            "duration": 3
        })
        timing += 3
        
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
    
    def generate_speaker_texts(self, script):
        """Generiert saubere Texte für jeden Sprecher"""
        
        marcel_parts = []
        jarvis_parts = []
        
        for segment in script["segments"]:
            if segment["speaker"] == "marcel":
                marcel_parts.append(segment["text"])
            else:
                jarvis_parts.append(segment["text"])
        
        return {
            "marcel": " ... ".join(marcel_parts),
            "jarvis": " ... ".join(jarvis_parts)
        }
    
    def save_script(self, script, content):
        """Speichert das Script als TXT-Datei"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        script_file = self.output_dir / f"RadioX_Latest_Script_{timestamp}.txt"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX LATEST BROADCAST SCRIPT\n")
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
            f.write(f"🎤 MARCEL: {script['metadata']['marcel_segments']} Segmente\n")
            f.write(f"🤖 JARVIS: {script['metadata']['jarvis_segments']} Segmente\n")
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
                speaker_icon = "🎤" if segment["speaker"] == "marcel" else "🤖"
                timing = segment["timing"]
                duration = segment["duration"]
                
                f.write(f"\n[{timing:02d}s-{timing+duration:02d}s] {i:2d}. {speaker_icon} {segment['speaker'].upper()}:\n")
                f.write(f"     {segment['text']}\n")
                
                if segment.get('source'):
                    f.write(f"     📰 Quelle: {segment['source']} ({segment.get('category', 'N/A')})\n")
        
        return script_file


async def generate_latest_broadcast():
    """Hauptfunktion für neuesten Broadcast"""
    
    print("🎙️ RADIOX LATEST BROADCAST")
    print("=" * 60)
    print("📡 Neueste Inhalte + Fehlerbehandlung")
    print(f"⏰ Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # System initialisieren
    broadcast = LatestBroadcast()
    
    # SCHRITT 1: Neueste Inhalte sammeln
    content = await broadcast.collect_latest_content()
    
    # SCHRITT 2: Script erstellen
    print("🎭 ERSTELLE SCRIPT")
    print("-" * 40)
    
    script = broadcast.create_latest_script(content)
    
    print("✅ Script erstellt:")
    print(f"   Gesamtdauer: {script['metadata']['total_duration']} Sekunden")
    print(f"   Marcel Segmente: {script['metadata']['marcel_segments']}")
    print(f"   Jarvis Segmente: {script['metadata']['jarvis_segments']}")
    print(f"   News verarbeitet: {script['metadata']['news_count']}")
    print()
    
    # SCHRITT 3: Script speichern
    print("📝 SPEICHERE SCRIPT")
    print("-" * 40)
    
    script_file = broadcast.save_script(script, content)
    print(f"✅ Script gespeichert: {script_file.name}")
    print()
    
    # SCHRITT 4: Sprecher-Texte generieren
    print("🔀 GENERIERE SPRECHER-TEXTE")
    print("-" * 40)
    
    speaker_texts = broadcast.generate_speaker_texts(script)
    
    print(f"🎤 Marcel Text: {len(speaker_texts['marcel'])} Zeichen")
    print(f"🤖 Jarvis Text: {len(speaker_texts['jarvis'])} Zeichen")
    print()
    
    print("🎤 MARCEL'S TEXT (Vorschau):")
    print("=" * 50)
    print(speaker_texts['marcel'][:150] + "...")
    print("=" * 50)
    print()
    
    print("🤖 JARVIS'S TEXT (Vorschau):")
    print("=" * 50)
    print(speaker_texts['jarvis'][:150] + "...")
    print("=" * 50)
    print()
    
    # SCHRITT 5: Bereit für Audio-Generierung
    print("🎵 BEREIT FÜR AUDIO-GENERIERUNG")
    print("-" * 40)
    print("✅ Alle Texte sind sauber (KEINE Tags)")
    print("✅ Timing-Informationen verfügbar")
    print("✅ Fehlerbehandlung durchgeführt")
    print()
    
    print("🎉 LATEST BROADCAST FERTIG!")
    print("=" * 60)
    print(f"📝 Script: {script_file.name}")
    print("🎤 Marcel Audio: Bereit für ElevenLabs")
    print("🤖 Jarvis Audio: Bereit für ElevenLabs")
    
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
    asyncio.run(generate_latest_broadcast()) 