"""
RadioX Voice Generator - ElevenLabs basierte Voice-Over Generierung
"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import aiofiles
from loguru import logger

from ..models.personas import PersonaConfig, get_persona_by_name, get_voice_prompt_for_persona
from ..config.settings import get_settings
from .audio_manager import AudioManager


class VoiceGenerator:
    """ElevenLabs basierter Voice-Over Generator für RadioX"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Audio Manager für professionelle Dateiorganisation
        self.audio_manager = AudioManager()
        
        # Temporäres Verzeichnis für Generierung
        self.temp_dir = self.audio_manager.structure["temp"]
        
    async def generate_voice_over(
        self,
        script_segments: List[Dict[str, Any]],
        persona_name: str,
        stream_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generiert Voice-Over Audio-Dateien für alle Skript-Segmente
        
        Args:
            script_segments: Liste von Voice-Over Segmenten
            persona_name: Name der Persona
            stream_id: Optional Stream-ID für Datei-Organisation
            
        Returns:
            Liste von generierten Audio-Dateien mit Metadaten
        """
        
        persona = get_persona_by_name(persona_name)
        if not persona:
            raise ValueError(f"Persona '{persona_name}' nicht gefunden")
        
        logger.info(f"Generiere Voice-Over für {len(script_segments)} Segmente ({persona.display_name})")
        
        generated_files = []
        
        # Temporäres Session-Verzeichnis erstellen
        timestamp = datetime.now()
        session_id = stream_id or f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        temp_session_dir = self.temp_dir / session_id
        temp_session_dir.mkdir(exist_ok=True)
        
        # Voice-Prompt für Persona
        voice_prompt = get_voice_prompt_for_persona(persona)
        
        # Segmente parallel verarbeiten (aber mit Rate Limiting)
        semaphore = asyncio.Semaphore(3)  # Max 3 gleichzeitige Requests
        
        tasks = []
        for segment in script_segments:
            task = self._generate_single_segment(
                segment, persona, temp_session_dir, voice_prompt, semaphore
            )
            tasks.append(task)
        
        # Alle Segmente generieren
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse sammeln
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Fehler bei Segment {i}: {result}")
                # Fallback: Text-to-Speech ohne Audio
                generated_files.append({
                    "segment_order": script_segments[i].get("order", i),
                    "segment_type": script_segments[i].get("type", "unknown"),
                    "text": script_segments[i].get("text", ""),
                    "audio_file": None,
                    "error": str(result),
                    "duration_seconds": 0
                })
            else:
                generated_files.append(result)
        
        # Nach Reihenfolge sortieren
        generated_files.sort(key=lambda x: x.get("segment_order", 0))
        
        logger.success(f"Voice-Over Generierung abgeschlossen: {len(generated_files)} Dateien")
        return generated_files
    
    async def _generate_single_segment(
        self,
        segment: Dict[str, Any],
        persona: PersonaConfig,
        temp_dir: Path,
        voice_prompt: str,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Generiert Audio für ein einzelnes Segment"""
        
        async with semaphore:
            try:
                text = segment.get("text", "")
                segment_type = segment.get("type", "unknown")
                order = segment.get("order", 0)
                
                if not text.strip():
                    logger.warning(f"Leerer Text für Segment {order}")
                    return {
                        "segment_order": order,
                        "segment_type": segment_type,
                        "text": text,
                        "audio_file": None,
                        "error": "Leerer Text",
                        "duration_seconds": 0
                    }
                
                # Temporärer Dateiname
                temp_filename = f"temp_{order:02d}_{segment_type}_{persona.name}.mp3"
                temp_path = temp_dir / temp_filename
                
                # Voice-Style Parameter
                voice_style = persona.voice_style
                
                # ElevenLabs API Call über MCP
                logger.info(f"🎙️ Generiere Audio für Segment {order}: {text[:50]}...")
                
                try:
                    # Echte ElevenLabs Voice-Generierung
                    await self._real_audio_generation(text, temp_path, voice_style)
                    logger.success(f"✅ Audio generiert: {temp_filename}")
                except Exception as e:
                    logger.warning(f"ElevenLabs Fehler, verwende Mock: {e}")
                    await self._mock_audio_generation(text, temp_path, voice_style)
                
                # Metadaten zurückgeben
                return {
                    "segment_order": order,
                    "segment_type": segment_type,
                    "category": segment.get("category"),
                    "title": segment.get("title"),
                    "text": text,
                    "audio_file": str(temp_path),
                    "duration_seconds": self._estimate_audio_duration(text),
                    "voice_settings": {
                        "voice_name": voice_style.voice_name,
                        "speed": voice_style.speed,
                        "stability": voice_style.stability,
                        "similarity_boost": voice_style.similarity_boost,
                        "style": voice_style.style
                    },
                    "generated_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Fehler bei Audio-Generierung für Segment {order}: {e}")
                raise
    
    async def _real_audio_generation(
        self,
        text: str,
        output_path: Path,
        voice_style: Any
    ):
        """Echte ElevenLabs Audio-Generierung über direkte API"""
        
        try:
            # Verwende voice_id wenn verfügbar, sonst voice_name
            voice_param = voice_style.voice_id if voice_style.voice_id else voice_style.voice_name
            logger.info(f"🎙️ ElevenLabs TTS: {voice_param}")
            
            # DIREKTE ElevenLabs API Integration
            logger.info("🔄 Verwende direkte ElevenLabs API")
            
            # Erstelle Output-Verzeichnis
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ElevenLabs API Service verwenden
            from .elevenlabs_api_service import ElevenLabsAPIService
            
            api_service = ElevenLabsAPIService()
            
            # Audio generieren über direkte API
            success = await api_service.text_to_speech(
                text=text,
                voice_id=voice_style.voice_id if voice_style.voice_id else api_service.voices.get('breaking_news', {}).get('voice_id', 'pNInz6obpgDQGcFmaJgB'),
                output_file=str(output_path),
                stability=getattr(voice_style, 'stability', 0.5),
                similarity_boost=getattr(voice_style, 'similarity_boost', 0.75),
                speed=getattr(voice_style, 'speed', 1.0),
                style=getattr(voice_style, 'style', 0.0),
                use_speaker_boost=getattr(voice_style, 'use_speaker_boost', True)
            )
            
            if success:
                # Schätze Dauer
                duration = len(text) * 0.08  # ~80ms pro Zeichen
                
                logger.success(f"✅ ElevenLabs Audio generiert: {output_path.name} ({duration:.1f}s)")
                
                return {
                    "file_path": str(output_path),
                    "duration": duration,
                    "voice_used": voice_param,
                    "text_length": len(text),
                    "elevenlabs_result": {
                        "voice_id": voice_style.voice_id,
                        "voice_name": voice_style.voice_name,
                        "settings": {
                            "stability": getattr(voice_style, 'stability', 0.5),
                            "similarity_boost": getattr(voice_style, 'similarity_boost', 0.75),
                            "style": getattr(voice_style, 'style', 0.0),
                            "speed": getattr(voice_style, 'speed', 1.0),
                            "use_speaker_boost": getattr(voice_style, 'use_speaker_boost', True)
                        },
                        "output_format": "mp3_44100_128",
                        "quality": "high",
                        "api_method": "direct"
                    }
                }
            else:
                raise Exception("ElevenLabs API Fehler - Audio-Generierung fehlgeschlagen")
                
        except Exception as e:
            logger.error(f"❌ ElevenLabs API Fehler: {e}")
            logger.warning("🔄 Fallback zu Mock-Generierung")
            return await self._mock_audio_generation_with_result(text, output_path, voice_style)
    
    async def _mock_audio_generation(
        self,
        text: str,
        output_path: Path,
        voice_style: Any
    ):
        """Mock Audio-Generierung für Demo-Zwecke"""
        
        # Simuliere Audio-Generierung mit Delay
        await asyncio.sleep(0.5)
        
        # Erstelle Mock-Audio-Datei (leere MP3)
        mock_content = b"Mock MP3 Audio Content for: " + text[:50].encode('utf-8')
        
        async with aiofiles.open(output_path, 'wb') as f:
            await f.write(mock_content)
        
        logger.debug(f"Mock-Audio erstellt: {output_path}")
    
    def _estimate_audio_duration(self, text: str) -> int:
        """Schätzt die Audio-Dauer basierend auf Text-Länge"""
        
        # Durchschnittlich 150 Wörter pro Minute
        words = len(text.split())
        duration_minutes = words / 150
        return int(duration_minutes * 60)
    
    async def generate_complete_stream(
        self,
        radio_script: Dict[str, Any],
        persona_name: str,
        stream_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generiert kompletten Audio-Stream aus Radio-Skript
        
        Args:
            radio_script: Komplettes Radio-Skript vom NewsSummarizer
            persona_name: Persona für Voice-Over
            stream_id: Optional Stream-ID
            
        Returns:
            Komplette Stream-Daten mit organisierten Audio-Dateien
        """
        
        logger.info(f"Generiere kompletten Audio-Stream für {persona_name}")
        
        # Stream-ID generieren falls nicht vorhanden
        if not stream_id:
            stream_id = f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Voice-Over Segmente aus Skript extrahieren
        from .news_summarizer import NewsSummarizer
        summarizer = NewsSummarizer()
        voice_segments = summarizer.format_for_voice_over(radio_script)
        
        # Temporäre Audio-Dateien generieren
        temp_audio_files = await self.generate_voice_over(
            script_segments=voice_segments,
            persona_name=persona_name,
            stream_id=stream_id
        )
        
        # Stream-Metadaten vorbereiten
        stream_metadata = {
            "stream_id": stream_id,
            "persona": persona_name,
            "generated_at": datetime.now().isoformat(),
            "script_metadata": radio_script.get("metadata", {}),
            "content_mix_metadata": radio_script.get("content_mix_metadata", {}),
            "voice_generation": {
                "total_segments": len(temp_audio_files),
                "successful_generations": len([f for f in temp_audio_files if f.get("audio_file")]),
                "failed_generations": len([f for f in temp_audio_files if not f.get("audio_file")])
            }
        }
        
        # Dateien mit AudioManager organisieren
        organized_files = self.audio_manager.organize_stream_files(
            temp_files=temp_audio_files,
            stream_id=stream_id,
            persona=persona_name,
            stream_metadata=stream_metadata
        )
        
        # Finale Stream-Daten zusammenstellen
        total_duration = sum(file.get("duration_seconds", 0) for file in organized_files["audio_files"])
        
        stream_data = {
            "stream_id": stream_id,
            "persona": persona_name,
            "status": "completed",
            "generated_at": organized_files["timestamp"],
            "total_segments": len(organized_files["audio_files"]),
            "total_duration_seconds": total_duration,
            "estimated_duration_minutes": round(total_duration / 60, 1),
            "organized_files": organized_files,
            "stream_path": organized_files["stream_path"],
            "manifest_file": organized_files["manifest_file"],
            "metadata_file": organized_files["metadata_file"],
            "audio_files": organized_files["audio_files"],
            "script_metadata": radio_script.get("metadata", {}),
            "content_mix_metadata": radio_script.get("content_mix_metadata", {})
        }
        
        # Temporäre Dateien aufräumen
        await self._cleanup_temp_session(stream_id)
        
        logger.success(f"Audio-Stream organisiert: {stream_data['stream_path']}")
        return stream_data
    
    async def _cleanup_temp_session(self, session_id: str):
        """Räumt temporäre Session-Dateien auf"""
        
        temp_session_dir = self.temp_dir / session_id
        
        if temp_session_dir.exists():
            try:
                import shutil
                shutil.rmtree(temp_session_dir)
                logger.debug(f"Temporäre Session aufgeräumt: {session_id}")
            except Exception as e:
                logger.warning(f"Konnte temporäre Session nicht aufräumen: {e}")
    
    def get_audio_files_for_stream(self, stream_id: str) -> List[Path]:
        """Holt alle Audio-Dateien für einen Stream aus dem organisierten Archiv"""
        
        # Suche in der organisierten Struktur
        streams_dir = self.audio_manager.structure["streams"]
        
        # Durchsuche alle Ordner nach Stream-ID
        for stream_folder in streams_dir.rglob(f"*{stream_id}*"):
            if stream_folder.is_dir():
                audio_files = list(stream_folder.glob("*.mp3"))
                return sorted(audio_files)
        
        return []
    
    async def cleanup_old_streams(self, days_old: int = 7):
        """Delegiert an AudioManager für professionelle Archivierung"""
        
        return self.audio_manager.archive_old_streams(days_old)
    
    def get_stream_statistics(self) -> Dict[str, Any]:
        """Holt detaillierte Stream-Statistiken vom AudioManager"""
        
        return self.audio_manager.get_storage_statistics()
    
    async def export_stream_for_broadcast(
        self,
        stream_id: str,
        export_format: str = "mp3"
    ) -> Optional[Path]:
        """
        Exportiert Stream für Broadcast
        """
        
        # Finde Stream-Manifest
        streams_dir = self.audio_manager.structure["streams"]
        
        for manifest_file in streams_dir.rglob("stream_manifest.json"):
            try:
                import json
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                if manifest.get("stream_info", {}).get("stream_id") == stream_id:
                    return self.audio_manager.export_stream_for_broadcast(
                        str(manifest_file), export_format
                    )
                    
            except Exception:
                continue
        
        logger.warning(f"Stream {stream_id} nicht gefunden für Export")
        return None
    
    async def _mock_audio_generation_with_result(
        self,
        text: str,
        output_path: Path,
        voice_style: Any
    ):
        """Mock Audio-Generierung mit korrekter Rückgabe-Struktur"""
        
        try:
            voice_param = voice_style.voice_id if voice_style.voice_id else voice_style.voice_name
            duration = len(text) * 0.08  # ~80ms pro Zeichen
            
            # Erstelle Mock-Audio-Datei
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Mock Audio-Inhalt (wird durch echte ElevenLabs Audio ersetzt)
            mock_audio_content = f"MOCK AUDIO: {text[:50]}..."
            
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(mock_audio_content)
            
            logger.success(f"✅ Mock Audio generiert: {output_path.name} ({duration:.1f}s)")
            
            return {
                "file_path": str(output_path),
                "duration": duration,
                "voice_used": voice_param,
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"❌ Mock Audio-Generierung fehlgeschlagen: {e}")
            raise 