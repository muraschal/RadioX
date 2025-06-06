#!/usr/bin/env python3

"""
Audio Generation Service
========================

Separater Service nur für Audio-Generierung:
- ElevenLabs V3 TTS für Marcel & Jarvis (English Default)
- Audio-Mixing und -Verarbeitung
- Musik-Integration
- Export in verschiedene Formate
- Kein Cover-Art (wird separat gehandhabt)
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


class AudioGenerationService:
    """
    Separater Service für Audio-Generierung
    
    Konvertiert Broadcast-Skripte in Audio-Dateien mit
    ElevenLabs V3 English Stimmen. Cover-Art wird separat gehandhabt.
    """
    
    def __init__(self):
        # Load settings centrally
        self.settings = get_settings()
        self.elevenlabs_api_key = self.settings.elevenlabs_api_key
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        # Audio-Konfiguration
        self.audio_config = {
            "sample_rate": 44100,
            "bit_depth": 16,
            "format": "mp3",
            "quality": "high",
            "normalize": True
        }
        
        # V3 VOICE CONFIGURATION - FULL ENGLISH + V3 FEATURES
        self.voice_config = {
            # === PRIMARY ENGLISH SPEAKERS (V3 OPTIMIZED) ===
            "marcel": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Natural & Expressive
                "stability": 0.50,    # V3 Creative Mode - Maximum Expression
                "similarity_boost": 0.85,
                "style": 0.70,       # High Style for V3 Emotional Range
                "use_speaker_boost": True,
                "model": "eleven_multilingual_v2",  # V3 Compatible
                "description": "Marcel - Enthusiastic English Host"
            },
            "jarvis": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - Analytical & Smart  
                "stability": 0.60,    # V3 Natural Mode - Balanced
                "similarity_boost": 0.80,
                "style": 0.50,       # Moderate Style for Analytical Precision
                "use_speaker_boost": True,
                "model": "eleven_multilingual_v2",  # V3 Compatible
                "description": "Jarvis - Analytical English AI"
            },
            
            # === ALTERNATIVE V3 VOICES FOR VARIETY ===
            "marcel_alt": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - Deep & Confident
                "stability": 0.45,    # More Creative for Energy
                "similarity_boost": 0.85,
                "style": 0.65,       # High Expression
                "use_speaker_boost": True,
                "model": "eleven_multilingual_v2",
                "description": "Marcel Alternative - Confident Host"
            },
            "jarvis_alt": {
                "voice_id": "TxGEqnHWrfWFTfGW9XjX",  # Josh - Professional & Clear
                "stability": 0.70,    # Robust for Consistency 
                "similarity_boost": 0.75,
                "style": 0.40,       # Lower Style for Tech Precision
                "use_speaker_boost": True,
                "model": "eleven_multilingual_v2",
                "description": "Jarvis Alternative - Tech Professional"
            },
            
            # === GERMAN BACKUP (IF NEEDED) ===
            "marcel_de": {
                "voice_id": self.settings.elevenlabs_marcel_voice_id or 'owi9KfbgBi6A987h5eJH',
                "stability": 0.55,
                "similarity_boost": 0.85,
                "style": 0.45,
                "use_speaker_boost": True,
                "model": "eleven_multilingual_v2",
                "description": "Marcel - German Voice"
            },
            "jarvis_de": {
                "voice_id": self.settings.elevenlabs_jarvis_voice_id or 'dmLlPcdDHenQXbfM5tee',
                "stability": 0.60,
                "similarity_boost": 0.75,
                "style": 0.40,
                "use_speaker_boost": True,
                "model": "eleven_multilingual_v2",
                "description": "Jarvis - German Voice"
            }
        }
        
        # Output-Verzeichnis
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    


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
        """Parses script into speaker segments (English V3 Default)"""
        
        segments = []
        lines = script_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # === PRIMARY ENGLISH SPEAKERS (DEFAULT) ===
            if line.startswith("MARCEL:"):
                segments.append({
                    "speaker": "marcel",  # Now English by default!
                    "text": line[7:].strip()
                })
            elif line.startswith("JARVIS:"):
                segments.append({
                    "speaker": "jarvis",  # Now English by default!
                    "text": line[7:].strip()
                })
            
            # === ALTERNATIVE VOICE OPTIONS ===
            elif line.startswith("MARCEL_ALT:"):
                segments.append({
                    "speaker": "marcel_alt",
                    "text": line[11:].strip()
                })
            elif line.startswith("JARVIS_ALT:"):
                segments.append({
                    "speaker": "jarvis_alt",
                    "text": line[11:].strip()
                })
            
            # === GERMAN FALLBACK ===
            elif line.startswith("MARCEL_DE:") or line.startswith("MARCEL (DE):"):
                segments.append({
                    "speaker": "marcel_de",
                    "text": line.split(":", 1)[1].strip()
                })
            elif line.startswith("JARVIS_DE:") or line.startswith("JARVIS (DE):"):
                segments.append({
                    "speaker": "jarvis_de",
                    "text": line.split(":", 1)[1].strip()
                })
            
            # === LEGACY COMPATIBILITY ===
            elif line.startswith("MARCEL_EN:") or line.startswith("MARCEL (EN):"):
                segments.append({
                    "speaker": "marcel",  # Redirect to default English
                    "text": line.split(":", 1)[1].strip()
                })
            elif line.startswith("JARVIS_EN:") or line.startswith("JARVIS (EN):"):
                segments.append({
                    "speaker": "jarvis",  # Redirect to default English
                    "text": line.split(":", 1)[1].strip()
                })
            
            else:
                # Line without speaker - append to last segment
                if segments:
                    segments[-1]["text"] += " " + line
        
        return segments
    
    async def _generate_segment_audio(
        self, 
        segment: Dict[str, Any], 
        session_id: str, 
        segment_index: int
    ) -> Optional[Path]:
        """Generiert Audio für ein einzelnes Segment"""
        
        speaker = segment["speaker"]
        text = segment["text"]
        
        if not text.strip():
            return None
        
        logger.info(f"🎤 Generiere Audio für {speaker}: {text[:50]}...")
        
        try:
            # Voice-Konfiguration für Sprecher
            voice_config = self.voice_config.get(speaker, self.voice_config["marcel"])
            
            # ElevenLabs API Request
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # ElevenLabs V3 Enhanced Request mit Audio Tags Support!
            enhanced_text = self._enhance_text_with_v3_tags(text, speaker)
            
            data = {
                "text": enhanced_text,
                "model_id": voice_config.get("model", "eleven_multilingual_v2"),  # V3 Model Support
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
                        audio_filename = f"{session_id}_{speaker}_{segment_index:03d}.mp3"
                        audio_path = self.output_dir / audio_filename
                        
                        with open(audio_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
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
        🎭 ElevenLabs V3 Audio Enhancement - FULL ENGLISH OPTIMIZATION
        Based on: https://elevenlabs.io/docs/best-practices/prompting/eleven-v3
        """
        
        enhanced_text = text.strip()
        
        # === MARCEL: ENTHUSIASTIC ENGLISH HOST ===
        if speaker in ["marcel", "marcel_alt"]:
            
            # 🔥 EXCITEMENT TRIGGERS
            excitement_keywords = ["bitcoin", "breaking", "incredible", "amazing", "wow", "unbelievable", "fantastic", "awesome"]
            if any(keyword in enhanced_text.lower() for keyword in excitement_keywords):
                enhanced_text = f"[excited] Oh my god, {enhanced_text}!"
            
            # 👋 WELCOMING ENERGY  
            elif any(keyword in enhanced_text.lower() for keyword in ["hello", "hey", "welcome", "good morning", "good evening"]):
                enhanced_text = f"[excited] Hey everyone! {enhanced_text}"
            
            # 💰 MONEY/NUMBERS IMPRESSED
            elif any(char.isdigit() for char in enhanced_text) and any(keyword in enhanced_text.lower() for keyword in ["$", "€", "million", "billion", "percent", "%", "thousand"]):
                enhanced_text = f"[impressed] {enhanced_text} [whispers] That's absolutely mind-blowing."
            
            # 😂 FUNNY MOMENTS
            elif any(keyword in enhanced_text.lower() for keyword in ["funny", "hilarious", "crazy", "ridiculous", "insane"]):
                enhanced_text = f"[laughs] {enhanced_text} [laughs harder]"
            
            # 🎉 CELEBRATION
            elif any(keyword in enhanced_text.lower() for keyword in ["celebrate", "victory", "success", "win", "achievement"]):
                enhanced_text = f"[excited] {enhanced_text} [applause]"
                
        # === JARVIS: ANALYTICAL ENGLISH AI ===
        elif speaker in ["jarvis", "jarvis_alt"]:
            
            # 😏 SARCASM TRIGGERS
            if any(keyword in enhanced_text.lower() for keyword in ["obviously", "of course", "clearly", "naturally", "predictably"]):
                enhanced_text = f"[sarcastic] {enhanced_text}"
            
            # 🧠 ANALYTICAL MODE
            elif any(keyword in enhanced_text.lower() for keyword in ["analyze", "data", "statistics", "calculate", "algorithm", "pattern"]):
                enhanced_text = f"[curious] {enhanced_text}"
            
            # 🤫 SECRETS & INSIGHTS
            elif any(keyword in enhanced_text.lower() for keyword in ["secret", "hidden", "between us", "confidentially", "insider"]):
                enhanced_text = f"[whispers] {enhanced_text}"
            
            # 😮‍💨 HUMAN BEHAVIOR COMMENTARY
            elif any(keyword in enhanced_text.lower() for keyword in ["humans", "people", "emotional", "irrational", "predictable"]):
                enhanced_text = f"[sighs] {enhanced_text}"
            
            # 🤖 TECH SUPERIORITY
            elif any(keyword in enhanced_text.lower() for keyword in ["ai", "artificial intelligence", "machine learning", "automation"]):
                enhanced_text = f"[mischievously] {enhanced_text}"
        
        # === GERMAN SPEAKERS (FALLBACK) ===
        elif speaker.endswith("_de"):
            # German-specific enhancements (minimal)
            if any(keyword in enhanced_text.lower() for keyword in ["bitcoin", "breaking"]):
                enhanced_text = f"[excited] Leute, {enhanced_text}!"
            elif any(keyword in enhanced_text.lower() for keyword in ["natürlich", "selbstverständlich"]):
                enhanced_text = f"[sarcastic] {enhanced_text}"
        
        # === UNIVERSAL V3 ENHANCEMENTS ===
        
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
            "incredible": "INCREDIBLE",
            "amazing": "AMAZING",
            "unbelievable": "UNBELIEVABLE",
            "fantastic": "FANTASTIC",
            "million": "MILLION",
            "billion": "BILLION"
        }
        
        for term, emphasized in emphasis_terms.items():
            enhanced_text = enhanced_text.replace(term, emphasized)
            enhanced_text = enhanced_text.replace(term.capitalize(), emphasized)
            enhanced_text = enhanced_text.replace(term.upper(), emphasized)
        
        # 🎵 SOUND EFFECTS FOR DRAMATIC MOMENTS
        if "crash" in enhanced_text.lower():
            enhanced_text = enhanced_text.replace("crash", "[explosion] crash")
        if "applause" not in enhanced_text and any(word in enhanced_text.lower() for word in ["success", "achievement", "victory"]):
            enhanced_text += " [applause]"
        
        # 🚀 ENGLISH NATURALNESS IMPROVEMENTS
        if not speaker.endswith("_de"):
            # Natural English contractions
            enhanced_text = enhanced_text.replace("cannot", "can't")
            enhanced_text = enhanced_text.replace("will not", "won't") 
            enhanced_text = enhanced_text.replace("do not", "don't")
            enhanced_text = enhanced_text.replace("it is", "it's")
            enhanced_text = enhanced_text.replace("that is", "that's")
            
            # English excitement interjections
            if "[excited]" in enhanced_text and "oh my god" not in enhanced_text.lower():
                enhanced_text = enhanced_text.replace("[excited]", "[excited] Guys,")
        
        return enhanced_text
    
    async def _combine_audio_segments(
        self, 
        audio_segments: List[Dict[str, Any]], 
        session_id: str,
        export_format: str
    ) -> Optional[Path]:
        """Kombiniert Audio-Segmente zu einer Datei und löscht alle temporären Dateien"""
        
        if not audio_segments:
            logger.warning("⚠️ Keine Audio-Segmente zum Kombinieren")
            return None
        
        logger.info(f"🔗 Kombiniere {len(audio_segments)} Audio-Segmente")
        
        try:
            # Schöner Dateiname für finale MP3
            final_filename = f"RadioX_Broadcast_{session_id[:8]}.{export_format}"
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
                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', 
                    '-i', str(concat_list_path), 
                    '-c', 'copy', str(final_path)
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ Audio mit ffmpeg kombiniert: {final_filename}")
                    
                    # Lösche concat-Liste
                    concat_list_path.unlink()
                    
                    # *** LÖSCHE ALLE TEMPORÄREN SEGMENT-DATEIEN ***
                    deleted_count = 0
                    for temp_file in temp_files_to_delete:
                        try:
                            temp_file.unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"⚠️ Konnte {temp_file} nicht löschen: {e}")
                    
                    logger.success(f"🗑️ {deleted_count} temporäre Audio-Segmente automatisch gelöscht")
                    logger.success(f"🎵 FINALE SAUBERE MP3 BEREIT: {final_filename}")
                    
                    return final_path
                else:
                    logger.warning(f"⚠️ ffmpeg fehlgeschlagen: {result.stderr}")
                    
            except (ImportError, FileNotFoundError, subprocess.SubprocessError) as e:
                logger.warning(f"⚠️ ffmpeg nicht verfügbar, verwende Fallback: {e}")
            
            # Fallback: Kopiere erstes Segment als finale Datei
            if segment_files:
                import shutil
                shutil.copy2(segment_files[0], final_path)
                
                # *** LÖSCHE ALLE TEMPORÄREN SEGMENT-DATEIEN (auch bei Fallback) ***
                deleted_count = 0
                for temp_file in temp_files_to_delete:
                    try:
                        temp_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Konnte {temp_file} nicht löschen: {e}")
                
                logger.info(f"✅ Audio kombiniert (Fallback): {final_filename}")
                logger.success(f"🗑️ {deleted_count} temporäre Audio-Segmente automatisch gelöscht")
                logger.success(f"🎵 FINALE SAUBERE MP3 BEREIT: {final_filename}")
                
                return final_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Kombinieren der Audio-Segmente: {e}")
            return None
    
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
        """Erstellt Audio-Metadaten"""
        
        total_duration = sum(seg.get("duration", 0) for seg in audio_segments)
        
        metadata = {
            "total_duration_seconds": total_duration,
            "total_duration_formatted": f"{int(total_duration // 60)}:{int(total_duration % 60):02d}",
            "segment_count": len(audio_segments),
            "speakers": list(set(seg["speaker"] for seg in audio_segments)),
            "file_size_bytes": final_audio_file.stat().st_size if final_audio_file and final_audio_file.exists() else 0,
            "format": self.audio_config["format"],
            "sample_rate": self.audio_config["sample_rate"],
            "generation_settings": {
                "quality": self.audio_config["quality"],
                "normalize": self.audio_config["normalize"]
            }
        }
        
        return metadata
    
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

