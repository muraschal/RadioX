#!/usr/bin/env python3

"""
RadioX 21:00 Broadcast - Abend-Edition
Marcel & Jarvis präsentieren die Abend-News
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import requests
import os
import json
import tempfile
import shutil
import base64
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, COMM

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.rss_parser import RSSParser
from src.services.weather_service import WeatherService
from src.services.coinmarketcap_service import CoinMarketCapService
from src.services.news_summarizer import NewsSummarizer


class RadioX21UhrBroadcast:
    """21:00 Abend-Broadcast mit Marcel & Jarvis"""
    
    def __init__(self):
        # ElevenLabs API
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable nicht gesetzt!")
        
        # Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Marcel Deutsch (Deine Stimme)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis Deutsch (AI Style)
        
        # Output-Verzeichnis
        self.output_dir = Path("D:/DEV/muraschal/RadioX/output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Temp-Verzeichnis für Segmente
        self.temp_dir = Path(tempfile.mkdtemp(prefix="radiox_21uhr_"))
        
        # GPT API
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
    async def collect_evening_content(self):
        """Sammelt Abend-spezifische Inhalte"""
        
        print("🌙 SAMMLE ABEND-INHALTE (21:00)")
        print("-" * 40)
        
        content = {
            "news": [],
            "weather": None,
            "bitcoin": None,
            "time_info": None
        }
        
        # Zeit-Info für Abend
        now = datetime.now()
        time_str = "21:00"  # Fixe Zeit für 21:00 Broadcast
        
        content["time_info"] = {
            "time": time_str,
            "period": "am Abend",
            "greeting": "Guten Abend"
        }
        
        # RSS News sammeln - Fokus auf Tages-Zusammenfassung
        try:
            print("📰 Sammle Tages-News...")
            rss_parser = RSSParser()
            zueri_news = await rss_parser.get_zueri_style_feed()
            content["news"] = zueri_news[:5]  # Top 5 für Abend-Zusammenfassung
            print(f"✅ {len(content['news'])} News gesammelt")
            
        except Exception as e:
            print(f"❌ RSS News Fehler: {str(e)}")
        
        # Wetter für morgen
        try:
            print("🌤️ Sammle Wetter-Ausblick...")
            weather_service = WeatherService()
            weather_data = await weather_service.get_weather_for_station("zurich")
            content["weather"] = weather_data
            print(f"✅ Wetter: {weather_data['current'].temperature:.1f}°C")
            
        except Exception as e:
            print(f"❌ Wetter Fehler: {str(e)}")
        
        # Bitcoin Tages-Performance
        try:
            print("₿ Sammle Bitcoin Tages-Performance...")
            btc_service = CoinMarketCapService()
            btc_data = await btc_service.get_bitcoin_price()
            content["bitcoin"] = btc_data
            print(f"✅ Bitcoin: ${btc_data.price_usd:,.0f} ({btc_data.change_24h:+.1f}%)")
            
        except Exception as e:
            print(f"❌ Bitcoin Fehler: {str(e)}")
        
        return content
    
    def create_evening_script(self, content):
        """Erstellt Abend-spezifisches Radio-Script"""
        
        print("🌙 ERSTELLE 21:00 ABEND-SCRIPT")
        print("-" * 40)
        
        # News für GPT vorbereiten
        news_text = ""
        news_topics = []
        
        if content["news"]:
            for i, news in enumerate(content["news"], 1):
                news_text += f"{i}. {news.title}\n   {news.summary[:150]}...\n   Quelle: {news.source}\n\n"
                news_topics.append(news.title.split(':')[0].strip())
        
        # Wetter Info
        weather_info = "Wetter nicht verfügbar"
        if content["weather"]:
            weather_service = WeatherService()
            weather_desc = weather_service.get_weather_description(content['weather']['current'].weather_code)
            weather_info = f"{content['weather']['current'].temperature:.1f}°C, {weather_desc}"
        
        # Bitcoin Info
        bitcoin_info = "Bitcoin-Daten nicht verfügbar"
        if content["bitcoin"]:
            btc_price_thousands = round(content['bitcoin'].price_usd / 1000)
            bitcoin_info = f"{btc_price_thousands} Tausend Dollar ({content['bitcoin'].change_24h:+.1f}%)"
        
        # GPT Prompt für Abend-Script
        gpt_prompt = f"""Du bist ein professioneller Radio-Script-Writer für RadioX Zürich - 21:00 ABEND-EDITION.

