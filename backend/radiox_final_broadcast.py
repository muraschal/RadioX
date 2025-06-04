#!/usr/bin/env python3

"""
RadioX Final Broadcast - Korrigierte Stimmen + GPT-Script + Image-Prompt!
Jarvis (Intro) + Marcel (Lokal) = PERFEKTES RADIO mit Cover-Art!
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


class FinalBroadcast:
    """Finales Broadcast-System mit korrigierten Stimmen"""
    
    def __init__(self):
        # ElevenLabs API
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable nicht gesetzt!")
        
        # KORRIGIERTE Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Marcel Deutsch (Deine Stimme)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis Deutsch (AI Style)
        
        # Output-Verzeichnis
        self.output_dir = Path("D:/DEV/muraschal/RadioX/output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Temp-Verzeichnis für Segmente
        self.temp_dir = Path(tempfile.mkdtemp(prefix="radiox_"))
        
        # GPT API
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
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
            content["news"] = zueri_news[:4]  # Top 4
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
    
    def create_gpt_radio_script(self, content):
        """Erstellt Radio-Script mit GPT-4"""
        
        print("🤖 ERSTELLE GPT RADIO-SCRIPT")
        print("-" * 40)
        
        # News für GPT vorbereiten
        news_text = ""
        news_topics = []
        
        if content["news"]:
            for i, news in enumerate(content["news"], 1):
                news_text += f"{i}. {news.title}\n   {news.summary[:150]}...\n   Quelle: {news.source}\n\n"
                # Topics für Image-Prompt sammeln
                news_topics.append(news.title.split(':')[0].strip())
        
        # Wetter Info
        weather_info = "Wetter nicht verfügbar"
        if content["weather"]:
            # Wetter-Beschreibung über weather_code holen
            weather_service = WeatherService()
            weather_desc = weather_service.get_weather_description(content['weather']['current'].weather_code)
            weather_info = f"{content['weather']['current'].temperature:.1f}°C, {weather_desc}"
        
        # Bitcoin Info
        bitcoin_info = "Bitcoin-Daten nicht verfügbar"
        if content["bitcoin"]:
            # Bitcoin auf Tausend runden für bessere Aussprache
            btc_price_thousands = round(content['bitcoin'].price_usd / 1000)
            bitcoin_info = f"{btc_price_thousands} Tausend Dollar ({content['bitcoin'].change_24h:+.1f}%)"
        
        # GPT Prompt für Radio-Script
        gpt_prompt = f"""Du bist ein professioneller Radio-Script-Writer für RadioX Zürich.

SPRECHER:
- JARVIS: AI-Co-Host, cool, tech-fokussiert, macht das INTRO und TECH-NEWS
- MARCEL: Haupt-Moderator aus Zürich, warm, lokal-fokussiert, macht LOKALE NEWS

WICHTIG: 
- BEIDE SPRECHER VERWENDEN NUR HOCHDEUTSCH! KEIN SCHWEIZERDEUTSCH!
- MARCEL spricht "Jarvis" auf ENGLISCH aus (wie "DSCHAR-wis", nicht "JAR-wis")
- Verwende phonetische Schreibweise: "Dscharvis" statt "Jarvis" wenn Marcel spricht

ZEIT: {content['time_info']['time']} Uhr {content['time_info']['period']}

AKTUELLE NEWS:
{news_text}

WETTER: {weather_info}
BITCOIN: {bitcoin_info}

AUFGABE:
Erstelle ein natürliches Radio-Dialog-Script mit folgender Struktur:

1. JARVIS macht das coole INTRO (Zeit + Begrüßung)
2. MARCEL begrüßt warm auf HOCHDEUTSCH (sagt "Dscharvis" statt "Jarvis")
3. JARVIS: Bitcoin-Update DIREKT AM ANFANG
4. MARCEL: Wetter-Info und Prognose DIREKT AM ANFANG (sagt "Dscharvis")
5. JARVIS leitet zu den News über
6. MARCEL präsentiert LOKALE/SCHWEIZER News (max 2)
7. JARVIS präsentiert TECH/BUSINESS News (max 2)
8. Kurze Reaktionen zwischen den Sprechern
9. MARCEL: Outro mit Zeit
10. JARVIS: Abschluss

