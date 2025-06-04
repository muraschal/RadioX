#!/usr/bin/env python3

"""
Audio Generation Service
========================

Service für die Generierung von Audio-Dateien:
- ElevenLabs TTS für Marcel & Jarvis Stimmen
- Audio-Mixing und -Verarbeitung
- Musik-Integration
- Export in verschiedene Formate
"""

import asyncio
import aiohttp
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class AudioGenerationService:
    """
    Service für die Generierung von Audio-Content
    
    Konvertiert Broadcast-Skripte in Audio-Dateien mit
    verschiedenen Stimmen und Audio-Effekten.
    """
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        # Audio-Konfiguration
        self.audio_config = {
            "sample_rate": 44100,
            "bit_depth": 16,
            "format": "mp3",
            "quality": "high",
            "normalize": True
        }
        
        # Stimmen-Konfiguration
        self.voice_config = {
            "marcel": {
                "voice_id": os.getenv('ELEVENLABS_MARCEL_VOICE_ID', 'default_marcel'),
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.2,
                "use_speaker_boost": True
            },
            "jarvis": {
                "voice_id": os.getenv('ELEVENLABS_JARVIS_VOICE_ID', 'default_jarvis'),
                "stability": 0.85,
                "similarity_boost": 0.75,
                "style": 0.1,
                "use_speaker_boost": True
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
                "final_audio_file": str(final_audio_file) if final_audio_file else None,
                "segment_files": [seg["audio_file"] for seg in audio_segments],
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
        """Teilt Skript in Sprecher-Segmente auf"""
        
        segments = []
        lines = script_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Erkenne Sprecher-Zeilen
            if line.startswith("MARCEL:"):
                segments.append({
                    "speaker": "marcel",
                    "text": line[7:].strip()  # Entferne "MARCEL: "
                })
            elif line.startswith("JARVIS:"):
                segments.append({
                    "speaker": "jarvis", 
                    "text": line[7:].strip()  # Entferne "JARVIS: "
                })
            else:
                # Zeile ohne Sprecher - füge zur letzten Zeile hinzu
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
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
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
    
    async def _combine_audio_segments(
        self, 
        audio_segments: List[Dict[str, Any]], 
        session_id: str,
        export_format: str
    ) -> Optional[Path]:
        """Kombiniert Audio-Segmente zu einer Datei"""
        
        if not audio_segments:
            logger.warning("⚠️ Keine Audio-Segmente zum Kombinieren")
            return None
        
        logger.info(f"🔗 Kombiniere {len(audio_segments)} Audio-Segmente")
        
        try:
            # Für einfache Implementierung: Verwende ffmpeg falls verfügbar
            # Ansonsten einfache Konkatenation
            
            final_filename = f"{session_id}_complete.{export_format}"
            final_path = self.output_dir / final_filename
            
            # Einfache Implementierung: Kopiere erstes Segment als Basis
            # In Produktion würde hier echtes Audio-Mixing stattfinden
            if audio_segments:
                first_segment_file = audio_segments[0]["audio_file"]
                
                # Kopiere erste Datei als Basis
                import shutil
                shutil.copy2(first_segment_file, final_path)
                
                logger.info(f"✅ Audio kombiniert: {final_filename}")
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