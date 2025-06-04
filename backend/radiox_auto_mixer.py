#!/usr/bin/env python3

"""
RadioX Auto Mixer - Automatisches Audio-Mixing ohne Audacity!
Marcel + Jarvis = FERTIGES MP3 mit korrektem Timing!
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import requests
import os
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence
import tempfile

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.rss_parser import RSSParser
from src.services.weather_service import WeatherService
from src.services.coinmarketcap_service import CoinMarketCapService


class AutoMixer:
    """Automatisches Audio-Mixing ohne Audacity"""
    
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
        
        # Temp-Verzeichnis für Segmente
        self.temp_dir = Path(tempfile.mkdtemp(prefix="radiox_"))
        
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
    
    def create_dialog_segments(self, content):
        """Erstellt Dialog-Segmente mit exaktem Timing"""
        
        print("🎭 ERSTELLE DIALOG-SEGMENTE")
        print("-" * 40)
        
        segments = []
        current_time = 0
        
        # 1. Intro - Jarvis startet cool
        segments.append({
            "id": 1,
            "speaker": "jarvis",
            "text": f"RadioX ist live! Es ist {content['time_info']['time']} Uhr {content['time_info']['period']}. Hier ist Jarvis mit den neuesten Updates.",
            "start": current_time,
            "duration": 5
        })
        current_time += 5
        
        # 2. Marcel begrüßt
        segments.append({
            "id": 2,
            "speaker": "marcel",
            "text": "Grüezi! Und ich bin Marcel. Zusammen bringen wir euch die aktuellen News aus Zürich und der Welt.",
            "start": current_time,
            "duration": 5
        })
        current_time += 5
        
        # 3. Jarvis leitet ein
        segments.append({
            "id": 3,
            "speaker": "jarvis",
            "text": "Perfekt, Marcel! Los geht's mit den Top-Meldungen.",
            "start": current_time,
            "duration": 3
        })
        current_time += 3
        
        # 4-6. News-Blöcke
        if content["news"]:
            for i, news in enumerate(content["news"][:2]):
                # News-Segment
                if news.category in ['zurich', 'schweiz', 'lokale_news_schweiz']:
                    speaker = "marcel"
                    intro = f"Lokale News {i+1}:"
                else:
                    speaker = "jarvis"
                    intro = f"Update {i+1}:"
                
                news_text = f"{intro} {news.title}. {news.summary[:120]}"
                segments.append({
                    "id": len(segments) + 1,
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
                    "id": len(segments) + 1,
                    "speaker": reaction_speaker,
                    "text": reaction_text,
                    "start": current_time,
                    "duration": 3
                })
                current_time += 3
        
        # 7. Bitcoin - Jarvis
        if content["bitcoin"]:
            segments.append({
                "id": len(segments) + 1,
                "speaker": "jarvis",
                "text": f"Krypto-Update: Bitcoin steht bei {content['bitcoin'].price_usd:,.0f} US-Dollar, das sind {content['bitcoin'].change_24h:+.1f}% in 24 Stunden.",
                "start": current_time,
                "duration": 8
            })
            current_time += 8
            
            segments.append({
                "id": len(segments) + 1,
                "speaker": "marcel",
                "text": "Die Krypto-Welt bleibt spannend, Jarvis!",
                "start": current_time,
                "duration": 3
            })
            current_time += 3
        
        # 8. Wetter-Übergang
        segments.append({
            "id": len(segments) + 1,
            "speaker": "marcel",
            "text": "Wie sieht's mit dem Wetter aus, Jarvis?",
            "start": current_time,
            "duration": 3
        })
        current_time += 3
        
        # 9. Wetter - Jarvis
        if content["weather"]:
            weather_text = content["weather"].get("radio_current", "Wetter nicht verfügbar")
            segments.append({
                "id": len(segments) + 1,
                "speaker": "jarvis",
                "text": f"Aktuell in Zürich: {weather_text}",
                "start": current_time,
                "duration": 6
            })
            current_time += 6
            
            segments.append({
                "id": len(segments) + 1,
                "speaker": "marcel",
                "text": "Perfekt für den Tag!",
                "start": current_time,
                "duration": 2
            })
            current_time += 2
        
        # 10-11. Outro
        segments.append({
            "id": len(segments) + 1,
            "speaker": "marcel",
            "text": f"Das waren die News um {content['time_info']['time']} Uhr, Marcel hier.",
            "start": current_time,
            "duration": 3
        })
        current_time += 3
        
        segments.append({
            "id": len(segments) + 1,
            "speaker": "jarvis",
            "text": "Und Jarvis. Bleibt dran bei RadioX - wir sind zurück mit mehr Updates!",
            "start": current_time,
            "duration": 4
        })
        current_time += 4
        
        print(f"✅ {len(segments)} Dialog-Segmente erstellt!")
        print(f"   Gesamtdauer: {current_time} Sekunden")
        
        return segments
    
    def generate_audio_segment(self, segment):
        """Generiert ein einzelnes Audio-Segment"""
        
        voice_id = self.marcel_voice_id if segment["speaker"] == "marcel" else self.jarvis_voice_id
        
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
                # Temp-Datei für Segment
                segment_file = self.temp_dir / f"segment_{segment['id']:02d}_{segment['speaker']}.mp3"
                
                with open(segment_file, 'wb') as f:
                    f.write(response.content)
                
                return {
                    "segment": segment,
                    "file": segment_file,
                    "success": True,
                    "size": len(response.content)
                }
            else:
                return {
                    "segment": segment,
                    "error": f"TTS Fehler {response.status_code}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "segment": segment,
                "error": str(e),
                "success": False
            }
    
    def mix_audio_segments(self, audio_segments, total_duration):
        """Mischt Audio-Segmente zu einem fertigen MP3"""
        
        print("🎵 MIXE AUDIO-SEGMENTE AUTOMATISCH")
        print("-" * 40)
        
        # Leeres Audio-Track erstellen (Stille)
        final_audio = AudioSegment.silent(duration=total_duration * 1000)  # Millisekunden
        
        successful_segments = [a for a in audio_segments if a["success"]]
        
        for audio in successful_segments:
            segment = audio["segment"]
            
            print(f"🎤 Mixe Segment {segment['id']:02d}: {segment['speaker'].upper()} bei {segment['start']}s")
            
            try:
                # Audio-Segment laden
                audio_clip = AudioSegment.from_mp3(audio["file"])
                
                # Position berechnen (Millisekunden)
                start_ms = segment["start"] * 1000
                
                # Audio an der richtigen Position einfügen
                final_audio = final_audio.overlay(audio_clip, position=start_ms)
                
                print(f"   ✅ Segment eingefügt bei {segment['start']}s")
                
            except Exception as e:
                print(f"   ❌ Mix-Fehler: {str(e)}")
        
        return final_audio
    
    def save_final_broadcast(self, final_audio, segments, content):
        """Speichert das finale Broadcast-MP3"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Final MP3 speichern
        final_file = self.output_dir / f"RadioX_AutoMix_{timestamp}.mp3"
        
        print(f"💾 Speichere finales MP3: {final_file.name}")
        
        # Export mit hoher Qualität
        final_audio.export(
            final_file,
            format="mp3",
            bitrate="128k",
            parameters=["-ar", "44100"]
        )
        
        file_size = final_file.stat().st_size / (1024 * 1024)  # MB
        duration = len(final_audio) / 1000  # Sekunden
        
        print(f"✅ Final MP3 gespeichert!")
        print(f"   📁 Datei: {final_file.name}")
        print(f"   📊 Größe: {file_size:.1f} MB")
        print(f"   ⏱️ Dauer: {duration:.1f} Sekunden")
        
        # Info-Datei erstellen
        info_file = self.output_dir / f"RadioX_AutoMix_Info_{timestamp}.txt"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX AUTO-MIX BROADCAST\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏰ Broadcast Zeit: {content['time_info']['time']} Uhr {content['time_info']['period']}\n")
            f.write(f"🎵 Final MP3: {final_file.name}\n")
            f.write(f"📊 Größe: {file_size:.1f} MB\n")
            f.write(f"⏱️ Dauer: {duration:.1f} Sekunden\n")
            f.write(f"🎤 Segmente: {len(segments)}\n")
            f.write("\n")
            
            f.write("🎭 DIALOG-ABLAUF:\n")
            f.write("-" * 40 + "\n")
            
            for segment in segments:
                speaker_icon = "🤖" if segment["speaker"] == "jarvis" else "🎤"
                f.write(f"[{segment['start']:02d}s-{segment['start']+segment['duration']:02d}s] {segment['id']:2d}. {speaker_icon} {segment['speaker'].upper()}:\n")
                f.write(f"     {segment['text']}\n\n")
        
        return final_file, info_file
    
    def cleanup_temp_files(self):
        """Räumt temporäre Dateien auf"""
        
        print("🧹 RÄUME TEMP-DATEIEN AUF")
        
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            print("✅ Temp-Dateien gelöscht")
        except Exception as e:
            print(f"❌ Cleanup-Fehler: {str(e)}")