STIL:
- Natürlicher Dialog, keine steife Ansagen
- NUR HOCHDEUTSCH für beide Sprecher
- Tech-Coolness bei Jarvis
- Kurze, prägnante Segmente
- Authentische Reaktionen
- Schweizer Themen, aber in Hochdeutsch
- Marcel sagt immer "Dscharvis" (englische Aussprache)

AUSGABE:
Nur das reine Dialog-Script, keine Regieanweisungen."""

        # GPT Request
        if not self.openai_api_key:
            print("❌ OpenAI API Key nicht verfügbar - verwende Fallback")
            return self.create_fallback_script(content), news_topics
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "Du bist ein professioneller Radio-Script-Writer für Schweizer Radio."},
                    {"role": "user", "content": gpt_prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            print("🤖 Sende GPT-4 Request...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content']
                print("✅ GPT Radio-Script erstellt!")
                return script, news_topics
            else:
                print(f"❌ GPT Fehler {response.status_code}: {response.text}")
                return self.create_fallback_script(content), news_topics
                
        except Exception as e:
            print(f"❌ GPT Request Fehler: {str(e)}")
            return self.create_fallback_script(content), news_topics
    
    def create_fallback_script(self, content):
        """Fallback Script falls GPT nicht verfügbar"""
        
        script = f"""JARVIS: RadioX ist live! Es ist {content['time_info']['time']} Uhr {content['time_info']['period']}. Hier ist Jarvis mit den neuesten Updates.

MARCEL: Grüezi! Und ich bin Marcel. Zusammen bringen wir euch die aktuellen News aus Zürich und der Welt.

JARVIS: Perfekt, Marcel! Los geht's mit den Top-Meldungen.

MARCEL: Lokale News: {content['news'][0].title if content['news'] else 'Keine News verfügbar'}. {content['news'][0].summary[:120] if content['news'] else ''}

JARVIS: Interessant, Marcel! Das bewegt wirklich die Leute.

JARVIS: Tech-Update: {content['news'][1].title if len(content['news']) > 1 else 'Weitere News folgen'}.

MARCEL: Da passiert einiges, Jarvis!

JARVIS: Krypto-Update: Bitcoin steht bei {round(content['bitcoin'].price_usd / 1000) if content['bitcoin'] else 0} Tausend US-Dollar, das sind {content['bitcoin'].change_24h:+.1f}% in 24 Stunden.

MARCEL: Die Krypto-Welt bleibt spannend, Jarvis!

MARCEL: Wie sieht's mit dem Wetter aus, Jarvis?

JARVIS: Aktuell in Zürich: {content['weather'].get('radio_current', 'Wetter nicht verfügbar') if content['weather'] else 'Wetter nicht verfügbar'}

MARCEL: Perfekt für den Tag!

MARCEL: Das waren die News um {content['time_info']['time']} Uhr, Marcel hier.

JARVIS: Und Jarvis. Bleibt dran bei RadioX - wir sind zurück mit mehr Updates!"""
        
        return script
    
    def parse_script_to_segments(self, script):
        """Parst GPT-Script zu Audio-Segmenten"""
        
        print("📝 PARSE SCRIPT ZU SEGMENTEN")
        print("-" * 40)
        
        segments = []
        lines = script.strip().split('\n')
        current_time = 0
        segment_id = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Sprecher erkennen
            if line.startswith("JARVIS:") or line.startswith("**JARVIS:**"):
                speaker = "jarvis"
                text = line.replace("JARVIS:", "").replace("**JARVIS:**", "").strip()
            elif line.startswith("MARCEL:") or line.startswith("**MARCEL:**"):
                speaker = "marcel"
                text = line.replace("MARCEL:", "").replace("**MARCEL:**", "").strip()
            else:
                continue  # Unbekannte Zeile überspringen
            
            # Segment-Dauer schätzen (basierend auf Textlänge)
            word_count = len(text.split())
            duration = max(1, min(15, word_count // 4))  # 1-15 Sekunden, schnellere Sprache
            
            segments.append({
                "id": segment_id,
                "speaker": speaker,
                "text": text,
                "start": current_time,
                "duration": duration
            })
            
            current_time += duration
            segment_id += 1
            
            print(f"   📝 Segment {segment_id-1:02d}: {speaker.upper()} ({duration}s) - {text[:50]}...")
        
        print(f"✅ {len(segments)} Segmente geparst!")
        print(f"   Gesamtdauer: {current_time} Sekunden")
        
        return segments
    
    def generate_image_prompt(self, news_topics, content):
        """Generiert Image-Prompt für Cover-Art mit 2-stufiger Generierung"""
        
        print("🎨 GENERIERE IMAGE-PROMPT (2-STUFIG)")
        print("-" * 40)
        
        # SCHRITT 1: Prosa-Summary für Bild basierend auf Transkript
        news_summary = []
        
        if content["news"]:
            for news in content["news"][:4]:  # Top 4 News
                title_short = news.title.split(':')[0].strip()
                summary_short = news.summary[:80].strip()
                news_summary.append(f"{title_short}: {summary_short}")
        
        # Fallback falls keine News
        if not news_summary:
            news_summary = ["Aktuelle Nachrichten aus Zürich und der Schweiz"]
        
        # Broadcast-Context
        broadcast_context = f"RadioX Zürich Broadcast um {content['time_info']['time']} Uhr {content['time_info']['period']}"
        bitcoin_context = f"Bitcoin bei ${content['bitcoin'].price_usd:,.0f} ({content['bitcoin'].change_24h:+.1f}%)"
        weather_context = f"Wetter in Zürich: {content['weather']['current'].temperature:.1f}°C"
        
        # SCHRITT 1: Prosa-Summary erstellen
        prosa_summary = f"""
{broadcast_context} mit den Moderatoren Marcel (menschlicher Radio-Host aus Zürich) und Jarvis (AI-Co-Host mit technischem Fokus).