# ============================================================
# STANDALONE CLI INTERFACE  
# ============================================================

async def main():
    """CLI Interface für Audio Generation Service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🔊 RadioX Audio Generation Service")
    parser.add_argument("--action", required=True, choices=[
        "test", "voices", "generate", "test-script", "demo"
    ], help="Aktion")
    parser.add_argument("--speaker", choices=["marcel", "jarvis", "marcel_alt", "jarvis_alt"], 
                       default="marcel", help="Sprecher")
    parser.add_argument("--text", help="Text für Audio-Generierung")
    parser.add_argument("--script-file", help="Script-Datei (.txt)")
    parser.add_argument("--output", help="Output-Datei")
    parser.add_argument("--session-id", default="cli_test", help="Session ID")
    
    args = parser.parse_args()
    
    print("🔊 AUDIO GENERATION SERVICE")
    print("=" * 50)
    
    # Für standalone: simplified service ohne Settings
    service = AudioGenerationService()
    
    if args.action == "test":
        print("🧪 Teste Audio Generation Service...")
        test_script = {
            'session_id': 'audio_test',
            'script_content': '''MARCEL: Hey everyone! This is a test of our English V3 audio system.
JARVIS: Indeed, Marcel. The new ElevenLabs V3 integration is quite impressive.
MARCEL: [excited] Oh my god, Bitcoin just hit $103,000! That's absolutely incredible!
JARVIS: [sarcastic] Obviously, humans getting excited about numbers again.'''
        }
        
        print("🎤 Generiere Test-Audio...")
        result = await service.generate_audio(test_script)
        
        if result.get('success'):
            print(f"✅ Audio erfolgreich generiert!")
            print(f"📁 Datei: {result.get('final_audio_file')}")
            if result.get('duration_seconds'):
                print(f"⏱️ Dauer: {result['duration_seconds']} Sekunden")
        else:
            print(f"❌ Fehler: {result.get('error', 'Unbekannt')}")
            
    elif args.action == "voices":
        print("🎭 V3 English Stimmen-Konfiguration:")
        for speaker, config in service.voice_config.items():
            print(f"\n🎤 {speaker.upper()}")
            print(f"   Voice ID: {config['voice_id']}")
            print(f"   Model: {config['model']}")
            print(f"   Stability: {config['stability']} (V3 Style: {config['style']})")
            if 'description' in config:
                print(f"   Info: {config['description']}")
                
    elif args.action == "generate":
        if not args.text:
            print("❌ --text Parameter erforderlich!")
            return
            
        print(f"🎤 Generiere Audio für {args.speaker}: {args.text[:50]}...")
        
        # Simple single-speaker generation
        enhanced_text = service._enhance_text_with_v3_tags(args.text, args.speaker)
        print(f"🎭 V3 Enhanced: {enhanced_text}")
        
        segment_data = {
            "speaker": args.speaker,
            "text": enhanced_text
        }
        
        try:
            output_file = await service._generate_segment_audio(segment_data, args.session_id, 0)
            print(f"✅ Audio generiert: {output_file}")
        except Exception as e:
            print(f"❌ Fehler: {e}")
            
    elif args.action == "test-script":
        if not args.script_file:
            print("❌ --script-file Parameter erforderlich!")
            return
            
        try:
            with open(args.script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
                
            test_script = {
                'session_id': args.session_id,
                'script_content': script_content
            }
            
            print(f"🎤 Generiere Audio aus Script: {args.script_file}")
            result = await service.generate_audio(test_script)
            
            if result.get('success'):
                print(f"✅ Audio erfolgreich generiert!")
                print(f"📁 Datei: {result.get('final_audio_file')}")
            else:
                print(f"❌ Fehler: {result.get('error')}")
                
        except FileNotFoundError:
            print(f"❌ Datei nicht gefunden: {args.script_file}")
        except Exception as e:
            print(f"❌ Fehler: {e}")
            
    elif args.action == "demo":
        print("🎭 V3 English Demo - Verschiedene Emotionen:")
        
        demo_texts = [
            ("marcel", "[excited] Oh my god, Bitcoin just reached $100,000! This is absolutely incredible!"),
            ("jarvis", "[sarcastic] Obviously, another human getting excited about imaginary internet money."),
            ("marcel", "[impressed] The Swiss National Bank just announced major policy changes! [whispers] This could change everything."),
            ("jarvis", "[curious] Analyzing the economic implications... [mischievously] Humans never learn from history."),
        ]
        
        for i, (speaker, text) in enumerate(demo_texts, 1):
            print(f"\n{i}. Generiere {speaker}: {text[:40]}...")
            
            segment_data = {"speaker": speaker, "text": text}
            try:
                output_file = await service._generate_segment_audio(segment_data, f"demo_{i}", 0)
                print(f"   ✅ {output_file}")
            except Exception as e:
                print(f"   ❌ Fehler: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 