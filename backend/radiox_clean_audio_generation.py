#!/usr/bin/env python3

"""
RadioX Clean Audio Generation - Generiert MP3s aus sauberen Texten
Jarvis (Cool Starter) + Marcel (Lokal Expert) = KEINE Pause-Tags!
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import requests
import os

# Add src to path
sys.path.append(str(Path(__file__).parent))

from radiox_clean_broadcast import generate_clean_broadcast


class CleanAudioGenerator:
    """Generiert saubere Audio-Dateien ohne Pause-Tags"""
    
    def __init__(self):
        # ElevenLabs API
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable nicht gesetzt!")
        
        # Sprecher-Konfiguration
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Deine Stimme (Deutsch)
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # Jarvis AI Style (Cool!)
        
        # Output-Verzeichnis
        self.output_dir = Path("D:/DEV/muraschal/RadioX/output")
        self.output_dir.mkdir(exist_ok=True)
        
        # ElevenLabs API URL
        self.api_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
    def generate_audio(self, text, voice_id, speaker_name):
        """Generiert Audio mit ElevenLabs API"""
        
        print(f"🎤 Generiere Audio für {speaker_name}...")
        print(f"   Text-Länge: {len(text)} Zeichen")
        print(f"   Voice ID: {voice_id}")
        
        # API Request
        url = f"{self.api_url}/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }
        
        try:
            print(f"   📡 Sende Request an ElevenLabs...")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                # Timestamp für Dateiname
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                
                # Dateiname
                audio_file = self.output_dir / f"RadioX_{speaker_name}_Clean_{timestamp}.mp3"
                
                # Audio speichern
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024  # KB
                print(f"   ✅ Audio gespeichert: {audio_file.name} ({file_size:.1f} KB)")
                
                return {
                    "success": True,
                    "file": audio_file,
                    "size_kb": file_size,
                    "speaker": speaker_name
                }
                
            else:
                error_msg = f"ElevenLabs API Fehler {response.status_code}: {response.text}"
                print(f"   ❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "speaker": speaker_name
                }
                
        except Exception as e:
            error_msg = f"Audio-Generierung Fehler: {str(e)}"
            print(f"   ❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "speaker": speaker_name
            }
    
    def save_audio_info(self, results, script_data):
        """Speichert Audio-Informationen"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        info_file = self.output_dir / f"RadioX_Clean_Audio_Info_{timestamp}.txt"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("🎙️ RADIOX CLEAN AUDIO GENERATION\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏰ Broadcast Zeit: {script_data['script']['metadata']['broadcast_time']} Uhr\n")
            f.write(f"⏱️ Script Dauer: {script_data['script']['metadata']['total_duration']} Sekunden\n")
            f.write("\n")
            
            f.write("🎵 GENERIERTE AUDIO-DATEIEN:\n")
            f.write("-" * 40 + "\n")
            
            total_size = 0
            for result in results:
                if result["success"]:
                    f.write(f"✅ {result['speaker'].upper()}: {result['file'].name} ({result['size_kb']:.1f} KB)\n")
                    total_size += result['size_kb']
                else:
                    f.write(f"❌ {result['speaker'].upper()}: {result['error']}\n")
            
            f.write(f"\n📊 Gesamt-Größe: {total_size:.1f} KB\n")
            f.write("\n")
            
            # Sprecher-Texte
            f.write("📝 SPRECHER-TEXTE:\n")
            f.write("=" * 60 + "\n")
            
            f.write("\n🤖 JARVIS (Cool Starter):\n")
            f.write("-" * 40 + "\n")
            f.write(script_data['speaker_texts']['jarvis'])
            f.write("\n\n")
            
            f.write("🎤 MARCEL (Lokal Expert):\n")
            f.write("-" * 40 + "\n")
            f.write(script_data['speaker_texts']['marcel'])
            f.write("\n\n")
            
            # Verbesserungen
            f.write("🔧 CLEAN AUDIO VERBESSERUNGEN:\n")
            f.write("-" * 40 + "\n")
            f.write("✅ KEINE Pause-Tags mehr!\n")
            f.write("✅ Jarvis startet cool\n")
            f.write("✅ Saubere Text-Trennung\n")
            f.write("✅ Direkte Leerzeichen statt '...'\n")
            f.write("✅ Separate MP3-Dateien für jeden Sprecher\n")
        
        return info_file


