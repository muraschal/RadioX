#!/usr/bin/env python3

"""
RadioX Conversational Broadcast - Echter Dialog mit ElevenLabs Conversational AI
Marcel + Jarvis = ECHTER DIALOG mit korrektem Timing!
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import requests
import os
import json

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.rss_parser import RSSParser
from src.services.weather_service import WeatherService
from src.services.coinmarketcap_service import CoinMarketCapService


class ConversationalBroadcast:
    """Echter Dialog-Broadcast mit ElevenLabs Conversational AI"""
    
    def __init__(self):
        # ElevenLabs API
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable nicht gesetzt!")
        
        # Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Deine Stimme (Deutsch)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis AI Style
        
        # Output-Verzeichnis
        self.output_dir = Path("D:/DEV/muraschal/RadioX/output")
        self.output_dir.mkdir(exist_ok=True)
        
        # ElevenLabs Conversational API
        self.conv_api_url = "https://api.elevenlabs.io/v1/convai/conversations"
        
    async def collect_content(self):
        """Sammelt aktuelle Inhalte"""
        
        print("📊 SAMMLE AKTUELLE INHALTE")
        print("-" * 40)
        
        content = {
            "news": [],
            "weather": None,
            "bitcoin": None,
            "time_info": None
        }
        
        # Zeit-Info
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        hour = now.hour
        
        if 5 <= hour < 12:
            time_of_day = "am Morgen"
        elif 12 <= hour < 17:
            time_of_day = "am Mittag"
        elif 17 <= hour < 22:
            time_of_day = "am Abend"
        else:
            time_of_day = "in der Nacht"
        
        content["time_info"] = {
            "time": time_str,
            "period": time_of_day
        }
        
        # RSS News sammeln
        try:
            print("📰 Sammle RSS News...")
            rss_parser = RSSParser()
            zueri_news = await rss_parser.get_zueri_style_feed()
            content["news"] = zueri_news[:3]  # Top 3
            print(f"✅ {len(content['news'])} News gesammelt")
            
        except Exception as e:
            print(f"❌ RSS News Fehler: {str(e)}")
        
        # Wetter sammeln
        try:
            print("🌤️ Sammle Wetter...")
            weather_service = WeatherService()
            weather_data = await weather_service.get_weather_for_station("zurich")
            content["weather"] = weather_data
            print(f"✅ Wetter: {weather_data['current'].temperature:.1f}°C")
            
        except Exception as e:
            print(f"❌ Wetter Fehler: {str(e)}")
        
        # Bitcoin sammeln
        try:
            print("₿ Sammle Bitcoin...")
            btc_service = CoinMarketCapService()
            btc_data = await btc_service.get_bitcoin_price()
            content["bitcoin"] = btc_data
            print(f"✅ Bitcoin: ${btc_data.price_usd:,.0f} ({btc_data.change_24h:+.1f}%)")
            
        except Exception as e:
            print(f"❌ Bitcoin Fehler: {str(e)}")
        
        return content
    
    def create_conversation_script(self, content):
        """Erstellt Conversation Script für ElevenLabs"""
        
        # News zusammenfassen
        news_summary = ""
        if content["news"]:
            for i, news in enumerate(content["news"], 1):
                news_summary += f"{i}. {news.title}. {news.summary[:100]}...\n"
        
        # Wetter Info
        weather_info = "Wetter nicht verfügbar"
        if content["weather"]:
            weather_info = content["weather"].get("radio_current", "Wetter nicht verfügbar")
        
        # Bitcoin Info
        bitcoin_info = "Bitcoin-Daten nicht verfügbar"
        if content["bitcoin"]:
            bitcoin_info = f"Bitcoin steht bei {content['bitcoin'].price_usd:,.0f} US-Dollar, das sind {content['bitcoin'].change_24h:+.1f}% in 24 Stunden"
        
        # Zeit Info
        time_str = content["time_info"]["time"]
        time_period = content["time_info"]["period"]
        
        # Conversation Script
        conversation_script = f"""
RADIOX LIVE BROADCAST - {time_str} UHR {time_period.upper()}

SPRECHER:
- JARVIS (Voice ID: {self.jarvis_voice_id}): Cool, Tech-Expert, startet das Gespräch
- MARCEL (Voice ID: {self.marcel_voice_id}): Lokal-Expert aus Zürich, warm

DIALOG-ABLAUF:

JARVIS: "RadioX ist live! Es ist {time_str} Uhr {time_period}. Hier ist Jarvis mit den neuesten Updates."

MARCEL: "Grüezi! Und ich bin Marcel. Zusammen bringen wir euch die aktuellen News aus Zürich und der Welt."