SPRECHER:
- JARVIS: AI-Co-Host, entspannt-cool, tech-fokussiert
- MARCEL: Haupt-Moderator aus Zürich, warm, entspannt, Tages-Rückblick

WICHTIG: 
- BEIDE SPRECHER VERWENDEN NUR HOCHDEUTSCH! KEIN SCHWEIZERDEUTSCH!
- MARCEL spricht "Jarvis" auf ENGLISCH aus (phonetisch: "Dscharvis")
- ABEND-STIMMUNG: Entspannter, ruhiger, Tages-Rückblick
- 21:00 UHR = Zeit zum Entspannen und Reflektieren

ZEIT: 21:00 Uhr am Abend

TAGES-NEWS:
{news_text}

WETTER: {weather_info} (Ausblick für morgen)
BITCOIN TAGES-PERFORMANCE: {bitcoin_info}

AUFGABE:
Erstelle ein entspanntes Abend-Radio-Script mit folgender Struktur:

1. JARVIS: Entspanntes Abend-Intro "Guten Abend, hier ist RadioX um 21 Uhr"
2. MARCEL: Warme Abend-Begrüßung (sagt "Dscharvis"), "Zeit für den Tages-Rückblick"
3. JARVIS: Bitcoin Tages-Performance - "Wie hat sich Bitcoin heute geschlagen?"
4. MARCEL: Wetter-Ausblick für morgen (sagt "Dscharvis")
5. MARCEL: "Die wichtigsten Ereignisse des Tages" - Lokale News (max 2)
6. JARVIS: Tech/Business Highlights des Tages (max 2)
7. Kurze entspannte Gespräche zwischen den Segmenten
8. MARCEL: "Das war unser Tages-Rückblick" + Ausblick auf morgen
9. JARVIS: Entspannter Abschluss "Schönen Abend noch"

STIL:
- Entspannte Abend-Atmosphäre
- Tages-Rückblick und Reflexion
- NUR HOCHDEUTSCH für beide Sprecher
- Ruhiger, weniger hektisch als Morgen-Radio
- Marcel sagt immer "Dscharvis" (englische Aussprache)
- "Guten Abend" statt "Guten Morgen"
- Fokus auf Entspannung und Ausblick

AUSGABE:
Nur das reine Dialog-Script, keine Regieanweisungen."""

        # GPT Request
        if not self.openai_api_key:
            print("❌ OpenAI API Key nicht verfügbar - verwende Abend-Fallback")
            return self.create_evening_fallback_script(content), news_topics
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {'role': 'user', 'content': gpt_prompt}
                ],
                'max_tokens': 1500,
                'temperature': 0.7
            }
            
            print("🤖 Sende Request an GPT-4...")
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content'].strip()
                print(f"✅ GPT-4 Script erstellt ({len(script)} Zeichen)")
                print("📝 GPT-4 Script:")
                print("-" * 40)
                print(script)
                print("-" * 40)
                return script, news_topics
            else:
                print(f"❌ GPT-4 Fehler: {response.status_code}")
                return self.create_evening_fallback_script(content), news_topics
                
        except Exception as e:
            print(f"❌ GPT-4 Exception: {str(e)}")
            return self.create_evening_fallback_script(content), news_topics
    
    def create_evening_fallback_script(self, content):
        """Fallback Abend-Script falls GPT nicht verfügbar"""
        
        # Bitcoin Info
        bitcoin_text = "Bitcoin-Daten nicht verfügbar"
        if content["bitcoin"]:
            btc_thousands = round(content['bitcoin'].price_usd / 1000)
            bitcoin_text = f"{btc_thousands} Tausend Dollar, heute {content['bitcoin'].change_24h:+.1f} Prozent"
        
        # Wetter Info
        weather_text = "Wetter-Daten nicht verfügbar"
        if content["weather"]:
            weather_text = f"{content['weather']['current'].temperature:.1f} Grad"
        
        # News
        news_text = "Keine aktuellen Nachrichten verfügbar"
        if content["news"]:
            news_text = content["news"][0].title
        
        script = f"""JARVIS: Guten Abend und willkommen zu RadioX um 21 Uhr. Hier ist euer Abend-Update.

MARCEL: Guten Abend zusammen! Hier ist Marcel, und mit mir wie immer Dscharvis. Zeit für unseren Tages-Rückblick.

JARVIS: Schauen wir zuerst auf Bitcoin. Der Kurs steht aktuell bei {bitcoin_text}.