Aktuelle Themen der Sendung:
{' | '.join(news_summary)}

Finanzmarkt: {bitcoin_context}
{weather_context}

Die Sendung kombiniert lokale Schweizer Nachrichten mit technischen Updates und Finanzinformationen in einem modernen, professionellen Radio-Format. Marcel bringt die lokale Perspektive ein, während Jarvis die technischen und internationalen Aspekte abdeckt.
        """.strip()
        
        print("✅ SCHRITT 1: Prosa-Summary erstellt")
        print(f"   Länge: {len(prosa_summary)} Zeichen")
        
        # SCHRITT 2: Stylized Podcast Cover 1024x1024
        stylized_prompt = f"""Stylized podcast cover art for a Zurich-based evening news broadcast at {content['time_info']['time']} PM. The image blends bold, symbolic visuals representing key news topics in a futuristic, editorial style:

NEWS-SPECIFIC VISUAL ELEMENTS:
{self._create_news_visual_elements(content["news"])}

FINANCIAL & WEATHER DATA:
– Floating data visualizations showing Bitcoin price trends (around {round(content['bitcoin'].price_usd / 1000) if content['bitcoin'] else 100}K USD)
– Minimalist weather icon with temperature bubble: {content['weather']['current'].temperature:.1f}°C

SWISS CONTEXT:
– Background integrates Swiss design motifs: Zurich skyline, Alpine silhouettes, Lake Zurich shoreline
– Red-white color accents inspired by the Swiss cross
– Clean Swiss design principles: minimal, functional, high-contrast

STYLE & AESTHETICS:
– Editorial and infographic aesthetic with bold, symbolic representations
– Neon blue and orange color accents for modern tech feel
– High contrast, modern design suitable for digital platforms
– Visual clarity with abstract, stylized icons rather than literal representations
– No text overlays in the image