JARVIS: "Perfekt, Marcel! Los geht's mit den Top-Meldungen."

MARCEL: "Lokale News aus Zürich: {content['news'][0].title if content['news'] else 'Keine News verfügbar'}. {content['news'][0].summary[:120] if content['news'] else ''}"

JARVIS: "Interessant, Marcel! Das bewegt wirklich die Leute."

JARVIS: "Tech-Update: {content['news'][1].title if len(content['news']) > 1 else 'Weitere News folgen'}."

MARCEL: "Da passiert einiges, Jarvis!"

JARVIS: "Krypto-Update: {bitcoin_info}"

MARCEL: "Die Krypto-Welt bleibt spannend, Jarvis!"

MARCEL: "Wie sieht's mit dem Wetter aus, Jarvis?"

JARVIS: "Aktuell in Zürich: {weather_info}"

MARCEL: "Perfekt für den Tag!"

MARCEL: "Das waren die News um {time_str} Uhr, Marcel hier."

JARVIS: "Und Jarvis. Bleibt dran bei RadioX - wir sind zurück mit mehr Updates!"

ENDE DES DIALOGS
"""
        
        return conversation_script
    
    def create_conversational_audio(self, script):
        """Erstellt Audio mit ElevenLabs Conversational AI"""
        
        print("🎤 ERSTELLE CONVERSATIONAL AUDIO")
        print("-" * 40)
        
        # Conversation Request
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Conversation Data
        conversation_data = {
            "agent_id": "your_agent_id_here",  # Müsste erstellt werden
            "conversation_config": {
                "agent_config": {
                    "prompt": {
                        "prompt": f"""Du bist ein RadioX Broadcast-System mit zwei Sprechern:

JARVIS (Voice: {self.jarvis_voice_id}): Cool, Tech-Expert
MARCEL (Voice: {self.marcel_voice_id}): Lokal-Expert aus Zürich

Führe folgenden Dialog aus:

{script}