MARCEL: Danke Dscharvis. Beim Wetter haben wir momentan {weather_text}. Morgen wird es ähnlich.

MARCEL: Die wichtigste Nachricht des Tages: {news_text}

JARVIS: Aus der Tech-Welt gibt es heute auch interessante Entwicklungen zu berichten.

MARCEL: Das war unser Rückblick auf den Tag. Morgen sind wir wieder für euch da.

JARVIS: Schönen Abend noch, Zürich. Bis morgen!"""

        return script
    
    def parse_script_to_segments(self, script):
        """Parst Script in Sprecher-Segmente"""
        
        print("📝 PARSE SCRIPT IN SEGMENTE")
        print("-" * 40)
        
        segments = []
        lines = script.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Entferne Markdown-Formatierung (**TEXT:**) und normale Formatierung (TEXT:)
            if line.startswith('**JARVIS:**') or line.startswith('JARVIS:'):
                text = line.replace('**JARVIS:**', '').replace('JARVIS:', '').strip()
                if text:
                    segments.append({
                        'speaker': 'JARVIS',
                        'voice_id': self.jarvis_voice_id,
                        'text': text
                    })
                    
            elif line.startswith('**MARCEL:**') or line.startswith('MARCEL:'):
                text = line.replace('**MARCEL:**', '').replace('MARCEL:', '').strip()
                if text:
                    segments.append({
                        'speaker': 'MARCEL',
                        'voice_id': self.marcel_voice_id,
                        'text': text
                    })
        
        print(f"✅ {len(segments)} Segmente erstellt")
        for i, segment in enumerate(segments, 1):
            print(f"   {i}. {segment['speaker']}: {segment['text'][:50]}...")
        return segments
    
    def generate_audio_segment(self, segment):
        """Generiert Audio für ein Segment"""
        
        speaker = segment['speaker']
        voice_id = segment['voice_id']
        text = segment['text']
        
        print(f"🎙️ Generiere {speaker}: {text[:50]}...")
        
        # Voice Settings
        if speaker == 'MARCEL':
            # Marcel: Nutze Frontend-Settings (keine API-Überschreibung)
            voice_settings = None
        else:
            # Jarvis: Optimierte API-Settings
            voice_settings = {
                "stability": 0.85,
                "similarity_boost": 0.95,
                "style": 0.1,
                "use_speaker_boost": True
            }
        
        # ElevenLabs Request
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": voice_settings
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Speichere Audio-Segment
                segment_file = self.temp_dir / f"{speaker}_{len(text)}.mp3"
                with open(segment_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ {speaker} Audio generiert ({len(response.content)} bytes)")
                return str(segment_file)
            else:
                print(f"❌ ElevenLabs Fehler für {speaker}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Audio-Generation Fehler für {speaker}: {str(e)}")
            return None
    
    def create_concatenated_audio(self, audio_segments):
        """Fügt Audio-Segmente zusammen"""
        
        print("🎵 FÜGE AUDIO-SEGMENTE ZUSAMMEN")
        print("-" * 40)
        
        # Timestamp für Dateiname
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        final_file = self.output_dir / f"RadioX_Final_{timestamp}.mp3"
        
        try:
            # Verwende pydub für Audio-Concatenation
            from pydub import AudioSegment
            
            # Lade alle Audio-Segmente
            combined_audio = AudioSegment.empty()
            
            for i, audio_file in enumerate(audio_segments):
                if audio_file and os.path.exists(audio_file):
                    print(f"   📎 Füge Segment {i+1} hinzu...")
                    segment = AudioSegment.from_mp3(audio_file)
                    combined_audio += segment
                    
                    # Kleine Pause zwischen Segmenten (0.5 Sekunden)
                    if i < len(audio_segments) - 1:
                        pause = AudioSegment.silent(duration=500)  # 500ms
                        combined_audio += pause
            
            # Exportiere finales Audio
            combined_audio.export(str(final_file), format="mp3", bitrate="128k")
            
            print(f"✅ Final Audio erstellt: {final_file.name}")
            print(f"📁 Größe: {final_file.stat().st_size / 1024 / 1024:.1f} MB")
            print(f"⏱️ Dauer: {len(combined_audio) / 1000:.1f} Sekunden")
            return final_file
                
        except ImportError:
            print("❌ pydub nicht verfügbar - verwende einfache Concatenation")
            # Fallback: Einfache Datei-Concatenation
            try:
                with open(final_file, 'wb') as outfile:
                    for audio_file in audio_segments:
                        if audio_file and os.path.exists(audio_file):
                            with open(audio_file, 'rb') as infile:
                                outfile.write(infile.read())
                
                print(f"✅ Final Audio erstellt (einfache Concatenation): {final_file.name}")
                print(f"📁 Größe: {final_file.stat().st_size / 1024 / 1024:.1f} MB")
                return final_file
            except Exception as e:
                print(f"❌ Fallback-Concat Fehler: {str(e)}")
                return None
                
        except Exception as e:
            print(f"❌ Audio-Concat Fehler: {str(e)}")
            return None
    
    def generate_cover_image(self, news_topics):
        """Generiert Cover-Bild für 21:00 Broadcast"""
        
        print("🎨 GENERIERE 21:00 COVER-BILD")
        print("-" * 40)
        
        # Abend-spezifischer Image-Prompt
        image_prompt = f"""Create a professional podcast cover art for "RadioX 21:00 Evening Edition" featuring:

