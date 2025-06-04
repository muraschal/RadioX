#!/usr/bin/env python3

"""
RadioX 8:00 Auto-Scheduler - Automatische Show-Generierung alle halbe Stunde
Mit verbesserter Interaktion zwischen Marcel und Jarvis
"""

import asyncio
import schedule
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal
import os
import requests

# Add src to path
sys.path.append(str(Path(__file__).parent))

from radiox_7uhr_morgen_broadcast import RadioX7UhrMorgenBroadcast
from src.utils.german_number_formatter import GermanNumberFormatter


class RadioX8UhrAutoScheduler:
    """Automatischer Scheduler für 8:00 Shows mit verbesserter Interaktion"""
    
    def __init__(self):
        self.running = True
        self.broadcast_system = None
        
        # Setup Signal Handler für graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🕰️ RadioX 8:00 Auto-Scheduler gestartet")
        print("⏰ Generiert Shows alle halbe Stunde ab 8:00")
        print("🎭 Mit verbesserter Marcel & Jarvis Interaktion")
    
    def signal_handler(self, signum, frame):
        """Graceful shutdown"""
        print(f"\n🛑 Shutdown-Signal erhalten ({signum})")
        self.running = False
    
    async def create_enhanced_broadcast(self):
        """Erstellt verbesserte Show mit mehr Interaktion"""
        
        try:
            print(f"\n🌅 STARTE 8:00 SHOW GENERIERUNG - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            # Initialisiere Broadcast-System falls nötig
            if not self.broadcast_system:
                self.broadcast_system = RadioX8UhrEnhancedBroadcast()
            
            # Erstelle verbesserte Show
            result = await self.broadcast_system.create_enhanced_morning_broadcast()
            
            if result:
                print(f"\n✅ 8:00 Show erfolgreich erstellt!")
                print(f"🎵 {result['segments']} Segmente mit verbesserter Interaktion")
                print(f"🎯 Fokusthema: {result.get('focus_topic', 'N/A')}")
                print(f"📁 Dateien im output/ Ordner verfügbar")
                
                # Kurze Pause vor nächster Generierung
                await asyncio.sleep(5)
                
            else:
                print("\n❌ Show-Generierung fehlgeschlagen!")
                
        except Exception as e:
            print(f"\n❌ Fehler bei Show-Generierung: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def schedule_job(self):
        """Wrapper für asyncio Job"""
        asyncio.run(self.create_enhanced_broadcast())
    
    def start_scheduler(self):
        """Startet den Scheduler"""
        
        print("📅 SCHEDULER-KONFIGURATION")
        print("-" * 40)
        
        # Schedule für jede halbe Stunde ab 8:00
        schedule.every().hour.at(":00").do(self.schedule_job)  # 8:00, 9:00, 10:00, etc.
        schedule.every().hour.at(":30").do(self.schedule_job)  # 8:30, 9:30, 10:30, etc.
        
        print("   ⏰ 8:00, 8:30, 9:00, 9:30, 10:00, 10:30, ...")
        print("   🔄 Kontinuierlich alle halbe Stunde")
        
        # Sofortige erste Ausführung für Test
        print("\n🚀 Starte erste Show sofort...")
        self.schedule_job()
        
        print(f"\n⏰ Scheduler läuft - nächste Show um {self.get_next_run_time()}")
        
        # Hauptschleife
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Prüfe alle 30 Sekunden
                
                # Zeige nächste geplante Zeit
                next_run = self.get_next_run_time()
                if next_run:
                    print(f"⏳ Warte auf nächste Show um {next_run} - {datetime.now().strftime('%H:%M:%S')}")
                
            except KeyboardInterrupt:
                print("\n🛑 Scheduler gestoppt durch Benutzer")
                break
            except Exception as e:
                print(f"❌ Scheduler-Fehler: {e}")
                time.sleep(60)  # Warte 1 Minute bei Fehlern
    
    def get_next_run_time(self):
        """Gibt die nächste geplante Ausführungszeit zurück"""
        jobs = schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run.strftime('%H:%M:%S')
        return None


class RadioX8UhrEnhancedBroadcast(RadioX7UhrMorgenBroadcast):
    """Erweiterte Broadcast-Klasse mit verbesserter Interaktion"""
    
    def __init__(self):
        super().__init__()
        self.number_formatter = GermanNumberFormatter()
        print("🎭 Enhanced Broadcast System mit verbesserter Interaktion initialisiert")
        print("🔢 German Number Formatter für optimale Zahlenaussprache aktiviert")
    
    def select_focus_topics(self, news_list):
        """Wählt Fokusthema und Interaktionsthema aus News"""
        
        print("🎯 WÄHLE FOKUS- UND INTERAKTIONSTHEMEN")
        print("-" * 40)
        
        if len(news_list) < 2:
            return None, None
        
        # Kategorisiere News nach Interaktionspotential
        tech_news = []
        local_news = []
        economic_news = []
        general_news = []
        
        for news in news_list:
            title_lower = news['title'].lower()
            description_lower = news.get('description', '').lower()
            
            # Tech/Bitcoin News (hohe Interaktion)
            if any(word in title_lower + description_lower for word in 
                   ['bitcoin', 'technologie', 'digital', 'ki', 'ai', 'internet', 'app', 'software']):
                tech_news.append(news)
            
            # Lokale Zürich News (mittlere Interaktion)
            elif any(word in title_lower for word in ['zürich', 'zurich', 'zürcher']):
                local_news.append(news)
            
            # Wirtschafts News (mittlere Interaktion)
            elif any(word in title_lower + description_lower for word in 
                     ['wirtschaft', 'unternehmen', 'markt', 'börse', 'bank', 'geld']):
                economic_news.append(news)
            
            else:
                general_news.append(news)
        
        # Wähle Fokusthema (längere Diskussion)
        focus_topic = None
        if tech_news:
            focus_topic = tech_news[0]
            focus_type = "TECH"
        elif economic_news:
            focus_topic = economic_news[0]
            focus_type = "WIRTSCHAFT"
        elif local_news:
            focus_topic = local_news[0]
            focus_type = "LOKAL"
        else:
            focus_topic = general_news[0] if general_news else news_list[0]
            focus_type = "ALLGEMEIN"
        
        # Wähle Interaktionsthema (kürzere Diskussion)
        interaction_topic = None
        remaining_news = [n for n in news_list if n != focus_topic]
        
        if remaining_news:
            # Bevorzuge lokale oder wirtschaftliche News für Interaktion
            for news in remaining_news:
                title_lower = news['title'].lower()
                if any(word in title_lower for word in ['zürich', 'schweiz', 'wirtschaft']):
                    interaction_topic = news
                    break
            
            if not interaction_topic:
                interaction_topic = remaining_news[0]
        
        print(f"   🎯 FOKUSTHEMA ({focus_type}): {focus_topic['title'][:50]}...")
        if interaction_topic:
            print(f"   💬 INTERAKTIONSTHEMA: {interaction_topic['title'][:50]}...")
        
        return focus_topic, interaction_topic
    
    def create_enhanced_morning_script(self, content):
        """Erstellt Script mit verbesserter Interaktion"""
        
        print("✍️ ERSTELLE ENHANCED SCRIPT MIT INTERAKTION")
        print("-" * 40)
        
        # Wähle Fokus- und Interaktionsthemen
        focus_topic, interaction_topic = self.select_focus_topics(content['news'])
        
        # Wähle Broadcast-Struktur
        structure_key, selected_structure = self.select_broadcast_structure()
        
        # Lade letztes Script als Referenz
        last_script_data = self.load_last_script()
        
        # News für Prompt formatieren
        news_text = ""
        for i, news in enumerate(content['news'], 1):
            news_type = "📰 STANDARD"
            if news == focus_topic:
                news_type = "🎯 FOKUSTHEMA (LANGE DISKUSSION)"
            elif news == interaction_topic:
                news_type = "💬 INTERAKTIONSTHEMA (KURZE DISKUSSION)"
            
            news_text += f"{i}. {news_type}: {news['title']}\n"
            if news.get('description'):
                news_text += f"   {news['description'][:200]}...\n"
        
        weather_info = f"Temperatur: {content['weather'].get('temperature', 'N/A')}°C, {content['weather'].get('description', 'N/A')}"
        bitcoin_info = f"Bitcoin: ${content['bitcoin'].get('price', 'N/A')} ({content['bitcoin'].get('change_24h', 'N/A')}%)"
        
        # Struktur-spezifische Anweisungen
        structure_instructions = "\n".join([f"   {step}" for step in selected_structure['structure']])
        
        # Referenz-Script für Variation
        reference_section = ""
        if last_script_data:
            reference_section = f"""
LETZTES SCRIPT ALS REFERENZ (NICHT KOPIEREN!):
{'-' * 50}
Letzte Struktur: {last_script_data['structure']}

{last_script_data['script'][:800]}...
{'-' * 50}

WICHTIG: Das obige Script ist NUR als Referenz gedacht!
- Erstelle eine GRUNDLEGEND ANDERE Show
- Verwende ANDERE Gesprächsverläufe und Übergänge
- NEUE Formulierungen und Ansätze
- Vermeide ähnliche Phrasen oder Strukturen
"""
        
        # Enhanced GPT Prompt mit Interaktions-Fokus
        gpt_prompt = f"""Du bist ein professioneller Radio-Script-Writer für RadioX Zürich.

SPRECHER-CHARAKTERE:
- MARCEL: Haupt-Moderator, warm, energisch, Zürcher, führt durch die Sendung
- JARVIS: AI-Co-Host, entspannt-cool, tech-fokussiert, ergänzt Marcel

NEUE INTERAKTIONS-REGELN FÜR LEBENDIGE DISKUSSIONEN:
1. FOKUSTHEMA: Längere Diskussion zwischen Marcel und Jarvis (3-4 Austausche)
2. INTERAKTIONSTHEMA: Kürzere Diskussion (2-3 Austausche)
3. NATÜRLICHE MEINUNGSAUSTAUSCHE: Verschiedene Perspektiven zeigen
4. MARCEL fragt Jarvis gezielt nach seiner Meinung
5. JARVIS bringt eigene Gedanken und Einschätzungen ein
6. ECHTE DISKUSSION statt nur Informationsweitergabe
7. BITCOIN-ONLY: Niemals andere Kryptowährungen erwähnen!

INTERAKTIONS-BEISPIELE:
MARCEL: "Das ist interessant. Jarvis, wie siehst du das?"
JARVIS: "Ich denke, das zeigt einen wichtigen Trend..."
MARCEL: "Guter Punkt! Aber könnte das nicht auch bedeuten..."
JARVIS: "Stimmt, wobei man auch bedenken sollte..."

DISKUSSIONS-STRUKTUR:
- FOKUSTHEMA: Ausführliche Analyse mit verschiedenen Blickwinkeln
- INTERAKTIONSTHEMA: Kurzer aber lebendiger Austausch
- Andere News: Kompakt aber mit gelegentlichen Kommentaren

TEMPO & STIL:
- LEBENDIGE DISKUSSIONEN bei Fokusthemen
- SCHNELL ZUM PUNKT bei Standard-News
- BITCOIN SACHLICH: Fakten ohne Hype
- AUTHENTISCHE RADIO-PARTNER-DYNAMIK

GEWÄHLTE STRUKTUR: "{selected_structure['name']}"
BESCHREIBUNG: {selected_structure['description']}

STRUKTUR-VORGABE:
{structure_instructions}
{reference_section}

INTERAKTIONS-SCHWERPUNKTE:
🎯 FOKUSTHEMA (LANGE DISKUSSION): {focus_topic['title'] if focus_topic else 'Nicht definiert'}
💬 INTERAKTIONSTHEMA (KURZE DISKUSSION): {interaction_topic['title'] if interaction_topic else 'Nicht definiert'}

ANTI-HALLUZINATIONS-REGELN:
- Verwende NUR die bereitgestellten echten News-Titel und Beschreibungen
- Erfinde KEINE zusätzlichen Details oder Fakten
- Bleibe bei den gegebenen Wetter- und Bitcoin-Daten
- KEINE erfundenen Zahlen, Namen oder Ereignisse

WICHTIG: 
- BEIDE SPRECHER VERWENDEN NUR HOCHDEUTSCH!
- MARCEL spricht "Jarvis" auf ENGLISCH aus (phonetisch: "Dscharvis")
- BITCOIN-ONLY: Spreche NIEMALS über andere Kryptowährungen!
- LEBENDIGE INTERAKTION: Echte Diskussionen, nicht nur Informationsweitergabe!
- VERSCHIEDENE PERSPEKTIVEN: Marcel und Jarvis haben unterschiedliche Sichtweisen
- NATÜRLICHE ÜBERGÄNGE: "Was denkst du?", "Wie siehst du das?", "Interessant, aber..."

CONTENT (NUR DIESE ECHTEN DATEN VERWENDEN):
{news_text}

WETTER: {weather_info}
BITCOIN: {bitcoin_info}

AUFGABE: Erstelle ein lebendiges Radio-Script mit ECHTEN DISKUSSIONEN zwischen Marcel und Jarvis:

INTERAKTIONS-STIL:
- FOKUSTHEMA: 3-4 Austausche mit verschiedenen Perspektiven
- INTERAKTIONSTHEMA: 2-3 Austausche mit kurzen Meinungen
- NATÜRLICHE FRAGEN: "Wie siehst du das?", "Was denkst du?"
- ECHTE ANTWORTEN: Jarvis bringt eigene Einschätzungen
- DISKUSSION: Verschiedene Blickwinkel, nicht nur Zustimmung
- BITCOIN SACHLICH: Fakten ohne übertriebene Begeisterung

FORMAT: Nur Sprecher-Namen und Text, keine Regieanweisungen.

Erstelle das komplette Script mit LEBENDIGEN DISKUSSIONEN und der Struktur "{selected_structure['name']}":"""

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
                'max_tokens': 2000,  # Mehr Tokens für längere Diskussionen
                'temperature': 0.8   # Höhere Kreativität für Interaktionen
            }
            
            print("🤖 Sende Enhanced Request an GPT-4...")
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content']
                print("   ✅ Enhanced Script erfolgreich generiert")
                print(f"   📝 Script-Länge: {len(script)} Zeichen")
                print(f"   🎯 Fokusthema: {focus_topic['title'][:50] if focus_topic else 'N/A'}...")
                
                # Speichere gewählte Struktur und Themen
                self.current_structure = selected_structure
                self.focus_topic = focus_topic
                self.interaction_topic = interaction_topic
                
                return script
            else:
                print(f"   ❌ GPT-4 Fehler: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Enhanced Script-Generierung Fehler: {str(e)}")
            return None
    
    def save_enhanced_broadcast_info(self, timestamp, segments, content, script):
        """Speichert Enhanced Broadcast-Informationen"""
        
        info_file = self.output_dir / f"RadioX_Enhanced_Info_{timestamp}.txt"
        
        info_content = f"""RadioX 8:00 Enhanced Edition - Broadcast Info
==================================================

Timestamp: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Duration: {len(segments) * 12} Sekunden (geschätzt mit Interaktionen)
Segments: {len(segments)}
Audio Files: {len(segments)}

STRUKTUR: {getattr(self, 'current_structure', {}).get('name', 'Standard')}
BESCHREIBUNG: {getattr(self, 'current_structure', {}).get('description', 'Standard-Struktur')}

INTERAKTIONS-SCHWERPUNKTE:
🎯 FOKUSTHEMA: {getattr(self, 'focus_topic', {}).get('title', 'Nicht definiert') if hasattr(self, 'focus_topic') and self.focus_topic else 'Nicht definiert'}
💬 INTERAKTIONSTHEMA: {getattr(self, 'interaction_topic', {}).get('title', 'Nicht definiert') if hasattr(self, 'interaction_topic') and self.interaction_topic else 'Nicht definiert'}

SPRECHER:
- MARCEL: {self.marcel_voice_id} (Deine deutsche Stimme)
- JARVIS: {self.jarvis_voice_id} (AI-Style deutsch)

CONTENT:
- News Items: {len(content['news'])}
- Weather: ✅
- Bitcoin: ✅
- Enhanced Interactions: ✅

NEWS TOPICS:
"""
        
        # News Topics mit Markierungen hinzufügen
        for news in content['news']:
            marker = ""
            if hasattr(self, 'focus_topic') and self.focus_topic and news == self.focus_topic:
                marker = " 🎯 [FOKUSTHEMA]"
            elif hasattr(self, 'interaction_topic') and self.interaction_topic and news == self.interaction_topic:
                marker = " 💬 [INTERAKTIONSTHEMA]"
            
            info_content += f"- {news['title']}{marker}\n"
        
        info_content += f"\nSCRIPT:\n{'=' * 30}\n{script}\n\n"
        info_content += f"SEGMENTE:\n{'=' * 30}\n"
        
        for i, segment in enumerate(segments, 1):
            text_preview = segment['text'][:80] + "..." if len(segment['text']) > 80 else segment['text']
            info_content += f"{i:2d}. {segment['speaker']}: {text_preview}\n"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_content)
        
        print(f"📄 Enhanced Broadcast-Info gespeichert: {info_file}")
    
    async def create_enhanced_morning_broadcast(self):
        """Erstellt Enhanced Morgen-Broadcast mit verbesserter Interaktion"""
        
        print("🌅 STARTE ENHANCED 8:00 BROADCAST GENERIERUNG")
        print("=" * 50)
        
        # 1. Sammle frische Inhalte
        content = await self.collect_fresh_content()
        
        if not content['news']:
            print("❌ Keine neuen News gefunden! Broadcast abgebrochen.")
            return None
        
        # 2. Erstelle Enhanced Script mit Interaktionen
        script = self.create_enhanced_morning_script(content)
        if not script:
            print("❌ Enhanced Script-Generierung fehlgeschlagen!")
            return None
        
        # 3. Parse Script in Segmente
        segments = self.parse_script_to_segments(script)
        if not segments:
            print("❌ Keine Segmente erstellt!")
            return None
        
        # 4. Generiere Audio für alle Segmente
        print("🎙️ GENERIERE ENHANCED AUDIO-SEGMENTE")
        print("-" * 40)
        
        audio_files = []
        for i, segment in enumerate(segments, 1):
            print(f"   🎵 Segment {i}/{len(segments)}: {segment['speaker']}")
            audio_file = self.generate_audio_segment(segment)
            audio_files.append(audio_file)
        
        # 5. Füge Audio zusammen
        final_mp3 = self.create_concatenated_audio(audio_files)
        if not final_mp3:
            print("❌ Audio-Concatenation fehlgeschlagen!")
            return None
        
        # 6. Generiere Cover
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        cover_file = self.generate_morning_cover(timestamp)
        
        # 7. Füge Cover zu MP3 hinzu
        if cover_file:
            self.add_cover_to_mp3(final_mp3, cover_file)
            
            # Verifiziere Cover-Integration
            cover_success = self.verify_mp3_cover(final_mp3)
            if not cover_success:
                print("⚠️ Cover-Integration fehlgeschlagen - versuche alternative Methode...")
                self.add_cover_alternative(final_mp3, cover_file)
        
        # 8. Speichere Enhanced Broadcast-Info
        self.save_enhanced_broadcast_info(timestamp, segments, content, script)
        
        print("🎉 ENHANCED 8:00 BROADCAST ERFOLGREICH ERSTELLT!")
        print("=" * 50)
        print(f"📁 MP3: {final_mp3}")
        print(f"🎨 Cover: {cover_file}")
        print(f"📄 Info: RadioX_Enhanced_Info_{timestamp}.txt")
        print(f"🎭 Enhanced Interaktionen: ✅")
        
        return {
            'mp3_file': final_mp3,
            'cover_file': cover_file,
            'timestamp': timestamp,
            'segments': len(segments),
            'focus_topic': getattr(self, 'focus_topic', {}).get('title', 'N/A') if hasattr(self, 'focus_topic') and self.focus_topic else 'N/A'
        }

    def generate_audio_segment(self, segment):
        """Generiert Audio für ein Segment mit optimierter Zahlenaussprache"""
        
        speaker = segment['speaker']
        text = segment['text']
        
        # Formatiere Zahlen für optimale deutsche Aussprache
        formatted_text = self.number_formatter.format_text_for_elevenlabs(text)
        
        # Wähle Voice ID basierend auf Sprecher
        if speaker.upper() == 'MARCEL':
            voice_id = self.marcel_voice_id
        elif speaker.upper() == 'JARVIS':
            voice_id = self.jarvis_voice_id
        else:
            voice_id = self.marcel_voice_id  # Fallback
        
        print(f"   🎙️ {speaker}: {formatted_text[:50]}...")
        
        try:
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.elevenlabs_api_key
            }
            
            data = {
                'text': formatted_text,  # Verwende formatierten Text
                'model_id': 'eleven_multilingual_v2',
                'voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.8,
                    'style': 0.0,
                    'use_speaker_boost': True
                }
            }
            
            response = requests.post(
                f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                audio_file = self.output_dir / f"segment_{speaker}_{timestamp}.mp3"
                
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"      ✅ Audio generiert: {audio_file.name}")
                return audio_file
            else:
                print(f"      ❌ ElevenLabs Fehler: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"      ❌ Audio-Generierung Fehler: {str(e)}")
            return None


def main():
    """Hauptfunktion für Auto-Scheduler"""
    
    print("🕰️ RADIOX 8:00 AUTO-SCHEDULER")
    print("=" * 50)
    print("⏰ Automatische Show-Generierung alle halbe Stunde")
    print("🎭 Mit verbesserter Marcel & Jarvis Interaktion")
    print("🎯 Fokusthemen und Diskussionen")
    print("🔄 Kontinuierlicher Betrieb")
    print()
    
    try:
        scheduler = RadioX8UhrAutoScheduler()
        scheduler.start_scheduler()
        
    except KeyboardInterrupt:
        print("\n🛑 Scheduler gestoppt durch Benutzer")
    except Exception as e:
        print(f"\n❌ Scheduler-Fehler: {str(e)}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main() 