Achte auf:
- Natürliche Pausen zwischen Sprechern
- Korrekte Voice-IDs
- Timing wie im Script angegeben
- Schweizer Lokalkolorit bei Marcel
- Tech-Fokus bei Jarvis
"""
                    },
                    "first_message": "RadioX ist live! Hier ist Jarvis mit den neuesten Updates.",
                    "language": "de",
                    "voice_id": self.jarvis_voice_id
                }
            }
        }
        
        try:
            print("📡 Sende Conversational Request...")
            response = requests.post(
                self.conv_api_url,
                json=conversation_data,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Conversational Audio erstellt!")
                return result
            else:
                print(f"❌ Conversational API Fehler: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Conversational Audio Fehler: {str(e)}")
            return None
    
    def create_simple_tts_with_timing(self, script, content):
        """Fallback: Erstellt TTS mit korrektem Timing"""
        
        print("🎤 FALLBACK: ERSTELLE TTS MIT TIMING")
        print("-" * 40)
        
        # Timing-basierte Segmente (wie im perfekten Script)
        segments = [
            {"speaker": "jarvis", "text": f"RadioX ist live! Es ist {content['time_info']['time']} Uhr {content['time_info']['period']}. Hier ist Jarvis mit den neuesten Updates.", "start": 0, "duration": 5},
            {"speaker": "marcel", "text": "Grüezi! Und ich bin Marcel. Zusammen bringen wir euch die aktuellen News aus Zürich und der Welt.", "start": 5, "duration": 5},
            {"speaker": "jarvis", "text": "Perfekt, Marcel! Los geht's mit den Top-Meldungen.", "start": 10, "duration": 3},
        ]
        
        # News hinzufügen
        current_time = 13
        if content["news"]:
            for i, news in enumerate(content["news"][:2]):
                if news.category in ['zurich', 'schweiz', 'lokale_news_schweiz']:
                    speaker = "marcel"
                    intro = f"Lokale News {i+1}:"
                else:
                    speaker = "jarvis"
                    intro = f"Update {i+1}:"
                
                news_text = f"{intro} {news.title}. {news.summary[:120]}"
                segments.append({
                    "speaker": speaker,
                    "text": news_text,
                    "start": current_time,
                    "duration": 15
                })
                current_time += 15
                
                # Reaktion
                reaction_speaker = "jarvis" if speaker == "marcel" else "marcel"
                reaction_text = "Interessant, Marcel! Das bewegt wirklich die Leute." if speaker == "marcel" else "Da passiert einiges, Jarvis!"
                segments.append({
                    "speaker": reaction_speaker,
                    "text": reaction_text,
                    "start": current_time,
                    "duration": 3
                })
                current_time += 3
        
        # Bitcoin
        if content["bitcoin"]:
            segments.append({
                "speaker": "jarvis",
                "text": f"Krypto-Update: Bitcoin steht bei {content['bitcoin'].price_usd:,.0f} US-Dollar, das sind {content['bitcoin'].change_24h:+.1f}% in 24 Stunden.",
                "start": current_time,
                "duration": 8
            })
            current_time += 8
            
            segments.append({
                "speaker": "marcel",
                "text": "Die Krypto-Welt bleibt spannend, Jarvis!",
                "start": current_time,
                "duration": 3
            })
            current_time += 3
        
        # Wetter
        if content["weather"]:
            weather_text = content["weather"].get("radio_current", "Wetter nicht verfügbar")
            
            segments.extend([
                {"speaker": "marcel", "text": "Wie sieht's mit dem Wetter aus, Jarvis?", "start": current_time, "duration": 3},
                {"speaker": "jarvis", "text": f"Aktuell in Zürich: {weather_text}", "start": current_time + 3, "duration": 6},
                {"speaker": "marcel", "text": "Perfekt für den Tag!", "start": current_time + 9, "duration": 2}
            ])
            current_time += 11
        
        # Outro
        segments.extend([
            {"speaker": "marcel", "text": f"Das waren die News um {content['time_info']['time']} Uhr, Marcel hier.", "start": current_time, "duration": 3},
            {"speaker": "jarvis", "text": "Und Jarvis. Bleibt dran bei RadioX - wir sind zurück mit mehr Updates!", "start": current_time + 3, "duration": 4}
        ])
        
        return segments
    
    def generate_timed_audio_segments(self, segments):
        """Generiert Audio-Segmente mit korrektem Timing"""
        
        print("🎵 GENERIERE TIMED AUDIO SEGMENTS")
        print("-" * 40)
        
        audio_segments = []
        
        for i, segment in enumerate(segments):
            voice_id = self.marcel_voice_id if segment["speaker"] == "marcel" else self.jarvis_voice_id
            
            print(f"🎤 Segment {i+1}: {segment['speaker'].upper()} ({segment['start']}s-{segment['start'] + segment['duration']}s)")
            print(f"   Text: {segment['text'][:50]}...")
            
            # TTS Request
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": segment["text"],
                "model_id": "eleven_turbo_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.2,
                    "use_speaker_boost": True
                }
            }
            
            try:
                response = requests.post(url, json=data, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    # Timestamp für Dateiname
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    
                    # Segment-Dateiname
                    segment_file = self.output_dir / f"RadioX_Segment_{i+1:02d}_{segment['speaker']}_{timestamp}.mp3"
                    
                    # Audio speichern
                    with open(segment_file, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = len(response.content) / 1024
                    print(f"   ✅ Segment gespeichert: {segment_file.name} ({file_size:.1f} KB)")
                    
                    audio_segments.append({
                        "segment": segment,
                        "file": segment_file,
                        "size_kb": file_size,
                        "success": True
                    })
                    
                else:
                    print(f"   ❌ TTS Fehler {response.status_code}: {response.text}")
                    audio_segments.append({
                        "segment": segment,
                        "error": f"TTS Fehler {response.status_code}",
                        "success": False
                    })
                    
            except Exception as e:
                print(f"   ❌ Segment Fehler: {str(e)}")
                audio_segments.append({
                    "segment": segment,
                    "error": str(e),
                    "success": False
                })
        
        return audio_segments
    
    def save_broadcast_info(self, segments, audio_segments, content):
        """Speichert Broadcast-Informationen"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        info_file = self.output_dir / f"RadioX_Conversational_Info_{timestamp}.txt"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX CONVERSATIONAL BROADCAST\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏰ Broadcast Zeit: {content['time_info']['time']} Uhr {content['time_info']['period']}\n")
            f.write(f"⏱️ Gesamtdauer: {segments[-1]['start'] + segments[-1]['duration']} Sekunden\n")
            f.write(f"🎵 Audio Segmente: {len(audio_segments)}\n")
            f.write("\n")
            
            # Erfolgreiche Segmente
            successful = [a for a in audio_segments if a["success"]]
            failed = [a for a in audio_segments if not a["success"]]
            
            f.write("🎵 GENERIERTE AUDIO-SEGMENTE:\n")
            f.write("-" * 40 + "\n")
            
            total_size = 0
            for audio in successful:
                segment = audio["segment"]
                f.write(f"✅ Segment {segments.index(segment)+1:02d}: {segment['speaker'].upper()} ({segment['start']}s-{segment['start']+segment['duration']}s)\n")
                f.write(f"   📁 {audio['file'].name} ({audio['size_kb']:.1f} KB)\n")
                f.write(f"   💬 {segment['text'][:80]}...\n\n")
                total_size += audio['size_kb']
            
            if failed:
                f.write("❌ FEHLGESCHLAGENE SEGMENTE:\n")
                f.write("-" * 40 + "\n")
                for audio in failed:
                    segment = audio["segment"]
                    f.write(f"💥 Segment {segments.index(segment)+1:02d}: {segment['speaker'].upper()} - {audio['error']}\n")
                f.write("\n")
            
            f.write(f"📊 Gesamt-Größe: {total_size:.1f} KB\n")
            f.write(f"✅ Erfolgreich: {len(successful)}/{len(audio_segments)} Segmente\n")
            f.write("\n")
            
            # Content-Quellen
            if content["news"]:
                f.write("📊 NEWS-QUELLEN:\n")
                f.write("-" * 40 + "\n")
                for i, news in enumerate(content["news"], 1):
                    f.write(f"{i}. {news.title} ({news.source})\n")
                f.write("\n")
            
            # Timing-Schema
            f.write("⏰ TIMING-SCHEMA:\n")
            f.write("=" * 60 + "\n")
            
            for i, segment in enumerate(segments, 1):
                speaker_icon = "🤖" if segment["speaker"] == "jarvis" else "🎤"
                f.write(f"[{segment['start']:02d}s-{segment['start']+segment['duration']:02d}s] {i:2d}. {speaker_icon} {segment['speaker'].upper()}:\n")
                f.write(f"     {segment['text']}\n\n")
        
        return info_file