DESIGN ELEMENTS:
- Evening/night theme with warm, cozy lighting
- Swiss design principles: clean, minimal, functional
- Professional broadcasting aesthetic with subtle neon accents
- 1024x1024 pixel format
- Dark background with warm orange/amber lighting
- Microphone and radio wave elements

TEXT ELEMENTS:
- "RADIOX" as main title (bold, modern font)
- "21:00 ABEND-EDITION" as subtitle
- "Marcel & Jarvis" as hosts
- Evening news topics: {', '.join(news_topics[:3]) if news_topics else 'Tages-Rückblick'}

STYLE:
- Modern, professional podcast/radio aesthetic
- Evening atmosphere with warm colors
- Swiss broadcasting quality
- Clean typography
- Subtle tech elements for AI co-host
- Cozy evening radio feeling

COLORS:
- Deep navy/dark blue background
- Warm amber/orange accent lighting
- White/light text
- Subtle neon blue highlights
- Professional broadcasting colors"""

        if not self.openai_api_key:
            print("❌ OpenAI API Key nicht verfügbar für Cover-Generierung")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'dall-e-3',
                'prompt': image_prompt,
                'n': 1,
                'size': '1024x1024',
                'quality': 'standard',
                'response_format': 'b64_json'
            }
            
            print("🎨 Generiere Cover mit DALL-E 3...")
            response = requests.post(
                'https://api.openai.com/v1/images/generations',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result['data'][0]['b64_json'])
                
                # Speichere Cover
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                cover_file = self.output_dir / f"RadioX_Cover_{timestamp}.png"
                
                with open(cover_file, 'wb') as f:
                    f.write(image_data)
                
                print(f"✅ Cover erstellt: {cover_file.name}")
                return cover_file
            else:
                print(f"❌ DALL-E Fehler: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Cover-Generation Fehler: {str(e)}")
            return None
    
    def add_cover_to_mp3(self, mp3_file, cover_image, content):
        """Fügt Cover-Bild zu MP3 hinzu"""
        
        if not cover_image or not cover_image.exists():
            print("❌ Kein Cover-Bild verfügbar")
            return
        
        try:
            print("🎵 Füge Cover zu MP3 hinzu...")
            
            # MP3 Tags setzen
            audio = MP3(mp3_file, ID3=ID3)
            
            # Entferne existierende Tags komplett
            try:
                audio.delete()
                audio.save()
            except:
                pass  # Falls keine Tags vorhanden sind
            
            # Neue Tags hinzufügen
            audio = MP3(mp3_file, ID3=ID3)
            
            # Stelle sicher, dass Tags existieren
            if audio.tags is None:
                audio.add_tags()
            
            # Basis-Tags
            audio.tags.add(TIT2(encoding=3, text=f"RadioX 21:00 Abend-Edition"))
            audio.tags.add(TPE1(encoding=3, text="Marcel & Jarvis"))
            audio.tags.add(TALB(encoding=3, text="RadioX AI Broadcasts"))
            
            # Cover-Bild hinzufügen
            with open(cover_image, 'rb') as img_file:
                img_data = img_file.read()
                
            audio.tags.add(APIC(
                encoding=3,
                mime='image/png',
                type=3,  # Cover (front)
                desc='Cover',
                data=img_data
            ))
            
            # Kommentar mit Broadcast-Info
            comment_text = f"RadioX 21:00 Abend-Edition - {datetime.now().strftime('%d.%m.%Y')}"
            audio.tags.add(COMM(encoding=3, lang='deu', desc='Broadcast Info', text=comment_text))
            
            audio.save(v2_version=3)  # ID3v2.3 für bessere Kompatibilität
            print("✅ Cover und Tags zu MP3 hinzugefügt")
            
        except Exception as e:
            print(f"❌ Cover-Integration Fehler: {str(e)}")
    
    def save_broadcast_info(self, segments, audio_segments, content, final_file, script, news_topics):
        """Speichert Broadcast-Informationen"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        info_file = self.output_dir / f"RadioX_Final_Info_{timestamp}.txt"
        
        # Berechne Gesamtdauer
        total_duration = 0
        if final_file and final_file.exists():
            try:
                audio = MP3(final_file)
                total_duration = audio.info.length
            except:
                pass
        
        info_content = f"""RadioX 21:00 Abend-Edition - Broadcast Info
{'=' * 50}

Timestamp: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Duration: {total_duration:.1f} Sekunden
Segments: {len(segments)}
Audio Files: {len([f for f in audio_segments if f])}

SPRECHER:
- MARCEL: {self.marcel_voice_id} (Deine deutsche Stimme)
- JARVIS: {self.jarvis_voice_id} (AI-Style deutsch)

CONTENT:
- News Items: {len(content.get('news', []))}
- Weather: {'✅' if content.get('weather') else '❌'}
- Bitcoin: {'✅' if content.get('bitcoin') else '❌'}

NEWS TOPICS:
{chr(10).join(f"- {topic}" for topic in news_topics) if news_topics else "Keine Topics verfügbar"}

SCRIPT:
{'=' * 30}
{script}

SEGMENTE:
{'=' * 30}
"""
        
        for i, segment in enumerate(segments, 1):
            info_content += f"{i:2d}. {segment['speaker']:6s}: {segment['text'][:80]}...\n"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_content)
        
        print(f"✅ Broadcast-Info gespeichert: {info_file.name}")
    
    def cleanup_temp_files(self):
        """Räumt temporäre Dateien auf"""
        try:
            shutil.rmtree(self.temp_dir)
            print("✅ Temp-Dateien aufgeräumt")
        except Exception as e:
            print(f"❌ Cleanup Fehler: {str(e)}")


