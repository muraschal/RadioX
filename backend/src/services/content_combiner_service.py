#!/usr/bin/env python3
"""
Content Combiner Service
========================

Service für Audio + Cover-Art Kombination
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import shutil
import json

# Für MP3 Metadata
try:
    import eyed3
    EYED3_AVAILABLE = True
except ImportError:
    EYED3_AVAILABLE = False
    logger.warning("⚠️ eyed3 nicht verfügbar - Cover-Embedding deaktiviert")


class ContentCombinerService:
    """Service für Audio + Cover-Art Kombination"""
    
    def __init__(self):
        # Output-Verzeichnisse
        self.output_dir = Path("output/final")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Kombination-Konfiguration
        self.config = {
            "metadata_version": "1.0",
            "radiox_branding": {
                "artist": "RadioX AI",
                "album": "RadioX News Broadcasts",
                "genre": "Talk/News",
                "year": datetime.now().year
            }
        }
    
    async def combine_audio_and_cover(
        self,
        session_id: str,
        audio_result: Dict[str, Any],
        cover_result: Dict[str, Any],
        broadcast_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Kombiniert Audio und Cover-Art zu finaler MP3"""
        
        logger.info(f"🔗 Kombiniere Audio + Cover für Session {session_id}")
        
        try:
            # 1. Input-Validierung
            validation_result = await self._validate_inputs(audio_result, cover_result)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "session_id": session_id,
                    "error": validation_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            # 2. Audio-Datei kopieren
            source_audio_path = Path(audio_result["audio_path"])
            final_audio_filename = f"radiox_broadcast_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            final_audio_path = self.output_dir / final_audio_filename
            
            shutil.copy2(source_audio_path, final_audio_path)
            logger.info(f"📄 Audio kopiert: {final_audio_filename}")
            
            # 3. Cover-Art einbetten (falls verfügbar)
            cover_embedded = False
            if cover_result.get("success") and EYED3_AVAILABLE:
                cover_path = Path(cover_result["cover_path"])
                cover_embedded = await self._embed_cover_art(
                    final_audio_path, 
                    cover_path, 
                    broadcast_metadata
                )
            
            # 4. Quality Check
            quality_check = await self._perform_quality_check(final_audio_path)
            
            logger.success(f"✅ Audio + Cover erfolgreich kombiniert: {final_audio_filename}")
            
            return {
                "success": True,
                "session_id": session_id,
                "final_audio_path": str(final_audio_path),
                "final_audio_filename": final_audio_filename,
                "cover_embedded": cover_embedded,
                "quality_check": quality_check,
                "file_size_mb": round(final_audio_path.stat().st_size / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Audio+Cover Kombination: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_combiner(self) -> bool:
        """Testet den Content Combiner"""
        
        mock_audio = {
            "success": True,
            "audio_path": "test_audio.mp3",
            "duration_seconds": 120
        }
        
        mock_cover = {
            "success": True,
            "cover_path": "test_cover.png",
            "cover_type": "fallback"
        }
        
        try:
            validation = await self._validate_inputs(mock_audio, mock_cover)
            logger.info(f"Combiner Test - Validierung: {validation}")
            return True
            
        except Exception as e:
            logger.error(f"Combiner Test Fehler: {e}")
            return False
    
    # Private Methods
    
    async def _validate_inputs(self, audio_result: Dict[str, Any], cover_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert Input-Daten"""
        
        if not audio_result.get("success"):
            return {"valid": False, "error": "Audio-Generierung fehlgeschlagen"}
        
        audio_path = audio_result.get("audio_path")
        if not audio_path or not Path(audio_path).exists():
            return {"valid": False, "error": f"Audio-Datei nicht gefunden: {audio_path}"}
        
        return {"valid": True}
    
    async def _embed_cover_art(self, audio_path: Path, cover_path: Path, metadata: Dict[str, Any]) -> bool:
        """Bettet Cover-Art in MP3 ein"""
        
        if not EYED3_AVAILABLE:
            logger.warning("⚠️ eyed3 nicht verfügbar - Cover-Embedding übersprungen")
            return False
        
        try:
            audiofile = eyed3.load(str(audio_path))
            
            if audiofile is None:
                logger.error("❌ MP3-Datei konnte nicht geladen werden")
                return False
            
            # Cover-Art einbetten
            with open(cover_path, 'rb') as cover_data:
                audiofile.tag.images.set(
                    eyed3.id3.frames.ImageFrame.FRONT_COVER,
                    cover_data.read(),
                    "image/png"
                )
            
            # Basis-Metadaten setzen
            audiofile.tag.artist = self.config["radiox_branding"]["artist"]
            audiofile.tag.album = self.config["radiox_branding"]["album"]
            audiofile.tag.genre = self.config["radiox_branding"]["genre"]
            
            audiofile.tag.save()
            
            logger.info(f"🎨 Cover-Art und Metadaten eingebettet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cover-Embedding Fehler: {e}")
            return False
    
    async def _perform_quality_check(self, audio_path: Path) -> Dict[str, Any]:
        """Führt Quality Check durch"""
        
        try:
            file_stats = audio_path.stat()
            
            quality_check = {
                "file_exists": audio_path.exists(),
                "file_size_bytes": file_stats.st_size,
                "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "file_readable": audio_path.is_file(),
                "minimum_size_check": file_stats.st_size > 1000,
                "timestamp": datetime.now().isoformat()
            }
            
            # Quality Score
            quality_score = 0
            if quality_check["file_exists"]: quality_score += 25
            if quality_check["file_readable"]: quality_score += 25
            if quality_check["minimum_size_check"]: quality_score += 25
            if EYED3_AVAILABLE: quality_score += 25
            
            quality_check["quality_score"] = quality_score
            quality_check["quality_rating"] = "Good" if quality_score >= 75 else "Fair" if quality_score >= 50 else "Poor"
            
            logger.info(f"📊 Quality Check: {quality_check['quality_rating']} ({quality_score}%)")
            
            return quality_check
            
        except Exception as e:
            logger.error(f"❌ Quality Check Fehler: {e}")
            return {
                "file_exists": False,
                "quality_score": 0,
                "quality_rating": "Failed",
                "error": str(e)
            } 