TECHNICAL SPECS:
– 1024x1024 pixels, square format
– Professional broadcast quality
– Bold, graphical, futuristic design"""
        
        print("✅ SCHRITT 2: Stylized Cover-Prompt erstellt")
        print(f"   Format: 1024x1024 Pixel")
        print(f"   Style: Futuristisch, Swiss Design")
        
        return {
            "prosa_summary": prosa_summary,
            "stylized_prompt": stylized_prompt,
            "news_count": len(news_summary),
            "context": f"{content['time_info']['time']} Uhr, Bitcoin ${content['bitcoin'].price_usd:,.0f}, {content['weather']['current'].temperature:.1f}°C"
        }
    
    def _create_news_visual_elements(self, news_items):
        """Erstellt spezifische visuelle Elemente basierend auf News-Inhalten"""
        
        visual_elements = []
        
        for news in news_items[:4]:  # Top 4 News
            title_lower = news.title.lower()
            summary_lower = news.summary.lower()
            
            # Politik/Präsident
            if any(word in title_lower for word in ['präsident', 'fdp', 'politik', 'wahl', 'kandidat', 'partei']):
                visual_elements.append("– Stylized steering wheel or political podium with abstract human silhouettes, symbolizing political leadership and party dynamics")
            
            # Umwelt/Muscheln/See
            elif any(word in title_lower for word in ['muschel', 'zürichsee', 'see', 'wasser', 'umwelt', 'quagga']):
                visual_elements.append("– Mussels or biological structures spreading through transparent water layers, referencing invasive species in Lake Zurich")
            
            # Wirtschaft/Preise/Kartell
            elif any(word in title_lower for word in ['preis', 'kartell', 'wirtschaft', 'hochpreis', 'busse', 'strafe']):
                visual_elements.append("– Cracked price tags, broken Swiss franc coins, or exaggerated barcodes representing price collusion and economic concerns")
            
            # Breaking News/Reporter/Katastrophen
            elif any(word in title_lower for word in ['breaking', 'reporter', 'unfall', 'brand', 'katastrophe', 'bergsturz']):
                visual_elements.append("– Abstract icons of fire, flood, and fast-moving figure symbolizing live breaking news and emergency reporting")
            
            # Tech/Digital/Innovation
            elif any(word in title_lower for word in ['tech', 'digital', 'innovation', 'ki', 'ai', 'technologie']):
                visual_elements.append("– Digital circuits, holographic displays, and tech interfaces representing technological advancement")
            
            # Verkehr/Transport
            elif any(word in title_lower for word in ['verkehr', 'transport', 'bahn', 'auto', 'strasse']):
                visual_elements.append("– Stylized transportation networks, road symbols, and movement lines representing traffic and mobility")
            
            # Gesundheit/Medizin
            elif any(word in title_lower for word in ['gesundheit', 'medizin', 'spital', 'kranken', 'arzt']):
                visual_elements.append("– Medical cross symbols, health icons, and care-related abstract shapes")
            
            # Fallback für andere News
            else:
                visual_elements.append("– Abstract geometric shapes and information symbols representing current events and news flow")
        
        # Falls keine spezifischen Elemente gefunden
        if not visual_elements:
            visual_elements = [
                "– Abstract news symbols, information flow icons, and editorial graphics",
                "– Stylized communication networks and broadcast elements",
                "– Modern infographic elements representing current events"
            ]
        
        return "\n".join(visual_elements[:4])  # Max 4 Elemente
    
    def generate_audio_segment(self, segment):
        """Generiert ein einzelnes Audio-Segment"""
        
        voice_id = self.marcel_voice_id if segment["speaker"] == "marcel" else self.jarvis_voice_id
        
        # Model basierend auf Sprecher wählen
        if segment["speaker"] == "marcel":
            # Marcel ist fine-tuned für multilingual
            model_id = "eleven_multilingual_v2"
        else:
            # Jarvis ist generated voice - braucht multilingual model
            model_id = "eleven_multilingual_v2"
        
        # TTS Request
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Voice-Settings basierend auf Sprecher
        if segment["speaker"] == "marcel":
            # Marcel: Verwende Frontend-Settings (keine voice_settings überschreiben)
            data = {
                "text": segment["text"],
                "model_id": model_id
                # KEINE voice_settings - Frontend-Settings werden verwendet!
            }
        else:
            # Jarvis: Verwende optimierte Settings für stabilere Sprache
            data = {
                "text": segment["text"],
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.85,  # HÖHERE Stabilität gegen Störungen
                    "similarity_boost": 0.95,  # HÖHERE Similarity für Konsistenz
                    "style": 0.0,  # KEINE Style-Exaggeration
                    "use_speaker_boost": False  # Deaktiviert für weniger Artefakte
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
                    "size": len(response.content),
                    "model": model_id
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
    
    def create_concatenated_audio(self, audio_segments):
        """Erstellt concatenated Audio mit optimierten Pausen"""
        
        print("🎵 ERSTELLE CONCATENATED AUDIO")
        print("-" * 40)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Alle erfolgreichen Segmente sammeln
        successful_segments = [a for a in audio_segments if a["success"]]
        successful_segments.sort(key=lambda x: x["segment"]["id"])
        
        if successful_segments:
            final_file = self.output_dir / f"RadioX_Final_{timestamp}.mp3"
            
            # Alle Segmente zusammenfügen mit minimalen Pausen
            with open(final_file, 'wb') as outfile:
                for i, audio in enumerate(successful_segments):
                    segment = audio["segment"]
                    print(f"   📎 Füge Segment {segment['id']:02d} hinzu: {segment['speaker'].upper()}")
                    
                    with open(audio["file"], 'rb') as infile:
                        outfile.write(infile.read())
                    
                    # Kleine Pause zwischen Segmenten (außer beim letzten)
                    if i < len(successful_segments) - 1:
                        # 0.3 Sekunden Pause als MP3-Stille (sehr kurz)
                        silence_bytes = b'\x00' * 1000  # Minimale Stille
                        outfile.write(silence_bytes)
            
            file_size = final_file.stat().st_size / (1024 * 1024)  # MB
            
            print(f"✅ Final MP3 erstellt!")
            print(f"   📁 Datei: {final_file.name}")
            print(f"   📊 Größe: {file_size:.1f} MB")
            print(f"   ⚡ Optimierte Pausen zwischen Segmenten")
            
            return final_file
        
        return None
    
    def save_broadcast_info(self, segments, audio_segments, content, final_file, script, image_prompt):
        """Speichert Broadcast-Informationen mit Image-Prompt"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        info_file = self.output_dir / f"RadioX_Final_Info_{timestamp}.txt"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX FINAL BROADCAST\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏰ Broadcast Zeit: {content['time_info']['time']} Uhr {content['time_info']['period']}\n")
            f.write(f"🎵 Final MP3: {final_file.name if final_file else 'Nicht erstellt'}\n")
            f.write(f"⏱️ Gesamtdauer: {segments[-1]['start'] + segments[-1]['duration'] if segments else 0} Sekunden\n")
            f.write(f"🎤 Segmente: {len(segments)}\n")
            f.write("\n")
            
            # Voice-IDs
            f.write("🎤 SPRECHER-KONFIGURATION:\n")
            f.write("-" * 40 + "\n")
            f.write(f"🤖 JARVIS (Deutsch): {self.jarvis_voice_id}\n")
            f.write(f"   URL: https://elevenlabs.io/app/voice-library?voiceId={self.jarvis_voice_id}\n")
            f.write(f"🎤 MARCEL (Deutsch): {self.marcel_voice_id}\n")
            f.write(f"   URL: https://elevenlabs.io/app/voice-library?voiceId={self.marcel_voice_id}\n")
            f.write("\n")
            
            # GPT Script
            f.write("📝 GPT RADIO-SCRIPT:\n")
            f.write("=" * 60 + "\n")
            f.write(script)
            f.write("\n\n")
            
            # Image-Prompt
            f.write("🎨 COVER-ART IMAGE-PROMPTS:\n")
            f.write("=" * 60 + "\n")
            f.write("📝 SCHRITT 1: PROSA-SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(image_prompt["prosa_summary"])
            f.write("\n\n")
            f.write("🎨 SCHRITT 2: STYLIZED COVER (1024x1024)\n")
            f.write("-" * 30 + "\n")
            f.write(image_prompt["stylized_prompt"])
            f.write("\n\n")
            
            # Audio-Segmente
            successful = [a for a in audio_segments if a["success"]]
            f.write("🎵 AUDIO-SEGMENTE:\n")
            f.write("-" * 40 + "\n")
            
            for audio in successful:
                segment = audio["segment"]
                speaker_icon = "🤖" if segment["speaker"] == "jarvis" else "🎤"
                f.write(f"✅ Segment {segment['id']:02d}: {speaker_icon} {segment['speaker'].upper()} ({segment['start']}s-{segment['start']+segment['duration']}s)\n")
                f.write(f"   💬 {segment['text']}\n\n")
            
            # Content-Quellen
            if content["news"]:
                f.write("📊 NEWS-QUELLEN:\n")
                f.write("-" * 40 + "\n")
                for i, news in enumerate(content["news"], 1):
                    f.write(f"{i}. {news.title} ({news.source})\n")
                f.write("\n")
        
        return info_file
    
    def cleanup_temp_files(self):
        """Räumt temporäre Dateien auf"""
        
        print("🧹 RÄUME TEMP-DATEIEN AUF")
        
        try:
            shutil.rmtree(self.temp_dir)
            print("✅ Temp-Dateien gelöscht")
        except Exception as e:
            print(f"❌ Cleanup-Fehler: {str(e)}")
    
    def generate_cover_image(self, image_prompt):
        """Generiert Cover-Image mit GPT und integriert es ins MP3"""
        
        print("🎨 GENERIERE COVER-IMAGE MIT GPT")
        print("-" * 40)
        
        if not self.openai_api_key:
            print("❌ OpenAI API Key nicht verfügbar - überspringe Image-Generierung")
            return None
        
        try:
            # GPT Image-Generierung
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": image_prompt["stylized_prompt"],
                "n": 1,
                "size": "1024x1024",
                "quality": "standard",
                "response_format": "b64_json"
            }
            
            print("🎨 Sende DALL-E 3 Request...")
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                image_b64 = result['data'][0]['b64_json']
                
                # Image speichern
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                image_file = self.output_dir / f"RadioX_Cover_{timestamp}.png"
                
                with open(image_file, 'wb') as f:
                    f.write(base64.b64decode(image_b64))
                
                file_size = image_file.stat().st_size / 1024  # KB
                print(f"✅ Cover-Image generiert!")
                print(f"   📁 Datei: {image_file.name}")
                print(f"   📊 Größe: {file_size:.1f} KB")
                
                return image_file
            else:
                print(f"❌ DALL-E Fehler {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Image-Generierung Fehler: {str(e)}")
            return None
    
    def add_cover_to_mp3(self, mp3_file, cover_image, content):
        """Fügt Cover-Image und Metadaten zum MP3 hinzu"""
        
        print("🎵 FÜGE COVER ZUM MP3 HINZU")
        print("-" * 40)
        
        if not cover_image or not cover_image.exists():
            print("❌ Kein Cover-Image verfügbar")
            return mp3_file
        
        try:
            # MP3 laden
            audio = MP3(mp3_file, ID3=ID3)
            
            # ID3 Tags hinzufügen falls nicht vorhanden
            if audio.tags is None:
                audio.add_tags()
            
            # Cover-Image hinzufügen
            with open(cover_image, 'rb') as img_file:
                audio.tags.add(
                    APIC(
                        encoding=0,  # ISO-8859-1 für bessere Kompatibilität
                        mime='image/png',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=img_file.read()
                    )
                )
            
            # Metadaten hinzufügen (ID3v2.3 kompatibel)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            audio.tags.add(TIT2(encoding=0, text=f"RadioX Zürich - {content['time_info']['time']} Uhr"))
            audio.tags.add(TPE1(encoding=0, text="Marcel & Jarvis"))
            audio.tags.add(TALB(encoding=0, text=f"RadioX Broadcast {timestamp}"))
            
            # Summary als Kommentar hinzufügen
            news_summary = []
            if content["news"]:
                for news in content["news"][:3]:  # Top 3 für Summary
                    news_summary.append(f"- {news.title.split(':')[0].strip()}")  # Verwende - statt •
            
            bitcoin_info = f"Bitcoin: {round(content['bitcoin'].price_usd / 1000) if content['bitcoin'] else 0}K USD"
            weather_info = f"Wetter: {content['weather']['current'].temperature:.1f}C" if content['weather'] else "Wetter: N/A"  # Entferne °
            
            summary_text = f"""RadioX Zurich Broadcast {content['time_info']['time']} Uhr {content['time_info']['period']}

TOP NEWS:
{chr(10).join(news_summary) if news_summary else '- Aktuelle Nachrichten'}

MARKTDATEN:
- {bitcoin_info}
- {weather_info}

MODERATOREN:
- Marcel (Zurich) - Lokale News & Wetter
- Jarvis (AI) - Tech News & Bitcoin

Dauer: {len([s for s in content.get('segments', []) if s])} Segmente
Produziert: {timestamp}"""
            
            audio.tags.add(COMM(encoding=0, lang='ger', desc='Summary', text=summary_text))
            
            # Speichern mit ID3v2.3 für Windows Media Player Kompatibilität
            audio.save(v2_version=3)
            
            print(f"✅ Cover und Metadaten hinzugefügt!")
            print(f"   🎨 Cover: {cover_image.name}")
            print(f"   🎵 MP3: {mp3_file.name}")
            
            return mp3_file
            
        except Exception as e:
            print(f"❌ MP3-Cover Fehler: {str(e)}")
            return mp3_file