async def generate_auto_mix_broadcast():
    """Hauptfunktion für Auto-Mix Broadcast"""
    
    print("🎙️ RADIOX AUTO-MIX BROADCAST")
    print("=" * 60)
    print("🤖 Jarvis + 🎤 Marcel = FERTIGES MP3 ohne Audacity!")
    print(f"⏰ Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # System initialisieren
    mixer = AutoMixer()
    
    try:
        # SCHRITT 1: Content sammeln
        content = await mixer.collect_content()
        
        # SCHRITT 2: Dialog-Segmente erstellen
        segments = mixer.create_dialog_segments(content)
        total_duration = segments[-1]["start"] + segments[-1]["duration"]
        
        # SCHRITT 3: Audio-Segmente generieren
        print("\n🎤 GENERIERE AUDIO-SEGMENTE")
        print("-" * 40)
        
        audio_segments = []
        for segment in segments:
            print(f"🎵 Generiere Segment {segment['id']:02d}: {segment['speaker'].upper()}")
            print(f"   Text: {segment['text'][:50]}...")
            
            audio_result = mixer.generate_audio_segment(segment)
            audio_segments.append(audio_result)
            
            if audio_result["success"]:
                size_kb = audio_result["size"] / 1024
                print(f"   ✅ Erfolgreich ({size_kb:.1f} KB)")
            else:
                print(f"   ❌ Fehler: {audio_result['error']}")
        
        # SCHRITT 4: Audio automatisch mixen
        print(f"\n🎵 AUTOMATISCHES AUDIO-MIXING")
        print("-" * 40)
        
        final_audio = mixer.mix_audio_segments(audio_segments, total_duration)
        
        # SCHRITT 5: Finales MP3 speichern
        print(f"\n💾 SPEICHERE FINALES BROADCAST")
        print("-" * 40)
        
        final_file, info_file = mixer.save_final_broadcast(final_audio, segments, content)
        
        # SCHRITT 6: Cleanup
        mixer.cleanup_temp_files()
        
        # SCHRITT 7: Zusammenfassung
        print("\n🎉 AUTO-MIX BROADCAST FERTIG!")
        print("=" * 60)
        
        successful = [a for a in audio_segments if a["success"]]
        print(f"✅ Erfolgreich: {len(successful)}/{len(audio_segments)} Audio-Segmente")
        print(f"🎵 Final MP3: {final_file.name}")
        print(f"📝 Info-Datei: {info_file.name}")
        print(f"⏱️ Gesamtdauer: {total_duration} Sekunden")
        
        print("\n🎯 FERTIG! Einfach MP3 abspielen! 🎵")
        
        return {
            "final_file": final_file,
            "info_file": info_file,
            "segments": segments,
            "successful_count": len(successful)
        }
        
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        mixer.cleanup_temp_files()
        raise


if __name__ == "__main__":
    asyncio.run(generate_auto_mix_broadcast()) 