async def generate_conversational_broadcast():
    """Hauptfunktion für Conversational Broadcast"""
    
    print("🎙️ RADIOX CONVERSATIONAL BROADCAST")
    print("=" * 60)
    print("🤖 Jarvis + 🎤 Marcel = ECHTER DIALOG mit korrektem Timing!")
    print(f"⏰ Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # System initialisieren
    broadcast = ConversationalBroadcast()
    
    # SCHRITT 1: Content sammeln
    content = await broadcast.collect_content()
    
    # SCHRITT 2: Conversation Script erstellen
    print("\n🎭 ERSTELLE CONVERSATION SCRIPT")
    print("-" * 40)
    
    script = broadcast.create_conversation_script(content)
    print("✅ Conversation Script erstellt!")
    
    # SCHRITT 3: Timing-basierte Segmente erstellen
    print("\n⏰ ERSTELLE TIMING-BASIERTE SEGMENTE")
    print("-" * 40)
    
    segments = broadcast.create_simple_tts_with_timing(script, content)
    print(f"✅ {len(segments)} Timing-Segmente erstellt!")
    print(f"   Gesamtdauer: {segments[-1]['start'] + segments[-1]['duration']} Sekunden")
    
    # SCHRITT 4: Audio-Segmente generieren
    print("\n🎵 GENERIERE AUDIO-SEGMENTE")
    print("-" * 40)
    
    audio_segments = broadcast.generate_timed_audio_segments(segments)
    
    # SCHRITT 5: Informationen speichern
    print("\n📝 SPEICHERE BROADCAST-INFORMATIONEN")
    print("-" * 40)
    
    info_file = broadcast.save_broadcast_info(segments, audio_segments, content)
    print(f"✅ Broadcast-Info gespeichert: {info_file.name}")
    
    # SCHRITT 6: Zusammenfassung
    print("\n🎉 CONVERSATIONAL BROADCAST FERTIG!")
    print("=" * 60)
    
    successful = [a for a in audio_segments if a["success"]]
    failed = [a for a in audio_segments if not a["success"]]
    
    print(f"✅ Erfolgreich: {len(successful)}/{len(audio_segments)} Audio-Segmente")
    print(f"📁 Alle Segmente im Output-Verzeichnis")
    print(f"📝 Timing-Schema: {info_file.name}")
    
    if failed:
        print(f"\n❌ Fehlgeschlagen: {len(failed)} Segmente")
    
    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("   1. Audio-Segmente in Audio-Editor laden")
    print("   2. Nach Timing-Schema zusammenfügen")
    print("   3. Pausen zwischen Segmenten einfügen")
    print("   4. Final-Mix exportieren")
    
    return {
        "segments": segments,
        "audio_segments": audio_segments,
        "info_file": info_file,
        "successful_count": len(successful)
    }


if __name__ == "__main__":
    asyncio.run(generate_conversational_broadcast()) 