async def generate_final_broadcast():
    """Hauptfunktion für Final Broadcast"""
    
    print("🎙️ RADIOX FINAL BROADCAST")
    print("=" * 60)
    print("🤖 Jarvis (Intro) + 🎤 Marcel (Lokal) = PERFEKTES RADIO!")
    print(f"⏰ Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # System initialisieren
    broadcast = FinalBroadcast()
    
    try:
        # SCHRITT 1: Content sammeln
        content = await broadcast.collect_content()
        
        # SCHRITT 2: GPT Radio-Script erstellen
        script, news_topics = broadcast.create_gpt_radio_script(content)
        
        # DEBUG: Script anzeigen
        print(f"\n🔍 DEBUG: GPT-SCRIPT")
        print("-" * 40)
        print(script[:500] + "..." if len(script) > 500 else script)
        print()
        
        # SCHRITT 3: Script zu Segmenten parsen
        segments = broadcast.parse_script_to_segments(script)
        
        # SCHRITT 4: Image-Prompt generieren
        image_prompt = broadcast.generate_image_prompt(news_topics, content)
        
        # SCHRITT 5: Audio-Segmente generieren
        print("\n🎤 GENERIERE AUDIO-SEGMENTE")
        print("-" * 40)
        
        audio_segments = []
        for segment in segments:
            print(f"🎵 Generiere Segment {segment['id']:02d}: {segment['speaker'].upper()}")
            print(f"   Text: {segment['text'][:50]}...")
            
            audio_result = broadcast.generate_audio_segment(segment)
            audio_segments.append(audio_result)
            
            if audio_result["success"]:
                size_kb = audio_result["size"] / 1024
                print(f"   ✅ Erfolgreich ({size_kb:.1f} KB)")
            else:
                print(f"   ❌ Fehler: {audio_result['error']}")
        
        # SCHRITT 6: Final MP3 erstellen
        print(f"\n🎵 ERSTELLE FINAL MP3")
        print("-" * 40)
        
        final_file = broadcast.create_concatenated_audio(audio_segments)
        
        # SCHRITT 7: Cover-Image generieren
        print(f"\n🎨 GENERIERE COVER-IMAGE")
        print("-" * 40)
        
        cover_image = broadcast.generate_cover_image(image_prompt)
        
        # SCHRITT 8: Cover zum MP3 hinzufügen
        if final_file and cover_image:
            print(f"\n🎵 INTEGRIERE COVER INS MP3")
            print("-" * 40)
            
            final_file = broadcast.add_cover_to_mp3(final_file, cover_image, content)
        
        # SCHRITT 9: Informationen speichern
        print("\n📝 SPEICHERE BROADCAST-INFORMATIONEN")
        print("-" * 40)
        
        info_file = broadcast.save_broadcast_info(segments, audio_segments, content, final_file, script, image_prompt)
        print(f"✅ Broadcast-Info gespeichert: {info_file.name}")
        
        # SCHRITT 10: Cleanup
        broadcast.cleanup_temp_files()
        
        # SCHRITT 11: Zusammenfassung
        print("\n🎉 FINAL BROADCAST FERTIG!")
        print("=" * 60)
        
        successful = [a for a in audio_segments if a["success"]]
        print(f"✅ Erfolgreich: {len(successful)}/{len(audio_segments)} Audio-Segmente")
        
        if final_file:
            print(f"🎵 Final MP3: {final_file.name}")
        
        if cover_image:
            print(f"🎨 Cover-Image: {cover_image.name}")
            print(f"🎵 Cover integriert ins MP3!")
        
        print(f"📝 Info-Datei: {info_file.name}")
        print(f"🎨 Image-Prompt: Enthalten in Info-Datei")
        print(f"⏱️ Gesamtdauer: {segments[-1]['start'] + segments[-1]['duration'] if segments else 0} Sekunden")
        
        print("\n🎯 FERTIG! MP3 mit Cover-Art abspielen! 🎵🎨")
        print("🎨 Automatisch generiertes Cover-Image integriert!")
        
        return {
            "final_file": final_file,
            "cover_image": cover_image,
            "info_file": info_file,
            "segments": segments,
            "successful_count": len(successful),
            "image_prompt": image_prompt
        }
        
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        broadcast.cleanup_temp_files()
        raise


if __name__ == "__main__":
    asyncio.run(generate_final_broadcast()) 