async def generate_21uhr_broadcast():
    """Hauptfunktion für 21:00 Broadcast"""
    
    print("🌙 RADIOX 21:00 ABEND-EDITION")
    print("=" * 50)
    
    broadcast = RadioX21UhrBroadcast()
    
    try:
        # 1. Content sammeln
        content = await broadcast.collect_evening_content()
        
        # 2. Script erstellen
        script, news_topics = broadcast.create_evening_script(content)
        
        # 3. Script parsen
        segments = broadcast.parse_script_to_segments(script)
        
        if not segments:
            print("❌ Keine Segmente erstellt!")
            return
        
        # 4. Audio generieren
        print("\n🎙️ GENERIERE AUDIO-SEGMENTE")
        print("-" * 40)
        
        audio_segments = []
        for segment in segments:
            audio_file = broadcast.generate_audio_segment(segment)
            audio_segments.append(audio_file)
        
        # 5. Audio zusammenfügen
        final_file = broadcast.create_concatenated_audio(audio_segments)
        
        if not final_file:
            print("❌ Audio-Erstellung fehlgeschlagen!")
            return
        
        # 6. Cover generieren
        cover_image = broadcast.generate_cover_image(news_topics)
        
        # 7. Cover zu MP3 hinzufügen
        if cover_image:
            broadcast.add_cover_to_mp3(final_file, cover_image, content)
        
        # 8. Info speichern
        broadcast.save_broadcast_info(segments, audio_segments, content, final_file, script, news_topics)
        
        print("\n🎉 21:00 BROADCAST ERFOLGREICH ERSTELLT!")
        print("=" * 50)
        print(f"📁 MP3: {final_file.name}")
        if cover_image:
            print(f"🎨 Cover: {cover_image.name}")
        print(f"📊 Größe: {final_file.stat().st_size / 1024 / 1024:.1f} MB")
        
    except Exception as e:
        print(f"❌ Broadcast-Erstellung fehlgeschlagen: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        broadcast.cleanup_temp_files()


if __name__ == "__main__":
    asyncio.run(generate_21uhr_broadcast()) 