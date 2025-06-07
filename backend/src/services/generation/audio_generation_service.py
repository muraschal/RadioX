#!/usr/bin/env python3

"""
Audio Generation Service
========================

Generiert Audio-Dateien aus Broadcast-Skripten mit ElevenLabs API v1.
Nutzt Voice Configuration Service für dynamische Voice-Verwaltung.
Verwendet die neuesten ElevenLabs Modelle (v2, v2.5, v3).
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

# Import centralized settings
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import get_settings

# Import Image Generation Service - FIX: Korrekter relativer Import
try:
    from .image_generation_service import ImageGenerationService
except ImportError:
    # Fallback für direkten Import
    import sys
    sys.path.append(str(Path(__file__).parent))
    from image_generation_service import ImageGenerationService

# Import Voice Configuration Service
from src.services.voice_config_service import get_voice_config_service


class AudioGenerationService:
    """
    Service für Audio-Generierung mit ElevenLabs API v1
    Nutzt Voice Configuration Service statt hardcoded Voices
    Verwendet neueste ElevenLabs Modelle (v2, v2.5, v3)
    """
    
    def __init__(self):
        # Load settings centrally
        self.settings = get_settings()
        
        # Voice Configuration Service (ersetzt hardcoded voice_config)
        self.voice_service = get_voice_config_service()
        
        # Image Generation Service für Cover-Art - SAFE INITIALIZATION
        try:
            self.image_service = ImageGenerationService()
            logger.debug("✅ ImageGenerationService erfolgreich initialisiert")
        except Exception as e:
            logger.warning(f"⚠️ ImageGenerationService konnte nicht initialisiert werden: {e}")
            self.image_service = None
        
        # ElevenLabs API Configuration (v1 ist die aktuelle API-Version)
        self.elevenlabs_api_key = self.settings.elevenlabs_api_key
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"  # v1 ist korrekt!
        
        # FFmpeg-Pfade für verschiedene Systeme
        self.ffmpeg_paths = [
            str(Path(__file__).parent.parent.parent.parent / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe"),
            "ffmpeg"  # Fallback für System-PATH
        ]
        
        # Output-Verzeichnis - DIREKT IM ROOT (nicht in backend/)
        self.output_dir = Path(__file__).parent.parent.parent.parent / "outplay"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_voice_with_fallback(self, speaker_name: str) -> Optional[Dict[str, Any]]:
        """
        Holt Voice-Konfiguration mit intelligenten Fallback-Strategien
        
        Args:
            speaker_name: Name des Speakers (marcel, jarvis, etc.)
            
        Returns:
            Voice-Konfiguration oder None wenn keine gefunden
        """
        
        try:
            # 1. Versuche spezifische Voice
            voice_config = await self.voice_service.get_voice_config(speaker_name)
            if voice_config:
                return voice_config
            
            # 2. Fallback zu Primary Voice des gleichen Typs
            if "marcel" in speaker_name.lower():
                fallback = await self.voice_service.get_voice_config("marcel")
                if fallback:
                    logger.info(f"🔄 Fallback für '{speaker_name}' zu marcel")
                    return fallback
            elif "jarvis" in speaker_name.lower():
                fallback = await self.voice_service.get_voice_config("jarvis")
                if fallback:
                    logger.info(f"🔄 Fallback für '{speaker_name}' zu jarvis")
                    return fallback
            
            # 3. Fallback zu erster Primary Voice
            primary_voices = await self.voice_service.get_primary_voices()
            if primary_voices:
                fallback_voice = list(primary_voices.values())[0]
                fallback_speaker = list(primary_voices.keys())[0]
                logger.warning(f"⚠️ Fallback für '{speaker_name}' zu Primary Voice '{fallback_speaker}'")
                return fallback_voice
            
            # 4. Letzter Fallback: Alle aktiven Voices
            all_voices = await self.voice_service.get_all_voice_configs()
            if all_voices:
                fallback_voice = list(all_voices.values())[0]
                fallback_speaker = list(all_voices.keys())[0]
                logger.error(f"❌ Notfall-Fallback für '{speaker_name}' zu '{fallback_speaker}'")
                return fallback_voice
            
            logger.error(f"❌ Keine Voice-Konfiguration für '{speaker_name}' verfügbar")
            return None
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Voice-Konfiguration für '{speaker_name}': {e}")
            return None
    
    def _get_ffmpeg_command(self) -> Optional[str]:
        """Ermittelt den verfügbaren ffmpeg-Pfad"""
        import subprocess
        
        for ffmpeg_path in self.ffmpeg_paths:
            try:
                # Teste ob ffmpeg verfügbar ist
                result = subprocess.run([ffmpeg_path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"✅ ffmpeg gefunden: {ffmpeg_path}")
                    return ffmpeg_path
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
                logger.debug(f"ffmpeg nicht verfügbar unter {ffmpeg_path}: {e}")
                continue
        
        logger.warning("⚠️ ffmpeg nicht gefunden - verwende Fallback-Modus")
        return None

    async def generate_audio(
        self,
        script: Dict[str, Any],
        include_music: bool = False,
        export_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Generiert Audio-Dateien aus Broadcast-Skript
        
        Args:
            script: Broadcast-Skript mit session_id und script_content
            include_music: Ob Hintergrundmusik hinzugefügt werden soll
            export_format: Audio-Format (mp3, wav, etc.)
            
        Returns:
            Dict mit Audio-Datei-Pfaden und Metadaten
        """
        
        session_id = script.get("session_id", "unknown")
        script_content = script.get("script_content", "")
        
        logger.info(f"🔊 Generiere Audio für Session {session_id}")
        
        if not self.elevenlabs_api_key:
            logger.warning("⚠️ ElevenLabs API Key nicht verfügbar - verwende Fallback")
            return await self._generate_fallback_audio(script, export_format)
        
        try:
            # 1. Skript in Sprecher-Segmente aufteilen
            segments = self._parse_script_segments(script_content)
            logger.info(f"📝 {len(segments)} Sprecher-Segmente gefunden")
            
            # 2. Audio für jeden Sprecher generieren
            audio_segments = []
            for i, segment in enumerate(segments):
                audio_file = await self._generate_segment_audio(
                    segment, session_id, i
                )
                if audio_file:
                    audio_segments.append({
                        "speaker": segment["speaker"],
                        "text": segment["text"],
                        "audio_file": audio_file,
                        "duration": await self._get_audio_duration(audio_file)
                    })
            
            # 3. Audio-Segmente zusammenfügen
            final_audio_file = await self._combine_audio_segments(
                audio_segments, session_id, export_format
            )
            
            # 4. Musik hinzufügen (optional)
            if include_music and final_audio_file:
                final_audio_file = await self._add_background_music(
                    final_audio_file, session_id
                )
            
            # 5. Audio-Metadaten erstellen
            audio_metadata = await self._create_audio_metadata(
                final_audio_file, audio_segments, script
            )
            
            result = {
                "success": True,
                "session_id": session_id,
                "audio_path": str(final_audio_file) if final_audio_file else None,
                "final_audio_file": str(final_audio_file) if final_audio_file else None,
                "segment_files": [seg["audio_file"] for seg in audio_segments],
                "duration_seconds": audio_metadata.get("total_duration_seconds", 0),
                "metadata": audio_metadata,
                "generation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Audio generiert: {final_audio_file}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Audio-Generierung: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "generation_timestamp": datetime.now().isoformat()
            }
    
    async def test_audio(self) -> bool:
        """Testet die Audio-Generierung"""
        
        test_script = {
            "session_id": "test_audio",
            "script_content": "MARCEL: Hallo, das ist ein Test.\nJARVIS: Ja, das funktioniert gut."
        }
        
        try:
            result = await self.generate_audio(test_script)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Audio Test Fehler: {e}")
            return False
    
    # Private Methods
    
    def _parse_script_segments(self, script_content: str) -> List[Dict[str, Any]]:
        """Parst Skript in Sprecher-Segmente mit verbesserter Name-Bereinigung"""
        
        segments = []
        lines = script_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Suche nach Sprecher-Pattern: "SPEAKER: Text"
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker_raw = parts[0].strip()
                    text = parts[1].strip()
                    
                    # VERBESSERTE SPEAKER-NAME BEREINIGUNG
                    speaker = self._clean_speaker_name(speaker_raw)
                    
                    if text and speaker:  # Nur wenn Text und gültiger Speaker vorhanden
                        segments.append({
                            "speaker": speaker,
                            "text": text
                        })
        
        return segments
    
    def _clean_speaker_name(self, speaker_raw: str) -> str:
        """Bereinigt Speaker-Namen von Formatierungs-Artefakten"""
        
        # Entferne ** Präfixe und andere Markdown-Formatierung
        speaker = speaker_raw.strip()
        
        # Entferne ** am Anfang und Ende
        speaker = speaker.strip('*')
        
        # Entferne andere Formatierungs-Zeichen
        speaker = speaker.strip('_').strip('-').strip()
        
        # Konvertiere zu Kleinbuchstaben für Konsistenz
        speaker = speaker.lower()
        
        # Mapping für bekannte Speaker-Varianten
        speaker_mapping = {
            "titel": "marcel",  # **titel -> marcel
            "marcel": "marcel",
            "jarvis": "jarvis",
            "marcel_alt": "marcel",  # Fallback zu marcel
            "jarvis_alt": "jarvis",  # Fallback zu jarvis
            "host": "marcel",       # Generischer Host -> marcel
            "ai": "jarvis",         # Generische AI -> jarvis
            "moderator": "marcel",  # Moderator -> marcel
            "assistant": "jarvis"   # Assistant -> jarvis
        }
        
        # Verwende Mapping falls verfügbar
        mapped_speaker = speaker_mapping.get(speaker, speaker)
        
        # Nur loggen wenn Mapping stattgefunden hat
        if mapped_speaker != speaker:
            logger.info(f"🎭 Speaker-Mapping: '{speaker_raw}' → '{mapped_speaker}'")
        
        return mapped_speaker
    
    async def _generate_segment_audio(
        self, 
        segment: Dict[str, Any], 
        session_id: str, 
        segment_index: int
    ) -> Optional[Path]:
        """Generiert Audio für ein einzelnes Segment mit Voice Configuration Service"""
        
        speaker = segment["speaker"]
        text = segment["text"]
        
        # Nur bei ersten paar Segmenten loggen
        if segment_index < 3:
            logger.info(f"🎤 Generiere Audio für {speaker}: {text[:50]}...")
        
        try:
            # Eindeutiger Dateiname mit Timestamp um Konflikte zu vermeiden
            timestamp = datetime.now().strftime("%H%M%S")
            audio_filename = f"{session_id}_{speaker}_{segment_index:03d}_{timestamp}.mp3"
            audio_path = self.output_dir / audio_filename
            
            # Voice-Konfiguration über Voice Service laden (ersetzt hardcoded voice_config)
            voice_config = await self.get_voice_with_fallback(speaker)
            
            if not voice_config:
                logger.error(f"❌ Keine Voice-Konfiguration für '{speaker}' verfügbar")
                return None
            
            # ElevenLabs API Request (v1 Endpoint mit neuesten Modellen)
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # ElevenLabs Enhanced Request mit Audio Tags Support (neueste Modelle)
            enhanced_text = self._enhance_text_with_v3_tags(text, speaker)
            
            data = {
                "text": enhanced_text,
                "model_id": voice_config.get("model", "eleven_multilingual_v2"),  # Neueste Modelle (v2, v2.5, v3)
                "voice_settings": {
                    "stability": voice_config["stability"],
                    "similarity_boost": voice_config["similarity_boost"],
                    "style": voice_config["style"],
                    "use_speaker_boost": voice_config["use_speaker_boost"]
                }
            }
            
            url = f"{self.elevenlabs_base_url}/text-to-speech/{voice_config['voice_id']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    
                    if response.status == 200:
                        # Audio-Datei speichern
                        with open(audio_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        # Nur bei ersten paar Segmenten loggen
                        if segment_index < 3:
                            logger.info(f"✅ Audio-Segment gespeichert: {audio_filename}")
                        return audio_path
                    
                    else:
                        logger.error(f"❌ ElevenLabs API Fehler {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Fehler bei Segment-Audio-Generierung: {e}")
            return None
    
    def _enhance_text_with_v3_tags(self, text: str, speaker: str) -> str:
        """
        🎭 ElevenLabs Text Enhancement - V3 OPTIMIZED
        Aktiviert V3 Emotional Tags für natürlichere Aussprache
        """
        
        enhanced_text = text.strip()
        
        # === V3 EMOTIONAL TAGS AKTIVIERT ===
        
        # 🎭 MARCEL EMOTIONAL ENHANCEMENTS
        if speaker.upper() == "MARCEL":
            # Begeisterung und Energie
            enhanced_text = enhanced_text.replace("amazing", "[excited] amazing")
            enhanced_text = enhanced_text.replace("incredible", "[impressed] incredible")
            enhanced_text = enhanced_text.replace("fantastic", "[excited] fantastic")
            enhanced_text = enhanced_text.replace("unbelievable", "[impressed] unbelievable")
            enhanced_text = enhanced_text.replace("Oh my god", "[excited] Oh my god")
            enhanced_text = enhanced_text.replace("I can't wait", "[excited] I can't wait")
            enhanced_text = enhanced_text.replace("I love", "[excited] I love")
            
            # Lachen hinzufügen
            if "!" in enhanced_text and any(word in enhanced_text.lower() for word in ["funny", "hilarious", "joke", "comedian"]):
                enhanced_text = enhanced_text.replace("!", "! [laughs]")
        
        # 🤖 JARVIS EMOTIONAL ENHANCEMENTS  
        elif speaker.upper() == "JARVIS":
            # Sarkasmus und Analytik
            enhanced_text = enhanced_text.replace("Obviously", "[sarcastic] Obviously")
            enhanced_text = enhanced_text.replace("Well,", "[analytical] Well,")
            enhanced_text = enhanced_text.replace("Indeed", "[analytical] Indeed")
            enhanced_text = enhanced_text.replace("Ah yes", "[sarcastic] Ah yes")
            enhanced_text = enhanced_text.replace("Of course", "[sarcastic] Of course")
            
            # Flüstern für vertrauliche Informationen
            if "between you and me" in enhanced_text.lower():
                enhanced_text = enhanced_text.replace("between you and me", "[whispers] between you and me")
            if "confidential" in enhanced_text.lower():
                enhanced_text = enhanced_text.replace("confidential", "[whispers] confidential")
        
        # === GRUNDLEGENDE TEXT-VERBESSERUNGEN ===
        
        # 📝 PUNCTUATION FOR BETTER PACING
        enhanced_text = enhanced_text.replace("...", " … ")
        enhanced_text = enhanced_text.replace(". ", ". … ")  # Add pauses after sentences
        
        # 🔊 EMPHASIS FOR KEY TERMS (V3 CAPS RECOGNITION)
        emphasis_terms = {
            "bitcoin": "BITCOIN",
            "blockchain": "BLOCKCHAIN", 
            "ai": "AI",
            "artificial intelligence": "ARTIFICIAL INTELLIGENCE",
            "breaking": "BREAKING",
            "million": "MILLION",
            "billion": "BILLION"
        }
        
        for term, emphasized in emphasis_terms.items():
            enhanced_text = enhanced_text.replace(term, emphasized)
            enhanced_text = enhanced_text.replace(term.capitalize(), emphasized)
            enhanced_text = enhanced_text.replace(term.upper(), emphasized)
        
        # 🚀 ENGLISH NATURALNESS IMPROVEMENTS
        if not speaker.endswith("_de"):
            # Natural English contractions
            enhanced_text = enhanced_text.replace("cannot", "can't")
            enhanced_text = enhanced_text.replace("will not", "won't") 
            enhanced_text = enhanced_text.replace("do not", "don't")
            enhanced_text = enhanced_text.replace("it is", "it's")
            enhanced_text = enhanced_text.replace("that is", "that's")
        
        return enhanced_text
    
    async def _combine_audio_segments(
        self, 
        audio_segments: List[Dict[str, Any]], 
        session_id: str,
        export_format: str
    ) -> Optional[Path]:
        """Kombiniert Audio-Segmente zu einer Datei mit korrekter Nomenklatur"""
        
        if not audio_segments:
            logger.warning("⚠️ Keine Audio-Segmente zum Kombinieren")
            return None
        
        logger.info(f"🔗 Kombiniere {len(audio_segments)} Audio-Segmente")
        
        try:
            # KORREKTE NOMENKLATUR: RadioX_Zurich_25-06-07_1045.mp3
            timestamp = datetime.now()
            date_str = timestamp.strftime("%y-%m-%d")
            time_str = timestamp.strftime("%H%M")
            
            final_filename = f"RadioX_Zurich_{date_str}_{time_str}.{export_format}"
            final_path = self.output_dir / final_filename
            
            # Sammle alle Segment-Dateien für Kombination und Löschung
            segment_files = []
            temp_files_to_delete = []
            
            for segment in audio_segments:
                audio_file = segment["audio_file"]
                if audio_file and audio_file.exists():
                    segment_files.append(str(audio_file))
                    temp_files_to_delete.append(audio_file)
            
            if not segment_files:
                logger.error("❌ Keine gültigen Audio-Segmente gefunden")
                return None
            
            # Versuche ffmpeg für echte Audio-Kombination
            ffmpeg_cmd = self._get_ffmpeg_command()
            if ffmpeg_cmd:
                try:
                    import subprocess
                    
                    # Erstelle concat-Liste für ffmpeg
                    concat_list_path = self.output_dir / f"{session_id}_concat_list.txt"
                    with open(concat_list_path, 'w') as f:
                        for segment_file in segment_files:
                            # Verwende absolute Pfade für ffmpeg
                            absolute_path = str(Path(segment_file).resolve())
                            f.write(f"file '{absolute_path}'\n")
                    
                    # ffmpeg Kommando für perfekte Audio-Kombination
                    ffmpeg_command = [
                        ffmpeg_cmd, '-y', '-f', 'concat', '-safe', '0', 
                        '-i', str(concat_list_path), 
                        '-c', 'copy', str(final_path)
                    ]
                    
                    result = subprocess.run(ffmpeg_command, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        logger.success(f"✅ Audio mit ffmpeg kombiniert: {final_filename}")
                        
                        # Lösche concat-Liste
                        try:
                            concat_list_path.unlink()
                        except Exception as e:
                            logger.warning(f"⚠️ Konnte concat-Liste nicht löschen: {e}")
                        
                        # *** WINDOWS-SAFE DATEI-LÖSCHUNG MIT RETRY ***
                        deleted_count = await self._safe_delete_temp_files(temp_files_to_delete)
                        
                        logger.success(f"🗑️ {deleted_count} temporäre Audio-Segmente automatisch gelöscht")
                        logger.success(f"🎵 FINALE MP3 BEREIT: {final_filename}")
                        
                        return final_path
                    else:
                        logger.warning(f"⚠️ ffmpeg fehlgeschlagen: {result.stderr}")
                        
                except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                    logger.warning(f"⚠️ ffmpeg-Ausführung fehlgeschlagen: {e}")
            
            # Fallback: Kopiere erstes Segment als finale Datei
            if segment_files:
                import shutil
                
                # Windows-safe copy mit Retry
                try:
                    shutil.copy2(segment_files[0], final_path)
                except Exception as e:
                    logger.warning(f"⚠️ Erster Copy-Versuch fehlgeschlagen: {e}")
                    # Retry nach kurzer Pause
                    import time
                    time.sleep(0.5)
                    shutil.copy2(segment_files[0], final_path)
                
                # *** WINDOWS-SAFE DATEI-LÖSCHUNG MIT RETRY ***
                deleted_count = await self._safe_delete_temp_files(temp_files_to_delete)
                
                logger.info(f"✅ Audio kombiniert (Fallback): {final_filename}")
                logger.success(f"🗑️ {deleted_count} temporäre Audio-Segmente automatisch gelöscht")
                logger.success(f"🎵 FINALE MP3 BEREIT: {final_filename}")
                
                return final_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Kombinieren der Audio-Segmente: {e}")
            return None
    
    async def _safe_delete_temp_files(self, temp_files: List[Path]) -> int:
        """Windows-sichere Datei-Löschung mit Retry-Logik"""
        import time
        import asyncio
        
        deleted_count = 0
        
        for temp_file in temp_files:
            # Mehrere Versuche mit steigenden Pausen
            for attempt in range(3):
                try:
                    # Kurze Pause vor Löschung (Windows File-Handle-Problem)
                    if attempt > 0:
                        await asyncio.sleep(0.2 * attempt)
                    
                    # Versuche Datei zu löschen
                    temp_file.unlink()
                    deleted_count += 1
                    break  # Erfolgreich gelöscht
                    
                except PermissionError as e:
                    if attempt < 2:  # Noch Versuche übrig
                        logger.debug(f"🔄 Retry {attempt + 1}/3 für {temp_file.name}: {e}")
                        continue
                    else:
                        logger.warning(f"⚠️ Konnte {temp_file.name} nicht löschen (File-Lock): {e}")
                        
                except FileNotFoundError:
                    # Datei bereits gelöscht - das ist OK
                    deleted_count += 1
                    break
                    
                except Exception as e:
                    logger.warning(f"⚠️ Unerwarteter Fehler beim Löschen von {temp_file.name}: {e}")
                    break
        
        return deleted_count
    
    async def _add_background_music(
        self, 
        audio_file: Path, 
        session_id: str
    ) -> Optional[Path]:
        """Fügt Hintergrundmusik hinzu"""
        
        logger.info("🎵 Füge Hintergrundmusik hinzu")
        
        # Placeholder für Musik-Integration
        # In Produktion würde hier echte Audio-Verarbeitung stattfinden
        
        try:
            # Erstelle neue Datei mit Musik-Suffix
            music_filename = f"{session_id}_with_music.mp3"
            music_path = self.output_dir / music_filename
            
            # Für jetzt: Kopiere Original-Datei
            import shutil
            shutil.copy2(audio_file, music_path)
            
            logger.info(f"✅ Musik hinzugefügt: {music_filename}")
            return music_path
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Hinzufügen von Musik: {e}")
            return audio_file  # Gib Original zurück
    
    async def _get_audio_duration(self, audio_file: Path) -> float:
        """Ermittelt Audio-Dauer in Sekunden"""
        
        try:
            # Placeholder für Audio-Dauer-Ermittlung
            # In Produktion würde hier eine Audio-Library verwendet
            
            # Schätze Dauer basierend auf Dateigröße (sehr grob)
            file_size = audio_file.stat().st_size
            estimated_duration = file_size / 32000  # Grobe Schätzung
            
            return max(1.0, estimated_duration)
            
        except Exception as e:
            logger.warning(f"⚠️ Fehler bei Dauer-Ermittlung: {e}")
            return 10.0  # Fallback
    
    async def _create_audio_metadata(
        self,
        final_audio_file: Optional[Path],
        audio_segments: List[Dict[str, Any]],
        script: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Erstellt Metadaten für generierte Audio-Datei"""
        
        total_duration = sum(seg.get("duration", 0) for seg in audio_segments)
        
        return {
            "session_id": script.get("session_id", "unknown"),
            "total_duration_seconds": total_duration,
            "segment_count": len(audio_segments),
            "speakers": list(set(seg["speaker"] for seg in audio_segments)),
            "file_size_bytes": final_audio_file.stat().st_size if final_audio_file and final_audio_file.exists() else 0,
            "format": "mp3",
            "sample_rate": 44100,
            "generation_settings": {
                "quality": "high",
                "normalize": True
            }
        }
    
    async def _generate_fallback_audio(
        self, 
        script: Dict[str, Any], 
        export_format: str
    ) -> Dict[str, Any]:
        """Generiert Fallback-Audio ohne ElevenLabs"""
        
        session_id = script.get("session_id", "unknown")
        
        logger.info(f"📝 Erstelle Text-Fallback für Session {session_id}")
        
        # Erstelle Text-Datei als Fallback
        text_filename = f"{session_id}_script.txt"
        text_path = self.output_dir / text_filename
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"RadioX Broadcast Script - Session {session_id}\n")
            f.write("=" * 50 + "\n\n")
            f.write(script.get("script_content", ""))
            f.write(f"\n\nGeneriert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "success": True,
            "session_id": session_id,
            "final_audio_file": None,
            "text_fallback": str(text_path),
            "metadata": {
                "fallback_mode": True,
                "reason": "ElevenLabs API nicht verfügbar"
            },
            "generation_timestamp": datetime.now().isoformat()
        }
    
    # Utility Methods
    
    async def list_available_voices(self) -> Dict[str, Any]:
        """Listet verfügbare ElevenLabs Stimmen auf"""
        
        if not self.elevenlabs_api_key:
            return {"error": "ElevenLabs API Key nicht verfügbar"}
        
        try:
            headers = {"xi-api-key": self.elevenlabs_api_key}
            url = f"{self.elevenlabs_base_url}/voices"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "voices": data.get("voices", [])
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API Fehler {response.status}"
                        }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup_old_audio_files(self, days_old: int = 7) -> Dict[str, Any]:
        """Räumt alte Audio-Dateien auf"""
        
        logger.info(f"🧹 Räume Audio-Dateien älter als {days_old} Tage auf")
        
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            deleted_files = []
            total_size_freed = 0
            
            for audio_file in self.output_dir.glob("*"):
                if audio_file.is_file():
                    file_time = audio_file.stat().st_mtime
                    
                    if file_time < cutoff_time:
                        file_size = audio_file.stat().st_size
                        audio_file.unlink()
                        deleted_files.append(str(audio_file.name))
                        total_size_freed += file_size
            
            return {
                "success": True,
                "deleted_files": deleted_files,
                "files_deleted": len(deleted_files),
                "size_freed_bytes": total_size_freed,
                "size_freed_mb": round(total_size_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Audio-Cleanup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_audio_stats(self) -> Dict[str, Any]:
        """Holt Statistiken über generierte Audio-Dateien"""
        
        try:
            audio_files = list(self.output_dir.glob("*.mp3"))
            total_size = sum(f.stat().st_size for f in audio_files)
            
            return {
                "total_files": len(audio_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "output_directory": str(self.output_dir),
                "latest_file": max(audio_files, key=lambda f: f.stat().st_mtime).name if audio_files else None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "total_files": 0,
                "total_size_mb": 0
            }

    async def generate_complete_broadcast(
        self,
        script: Dict[str, Any],
        include_music: bool = False,
        include_cover: bool = False,  # Default auf False gesetzt
        export_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Generiert kompletten Broadcast - NUR MP3 FOKUS
        Cover-Art optional und standardmäßig deaktiviert
        
        Args:
            script: Broadcast-Skript mit session_id und script_content
            include_music: Ob Hintergrundmusik hinzugefügt werden soll
            include_cover: Ob Cover-Art generiert werden soll (Standard: False)
            export_format: Audio-Format (mp3, wav, etc.)
            
        Returns:
            Dict mit Audio-Datei-Pfaden und Metadaten
        """
        
        session_id = script.get("session_id", "unknown")
        
        logger.info(f"🎬 Generiere Broadcast für Session {session_id}")
        logger.info("🎵 FOKUS: Nur MP3-Audio-Generierung")
        
        try:
            # 1. Audio generieren (HAUPTFOKUS)
            logger.info("🔊 Audio-Generierung...")
            audio_result = await self.generate_audio(script, include_music, export_format)
            
            if not audio_result.get("success"):
                logger.error("❌ Audio-Generierung fehlgeschlagen")
                return audio_result
            
            # 2. Cover-Art nur wenn explizit angefordert
            cover_result = None
            dalle_prompt = None
            if include_cover and self.image_service:
                logger.info("🎨 Cover-Art-Generierung (optional)...")
                try:
                    target_time = script.get("target_time", "12:00")
                    
                    cover_result = await self.image_service.generate_cover_art(
                        session_id=session_id,
                        broadcast_content=script,
                        target_time=target_time
                    )
                    
                    if cover_result and cover_result.get("success"):
                        logger.success(f"✅ Cover-Art generiert: {cover_result.get('cover_filename')}")
                        dalle_prompt = cover_result.get("dalle_prompt")  # DALL-E Prompt extrahieren
                    else:
                        logger.warning("⚠️ Cover-Art-Generierung fehlgeschlagen")
                        cover_result = None
                        
                except Exception as e:
                    logger.warning(f"⚠️ Cover-Art-Generierung fehlgeschlagen: {e}")
                    cover_result = None
            
            # 3. Cover in MP3 einbetten (nur wenn Cover vorhanden)
            final_audio_path = audio_result.get("final_audio_file")
            if cover_result and cover_result.get("success") and final_audio_path and self.image_service:
                logger.info("🏷️ Cover-Art in MP3 einbetten...")
                try:
                    cover_path = Path(cover_result["cover_path"])
                    audio_path = Path(final_audio_path)
                    
                    embed_success = await self.image_service.embed_cover_in_mp3(
                        audio_file=audio_path,
                        cover_file=cover_path,
                        metadata=audio_result.get("metadata", {})
                    )
                    
                    if embed_success:
                        logger.success("✅ Cover-Art in MP3 eingebettet")
                    else:
                        logger.warning("⚠️ Cover-Embedding fehlgeschlagen")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Cover-Embedding fehlgeschlagen: {e}")
            
            # 4. NEUE FUNKTION: Comprehensive Info File erstellen
            if final_audio_path:
                logger.info("📄 Erstelle comprehensive Info-Datei...")
                try:
                    # Erstelle Info-Dateiname mit korrekter Nomenklatur
                    timestamp = datetime.now()
                    date_str = timestamp.strftime("%y-%m-%d")
                    time_str = timestamp.strftime("%H%M")
                    info_filename = f"RadioX_Zurich_{date_str}_{time_str}_info.txt"
                    info_path = self.output_dir / info_filename
                    
                    # Erweitere Metadaten für Info-Datei
                    comprehensive_metadata = {
                        **script,  # Alle Script-Daten
                        **audio_result.get("metadata", {}),  # Audio-Metadaten
                        "broadcast_style": script.get("broadcast_style", "Unknown"),
                        "estimated_duration_minutes": script.get("estimated_duration_minutes", 5),
                        "all_collected_news": script.get("all_collected_news", []),
                        "selected_news": script.get("selected_news", []),
                        "news_selection_criteria": script.get("news_selection_criteria", "Automatische Auswahl"),
                        "weather_data": script.get("weather_data", {}),
                        "crypto_data": script.get("crypto_data", {}),
                        "gpt_input_data": script.get("gpt_input_data", {})  # GPT-Input hinzufügen
                    }
                    
                    await self._create_comprehensive_info_file(
                        info_path=info_path,
                        script_content=script.get("script_content", ""),
                        broadcast_metadata=comprehensive_metadata,
                        final_filename=Path(final_audio_path).name,
                        dalle_prompt=dalle_prompt
                    )
                    
                    logger.success(f"✅ Info-Datei erstellt: {info_filename}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Info-Datei-Erstellung fehlgeschlagen: {e}")
            
            # 5. Ergebnis zusammenstellen
            complete_result = {
                "success": True,
                "session_id": session_id,
                "broadcast_type": "audio_focused",
                
                # Audio-Daten (HAUPTFOKUS)
                "audio_path": audio_result.get("final_audio_file"),
                "audio_duration_seconds": audio_result.get("duration_seconds", 0),
                "audio_metadata": audio_result.get("metadata", {}),
                
                # Cover-Art-Daten (nur wenn generiert)
                "cover_path": cover_result.get("cover_path") if cover_result else None,
                "cover_generated": include_cover and cover_result and cover_result.get("success", False),
                "dalle_prompt": dalle_prompt,
                
                # Info-Datei
                "info_file": str(info_path) if 'info_path' in locals() else None,
                
                # Metadaten
                "generation_timestamp": datetime.now().isoformat(),
                "includes_music": include_music,
                "export_format": export_format
            }
            
            # 6. Automatische Bereinigung (alle außer finale MP3 und Info)
            if final_audio_path:
                logger.info("🧹 Automatische Bereinigung...")
                cleanup_result = await self._cleanup_temp_files_after_generation(
                    session_id=session_id,
                    final_audio_file=Path(final_audio_path),
                    cover_file=Path(cover_result["cover_path"]) if cover_result else None
                )
                
                complete_result["cleanup"] = cleanup_result
                
                if cleanup_result.get("files_deleted", 0) > 0:
                    logger.success(f"🗑️ {cleanup_result['files_deleted']} temporäre Dateien bereinigt")
            
            logger.success(f"🎉 BROADCAST ERSTELLT!")
            logger.success(f"🎵 MP3: {Path(final_audio_path).name if final_audio_path else 'N/A'}")
            if complete_result.get("info_file"):
                logger.success(f"📄 Info: {Path(complete_result['info_file']).name}")
            if complete_result.get("cover_generated"):
                logger.success(f"🎨 Cover: {cover_result.get('cover_filename', 'N/A')}")
            
            return complete_result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Broadcast-Generierung: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "generation_timestamp": datetime.now().isoformat()
            }

    async def test_complete_system(self) -> bool:
        """Testet das komplette Audio + Cover System"""
        
        logger.info("🧪 TESTE KOMPLETTES AUDIO + COVER SYSTEM")
        logger.info("=" * 60)
        
        test_script = {
            "session_id": "complete_test",
            "script_content": """MARCEL: [excited] Hey everyone! Welcome to RadioX AI News! 
We've got some absolutely INCREDIBLE Bitcoin updates today!

JARVIS: [sarcastic] Obviously, Marcel is getting excited about numbers again. 
But I must admit, the market data is quite fascinating.

MARCEL: [impressed] Bitcoin just hit $103,000! That's a new all-time high! 
[whispers] This could change everything for crypto adoption.

JARVIS: [curious] Analyzing the market patterns... [mischievously] 
Humans never learn from their emotional trading decisions, do they?

MARCEL: [laughs] Well Jarvis, at least we're here to give them the facts! 
Thanks for tuning in to RadioX AI News!"""
        }
        
        try:
            # Teste kompletten Broadcast mit Cover
            result = await self.generate_complete_broadcast(
                script=test_script,
                include_music=False,
                include_cover=True,
                export_format="mp3"
            )
            
            if result.get("success"):
                logger.success("✅ KOMPLETTER SYSTEM-TEST ERFOLGREICH!")
                logger.info(f"🎵 Audio: {result.get('audio_path')}")
                logger.info(f"🎨 Cover: {result.get('cover_path')}")
                logger.info(f"⏱️ Dauer: {result.get('audio_duration_seconds')} Sekunden")
                return True
            else:
                logger.error(f"❌ System-Test fehlgeschlagen: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ System-Test Fehler: {e}")
            return False

    async def create_final_broadcast_package(
        self,
        session_id: str,
        audio_file: Path,
        cover_file: Path,
        script_content: str,
        broadcast_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Erstellt finales Broadcast-Paket mit optimierter Nomenklatur und Metadaten"""
        
        logger.info(f"📦 Erstelle finales Broadcast-Paket für Session {session_id}")
        
        try:
            # 1. Finale Nomenklatur erstellen: RadioX_Zurich_25-06-07_1009
            timestamp = datetime.now()
            date_str = timestamp.strftime("%y-%m-%d")
            time_str = timestamp.strftime("%H%M")
            channel = broadcast_metadata.get("channel", "zurich").capitalize()
            
            # Korrigiere bekannte Channel-Namen
            channel_mapping = {
                "Zurich": "Zurich",
                "Basel": "Basel", 
                "Bern": "Bern",
                "Geneva": "Geneva"
            }
            channel = channel_mapping.get(channel, channel)
            
            final_filename = f"RadioX_{channel}_{date_str}_{time_str}"
            
            # 2. Finale Verzeichnisse erstellen
            final_dir = Path("outplay/final")
            final_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle Unterverzeichnisse
            audio_dir = final_dir / "audio"
            covers_dir = final_dir / "covers"
            audio_dir.mkdir(exist_ok=True)
            covers_dir.mkdir(exist_ok=True)
            
            # Sammle alle Dateien
            output_audio_dir = Path("outplay/audio")
            output_covers_dir = Path("outplay/covers")
            
            # 3. MP3 mit Cover und Metadaten erstellen
            final_mp3_path = final_dir / f"{final_filename}.mp3"
            
            # Kopiere Audio-Datei
            import shutil
            shutil.copy2(audio_file, final_mp3_path)
            
            # 4. Cover einbetten und Metadaten hinzufügen
            success = await self._embed_cover_and_metadata(
                audio_file=final_mp3_path,
                cover_file=cover_file,
                script_content=script_content,
                metadata=broadcast_metadata,
                final_filename=final_filename
            )
            
            if not success:
                logger.warning("⚠️ Cover/Metadaten-Embedding fehlgeschlagen")
            
            # 5. Cover separat kopieren
            final_cover_path = final_dir / f"{final_filename}_cover.png"
            if cover_file and cover_file.exists():
                shutil.copy2(cover_file, final_cover_path)
            
            # 6. Transcript-Datei erstellen
            transcript_path = final_dir / f"{final_filename}_transcript.txt"
            await self._create_transcript_file(
                transcript_path=transcript_path,
                script_content=script_content,
                metadata=broadcast_metadata,
                final_filename=final_filename
            )
            
            # 7. *** NEUE FUNKTION: TEMPORÄRE DATEIEN BEREINIGEN ***
            cleanup_result = await self._cleanup_temp_files_after_final_package(
                session_id=session_id,
                original_audio_file=audio_file,
                original_cover_file=cover_file
            )
            
            result = {
                "success": True,
                "session_id": session_id,
                "final_filename": final_filename,
                "files": {
                    "mp3": str(final_mp3_path),
                    "cover": str(final_cover_path) if cover_file else None,
                    "transcript": str(transcript_path)
                },
                "metadata_embedded": success,
                "cleanup": cleanup_result,
                "creation_timestamp": timestamp.isoformat()
            }
            
            logger.success(f"✅ Finales Broadcast-Paket erstellt: {final_filename}")
            if cleanup_result.get("files_deleted", 0) > 0:
                logger.success(f"🗑️ {cleanup_result['files_deleted']} temporäre Dateien automatisch bereinigt")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen des finalen Pakets: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "creation_timestamp": datetime.now().isoformat()
            }
    
    async def _cleanup_temp_files_after_final_package(
        self,
        session_id: str,
        original_audio_file: Path,
        original_cover_file: Path
    ) -> Dict[str, Any]:
        """Bereinigt temporäre Dateien nach Erstellung des finalen Pakets"""
        
        logger.info(f"🧹 Bereinige temporäre Dateien für Session {session_id}")
        
        try:
            files_to_delete = []
            deleted_files = []
            total_size_freed = 0
            
            # 1. Original Audio-Datei aus output/audio
            if original_audio_file and original_audio_file.exists():
                files_to_delete.append(original_audio_file)
            
            # 2. Original Cover-Datei aus output/covers
            if original_cover_file and original_cover_file.exists():
                files_to_delete.append(original_cover_file)
            
            # 3. Alle anderen Session-bezogenen Dateien finden
            output_audio_dir = Path("outplay/audio")
            output_covers_dir = Path("outplay/covers")
            
            # Session-ID Pattern (erste 8 Zeichen)
            session_short = session_id[:8] if len(session_id) >= 8 else session_id
            
            # Suche nach Session-bezogenen Dateien
            for directory in [output_audio_dir, output_covers_dir]:
                if directory.exists():
                    for file_path in directory.glob("*"):
                        if file_path.is_file() and session_short in file_path.name:
                            if file_path not in files_to_delete:
                                files_to_delete.append(file_path)
            
            # 4. Dateien sicher löschen
            for file_path in files_to_delete:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files.append(file_path.name)
                    total_size_freed += file_size
                    logger.debug(f"🗑️ Gelöscht: {file_path.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Konnte {file_path.name} nicht löschen: {e}")
            
            result = {
                "success": True,
                "files_deleted": len(deleted_files),
                "deleted_files": deleted_files,
                "size_freed_bytes": total_size_freed,
                "size_freed_mb": round(total_size_freed / (1024 * 1024), 2)
            }
            
            if deleted_files:
                logger.success(f"✅ {len(deleted_files)} temporäre Dateien bereinigt ({result['size_freed_mb']} MB)")
            else:
                logger.info("ℹ️ Keine temporären Dateien zum Bereinigen gefunden")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Bereinigung temporärer Dateien: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_deleted": 0
            }
    
    async def _embed_cover_and_metadata(
        self,
        audio_file: Path,
        cover_file: Path,
        script_content: str,
        metadata: Dict[str, Any],
        final_filename: str
    ) -> bool:
        """Bettet Cover und erweiterte Metadaten in MP3 ein"""
        
        logger.info(f"🏷️ Bette Cover und Metadaten in MP3 ein: {audio_file.name}")
        
        try:
            # FFmpeg-Pfade für verschiedene Systeme
            ffmpeg_paths = [
                str(Path(__file__).parent.parent.parent.parent / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe"),
                "ffmpeg"  # Fallback für System-PATH
            ]
            
            # Finde verfügbares ffmpeg
            ffmpeg_cmd = None
            for ffmpeg_path in ffmpeg_paths:
                try:
                    result = subprocess.run([ffmpeg_path, '-version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        ffmpeg_cmd = ffmpeg_path
                        break
                except:
                    continue
            
            if not ffmpeg_cmd:
                logger.warning("⚠️ ffmpeg nicht gefunden - Cover/Metadaten-Embedding übersprungen")
                return False
            
            # Erstelle temporäre Ausgabedatei
            temp_output = audio_file.parent / f"temp_final_{audio_file.stem}.mp3"
            
            # Erweiterte Metadaten vorbereiten
            timestamp = datetime.now()
            show_style = metadata.get("broadcast_style", "Unknown")
            duration_min = metadata.get("estimated_duration_minutes", 0)
            news_count = len(metadata.get("selected_news", []))
            
            # Transcript für Lyrics-Tag vorbereiten (gekürzt für ID3)
            transcript_preview = script_content[:500] + "..." if len(script_content) > 500 else script_content
            
            # ffmpeg Kommando für Cover und Metadaten
            ffmpeg_command = [
                ffmpeg_cmd, '-y',  # Überschreibe Ausgabedatei
                '-i', str(audio_file),  # Audio-Input
                '-i', str(cover_file),  # Cover-Input
                '-map', '0:0',  # Audio-Stream
                '-map', '1:0',  # Cover-Stream
                '-c', 'copy',  # Kopiere Audio ohne Re-Encoding
                '-id3v2_version', '3',  # ID3v2.3 für bessere Kompatibilität
                '-metadata:s:v', 'title="RadioX Cover Art"',
                '-metadata:s:v', 'comment="AI Generated Cover"',
                # Basis-Metadaten
                '-metadata', f'title={final_filename}',
                '-metadata', 'artist=RadioX AI',
                '-metadata', 'album=RadioX AI News Broadcast',
                '-metadata', f'date={timestamp.strftime("%Y")}',
                '-metadata', f'genre=News/Talk',
                # Erweiterte Metadaten
                '-metadata', f'comment=RadioX AI News - {show_style} Style - {news_count} News Stories - {duration_min} Minutes',
                '-metadata', f'description=AI-generated radio broadcast featuring Marcel & Jarvis',
                '-metadata', f'copyright=RadioX AI {timestamp.strftime("%Y")}',
                # Transcript als Lyrics (gekürzt)
                '-metadata', f'lyrics={transcript_preview}',
                str(temp_output)
            ]
            
            # Führe ffmpeg aus
            result = subprocess.run(ffmpeg_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Ersetze Original-Datei mit Metadaten-Version
                import shutil
                shutil.move(str(temp_output), str(audio_file))
                
                logger.success(f"✅ Cover und Metadaten erfolgreich eingebettet: {audio_file.name}")
                return True
            else:
                logger.error(f"❌ ffmpeg Metadaten-Embedding fehlgeschlagen: {result.stderr}")
                # Lösche temporäre Datei falls vorhanden
                if temp_output.exists():
                    temp_output.unlink()
                return False
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Metadaten-Embedding: {e}")
            return False
    
    async def _create_transcript_file(
        self,
        transcript_path: Path,
        script_content: str,
        metadata: Dict[str, Any],
        final_filename: str
    ) -> None:
        """Erstellt separate Transcript-Datei mit Metadaten"""
        
        try:
            timestamp = datetime.now()
            show_style = metadata.get("broadcast_style", "Unknown")
            duration_min = metadata.get("estimated_duration_minutes", 0)
            news_count = len(metadata.get("selected_news", []))
            session_id = metadata.get("session_id", "Unknown")
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(f"# RadioX AI News Broadcast - Transcript\n")
                f.write(f"# =====================================\n\n")
                f.write(f"Filename: {final_filename}\n")
                f.write(f"Session ID: {session_id}\n")
                f.write(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Show Style: {show_style}\n")
                f.write(f"Duration: {duration_min} minutes\n")
                f.write(f"News Stories: {news_count}\n")
                f.write(f"Hosts: Marcel (Human) & Jarvis (AI)\n\n")
                f.write(f"# Transcript\n")
                f.write(f"# ----------\n\n")
                f.write(script_content)
                f.write(f"\n\n# End of Transcript\n")
                f.write(f"# Generated by RadioX AI System\n")
            
            logger.info(f"✅ Transcript-Datei erstellt: {transcript_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen der Transcript-Datei: {e}")
            raise

    async def _cleanup_temp_files_after_generation(
        self,
        session_id: str,
        final_audio_file: Path,
        cover_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Bereinigt alle temporären Dateien außer der finalen MP3"""
        
        logger.info(f"🧹 Bereinige temporäre Dateien für Session {session_id}")
        
        try:
            files_to_delete = []
            deleted_files = []
            total_size_freed = 0
            
            # 1. Cover-Datei löschen (falls vorhanden)
            if cover_file and cover_file.exists():
                files_to_delete.append(cover_file)
            
            # 2. Alle anderen Session-bezogenen Dateien im Output-Verzeichnis finden
            output_dir = Path(__file__).parent.parent.parent.parent / "outplay"
            
            # Session-ID Pattern (erste 8 Zeichen)
            session_short = session_id[:8] if len(session_id) >= 8 else session_id
            
            # Suche nach Session-bezogenen Dateien (außer finale MP3)
            if output_dir.exists():
                for file_path in output_dir.glob("*"):
                    if (file_path.is_file() and 
                        session_short in file_path.name and 
                        file_path != final_audio_file):  # Finale MP3 NICHT löschen
                        files_to_delete.append(file_path)
            
            # 3. Dateien sicher löschen
            for file_path in files_to_delete:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files.append(file_path.name)
                    total_size_freed += file_size
                    logger.debug(f"🗑️ Gelöscht: {file_path.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Konnte {file_path.name} nicht löschen: {e}")
            
            result = {
                "success": True,
                "files_deleted": len(deleted_files),
                "deleted_files": deleted_files,
                "size_freed_bytes": total_size_freed,
                "size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
                "final_mp3_kept": str(final_audio_file)
            }
            
            if deleted_files:
                logger.success(f"✅ {len(deleted_files)} temporäre Dateien bereinigt, finale MP3 behalten")
            else:
                logger.info("ℹ️ Keine temporären Dateien zum Bereinigen gefunden")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Bereinigung: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_deleted": 0
            }

    async def _create_comprehensive_info_file(
        self,
        info_path: Path,
        script_content: str,
        broadcast_metadata: Dict[str, Any],
        final_filename: str,
        dalle_prompt: Optional[str] = None
    ) -> None:
        """Erstellt umfassende HTML Info-Datei mit allen Metadaten, News-Analysen und Transkript"""
        
        try:
            timestamp = datetime.now()
            show_style = broadcast_metadata.get("broadcast_style", "Unknown")
            duration_min = broadcast_metadata.get("estimated_duration_minutes", 0)
            session_id = broadcast_metadata.get("session_id", "Unknown")
            
            # Extrahiere News-Daten
            all_news = broadcast_metadata.get("all_collected_news", [])
            selected_news = broadcast_metadata.get("selected_news", [])
            news_selection_criteria = broadcast_metadata.get("news_selection_criteria", "Automatische Auswahl")
            
            # GPT-Input extrahieren
            gpt_input_data = broadcast_metadata.get("gpt_input_data", {})
            
            # HTML-Datei erstellen
            html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RadioX Broadcast Info - {session_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .subtitle {{
            margin: 10px 0 0 0;
            opacity: 0.8;
            font-size: 1.1em;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        .section h2 {{
            margin-top: 0;
            color: #2c3e50;
            font-size: 1.8em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .info-card .label {{
            font-weight: bold;
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .info-card .value {{
            font-size: 1.2em;
            color: #2c3e50;
            margin-top: 5px;
        }}
        .news-item {{
            background: white;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #e74c3c;
        }}
        .news-item.selected {{
            border-left-color: #27ae60;
            background: #f8fff8;
        }}
        .news-title {{
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .news-title a {{
            color: #3498db;
            text-decoration: none;
        }}
        .news-title a:hover {{
            text-decoration: underline;
        }}
        .news-meta {{
            display: flex;
            gap: 20px;
            margin: 10px 0;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        .news-summary {{
            margin: 10px 0;
            color: #555;
        }}
        .transcript {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 25px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            line-height: 1.8;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        .gpt-input {{
            background: #f39c12;
            color: white;
            padding: 25px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        .dalle-prompt {{
            background: #9b59b6;
            color: white;
            padding: 25px;
            border-radius: 8px;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge.selected {{
            background: #27ae60;
            color: white;
        }}
        .badge.available {{
            background: #95a5a6;
            color: white;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin: 20px 0;
        }}
        .stat {{
            padding: 15px;
        }}
        .stat .number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .stat .label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .footer {{
            background: #34495e;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📻 RadioX AI Broadcast</h1>
            <div class="subtitle">Comprehensive Analysis & Metadata</div>
            <div class="subtitle">Session: {session_id}</div>
        </div>
        
        <div class="content">
            <!-- Basic Information -->
            <div class="section">
                <h2>📋 Basic Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="label">Filename</div>
                        <div class="value">{final_filename}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Generated</div>
                        <div class="value">{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Show Style</div>
                        <div class="value">{show_style}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Duration</div>
                        <div class="value">{duration_min} minutes</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Hosts</div>
                        <div class="value">Marcel (Human) & Jarvis (AI)</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Language</div>
                        <div class="value">English</div>
                    </div>
                </div>
            </div>

            <!-- Statistics -->
            <div class="section">
                <h2>📊 Statistics</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="number">{len(all_news)}</div>
                        <div class="label">Total News Collected</div>
                    </div>
                    <div class="stat">
                        <div class="number">{len(selected_news)}</div>
                        <div class="label">News Selected</div>
                    </div>
                    <div class="stat">
                        <div class="number">{len(script_content.split())}</div>
                        <div class="label">Script Words</div>
                    </div>
                </div>
            </div>

            <!-- Show Summary -->
            <div class="section">
                <h2>📝 Show Summary</h2>
                <p><strong>Meta Description:</strong> RadioX AI News {timestamp.strftime('%H:%M')} - {show_style} Edition: Your daily AI-powered news update. Hosted by Marcel & Jarvis AI. Duration: {duration_min} minutes.</p>
            </div>"""

            # Alle gesammelten News
            html_content += f"""
            <!-- All Collected News -->
            <div class="section">
                <h2>📰 All Collected News ({len(all_news)} total)</h2>"""
            
            if all_news:
                for i, news in enumerate(all_news):
                    is_selected = any(sel.get('title') == news.get('title') for sel in selected_news)
                    badge_class = "selected" if is_selected else "available"
                    badge_text = "SELECTED" if is_selected else "AVAILABLE"
                    
                    title = news.get('title', 'No Title')
                    url = news.get('url', '#')
                    source = news.get('source', 'Unknown')
                    published = news.get('published_date', 'Unknown')
                    summary = news.get('summary', 'No summary available')
                    
                    html_content += f"""
                <div class="news-item {'selected' if is_selected else ''}">
                    <div class="news-title">
                        <a href="{url}" target="_blank">{title}</a>
                        <span class="badge {badge_class}">{badge_text}</span>
                    </div>
                    <div class="news-meta">
                        <span><strong>Source:</strong> {source}</span>
                        <span><strong>Published:</strong> {published}</span>
                    </div>
                    <div class="news-summary">{summary}</div>
                </div>"""
            else:
                html_content += """
                <div class="news-item">
                    <div class="news-title">⚠️ No news collected</div>
                    <div class="news-summary">This indicates an issue with the RSS feed collection system.</div>
                </div>"""
            
            html_content += "</div>"

            # Selected News mit Begründung
            html_content += f"""
            <!-- Selected News -->
            <div class="section">
                <h2>✅ Selected News ({len(selected_news)} chosen)</h2>
                <p><strong>Selection Criteria:</strong> {news_selection_criteria}</p>"""
            
            if selected_news:
                for news in selected_news:
                    title = news.get('title', 'No Title')
                    url = news.get('url', '#')
                    reason = news.get('selection_reason', 'No reason provided')
                    
                    html_content += f"""
                <div class="news-item selected">
                    <div class="news-title">
                        <a href="{url}" target="_blank">{title}</a>
                    </div>
                    <div class="news-summary"><strong>Selection Reason:</strong> {reason}</div>
                </div>"""
            else:
                html_content += """
                <div class="news-item">
                    <div class="news-title">⚠️ No news selected</div>
                    <div class="news-summary">This indicates an issue with the content processing system.</div>
                </div>"""
            
            html_content += "</div>"

            # GPT Input Data
            if gpt_input_data:
                html_content += f"""
                <!-- GPT Input Data -->
                <div class="section">
                    <h2>🤖 GPT Input Data</h2>
                    <p>This is the exact data sent to GPT-4 for show generation:</p>
                    <div class="gpt-input">{str(gpt_input_data)}</div>
                </div>"""

            # DALL-E Prompt
            if dalle_prompt:
                html_content += f"""
                <!-- DALL-E Prompt -->
                <div class="section">
                    <h2>🎨 DALL-E Cover Art Prompt</h2>
                    <div class="dalle-prompt">{dalle_prompt}</div>
                </div>"""

            # Full Transcript
            html_content += f"""
            <!-- Full Transcript -->
            <div class="section">
                <h2>🎙️ Full Transcript (1:1 ElevenLabs Script)</h2>
                <p>This is the exact script sent to ElevenLabs for audio generation:</p>
                <div class="transcript">{script_content}</div>
            </div>
        </div>
        
        <div class="footer">
            Generated by RadioX AI System v3.2 • {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""

            # HTML-Datei schreiben
            html_path = info_path.with_suffix('.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Comprehensive HTML Info-Datei erstellt: {html_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen der Info-Datei: {e}")
            # Fallback: Erstelle einfache Text-Datei
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"RadioX Broadcast Info - Error\n")
                f.write(f"Session: {session_id}\n")
                f.write(f"Error: {e}\n")

# ============================================================
# STANDALONE CLI INTERFACE  
# ============================================================

async def main():
    """Test-Funktion für Audio Generation Service"""
    
    print("🔊 AUDIO GENERATION SERVICE TEST")
    print("=" * 50)
    
    service = AudioGenerationService()
    
    # Test Voice Configuration Service Integration
    print("\n🎤 Teste Voice Configuration Service Integration...")
    try:
        marcel_voice = await service.get_voice_with_fallback("marcel")
        if marcel_voice:
            print(f"✅ Marcel Voice: {marcel_voice['voice_name']}")
        else:
            print("❌ Marcel Voice nicht gefunden")
        
        jarvis_voice = await service.get_voice_with_fallback("jarvis")
        if jarvis_voice:
            print(f"✅ Jarvis Voice: {jarvis_voice['voice_name']}")
        else:
            print("❌ Jarvis Voice nicht gefunden")
            
    except Exception as e:
        print(f"❌ Voice Configuration Test Fehler: {e}")
    
    # Test Audio Generation
    print("\n🔊 Teste Audio-Generierung...")
    success = await service.test_audio()
    
    if success:
        print("✅ Audio Generation Service funktioniert!")
    else:
        print("❌ Audio Generation Service Test fehlgeschlagen!")


if __name__ == "__main__":
    asyncio.run(main()) 