async def generate_clean_audio():
    """Hauptfunktion für saubere Audio-Generierung"""
    
    print("🎙️ RADIOX CLEAN AUDIO GENERATION")
    print("=" * 60)
    print("🤖 Jarvis (Cool) + 🎤 Marcel (Lokal) = SAUBERE MP3s!")
    print(f"⏰ Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # SCHRITT 1: Sauberes Broadcast generieren
    print("🎭 GENERIERE SAUBERES BROADCAST")
    print("-" * 40)
    
    script_data = await generate_clean_broadcast()
    
    print()
    print("✅ Sauberes Broadcast generiert!")
    print(f"   🤖 Jarvis Text: {len(script_data['speaker_texts']['jarvis'])} Zeichen")
    print(f"   🎤 Marcel Text: {len(script_data['speaker_texts']['marcel'])} Zeichen")
    print()
    
    # SCHRITT 2: Audio-Generator initialisieren
    print("🎵 INITIALISIERE AUDIO-GENERATOR")
    print("-" * 40)
    
    try:
        audio_gen = CleanAudioGenerator()
        print("✅ Audio-Generator bereit!")
        print(f"   API Key: {'✅ Gesetzt' if audio_gen.api_key else '❌ Fehlt'}")
        print(f"   Output Dir: {audio_gen.output_dir}")
        print()
        
    except Exception as e:
        print(f"❌ Audio-Generator Fehler: {str(e)}")
        return
    
    # SCHRITT 3: Audio-Dateien generieren
    print("🎤 GENERIERE AUDIO-DATEIEN")
    print("-" * 40)
    
    results = []
    
    # Jarvis Audio (Cool Starter)
    jarvis_result = audio_gen.generate_audio(
        text=script_data['speaker_texts']['jarvis'],
        voice_id=audio_gen.jarvis_voice_id,
        speaker_name="Jarvis"
    )
    results.append(jarvis_result)
    
    print()
    
    # Marcel Audio (Lokal Expert)
    marcel_result = audio_gen.generate_audio(
        text=script_data['speaker_texts']['marcel'],
        voice_id=audio_gen.marcel_voice_id,
        speaker_name="Marcel"
    )
    results.append(marcel_result)
    
    print()
    
    # SCHRITT 4: Ergebnisse speichern
    print("📝 SPEICHERE AUDIO-INFORMATIONEN")
    print("-" * 40)
    
    info_file = audio_gen.save_audio_info(results, script_data)
    print(f"✅ Audio-Info gespeichert: {info_file.name}")
    print()
    
    # SCHRITT 5: Zusammenfassung
    print("🎉 CLEAN AUDIO GENERATION FERTIG!")
    print("=" * 60)
    
    successful_files = [r for r in results if r["success"]]
    failed_files = [r for r in results if not r["success"]]
    
    print(f"✅ Erfolgreich: {len(successful_files)}/{len(results)} Audio-Dateien")
    
    for result in successful_files:
        print(f"   🎵 {result['speaker']}: {result['file'].name} ({result['size_kb']:.1f} KB)")
    
    if failed_files:
        print(f"\n❌ Fehlgeschlagen: {len(failed_files)} Audio-Dateien")
        for result in failed_files:
            print(f"   💥 {result['speaker']}: {result['error']}")
    
    print(f"\n📝 Script: {script_data['script_file'].name}")
    print(f"📊 Audio-Info: {info_file.name}")
    
    if len(successful_files) == 2:
        print("\n🎯 BEREIT FÜR BROADCAST!")
        print("   - Beide Sprecher-Audios generiert")
        print("   - KEINE Pause-Tags")
        print("   - Jarvis startet cool")
        print("   - Saubere Text-Trennung")
    
    return {
        "results": results,
        "script_data": script_data,
        "info_file": info_file,
        "successful_count": len(successful_files)
    }


if __name__ == "__main__":
    asyncio.run(generate_clean_audio()) 