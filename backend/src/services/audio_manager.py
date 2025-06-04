"""
RadioX Audio Manager - Professionelle Audio-Datei Organisation
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from loguru import logger


class AudioManager:
    """Verwaltet Audio-Dateien mit professioneller Ordnerstruktur"""
    
    def __init__(self, base_audio_dir: str = "audio_archive"):
        self.base_dir = Path(base_audio_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Ordnerstruktur definieren
        self.structure = {
            "streams": self.base_dir / "streams",           # Fertige Streams
            "segments": self.base_dir / "segments",         # Einzelne Voice-Segmente
            "temp": self.base_dir / "temp",                 # Temporäre Dateien
            "archive": self.base_dir / "archive",           # Archivierte Streams
            "exports": self.base_dir / "exports",           # Export-Dateien
            "backups": self.base_dir / "backups"            # Backups
        }
        
        # Alle Ordner erstellen
        for folder in self.structure.values():
            folder.mkdir(exist_ok=True)
    
    def get_stream_path(
        self, 
        stream_id: str, 
        persona: str, 
        timestamp: Optional[datetime] = None
    ) -> Path:
        """
        Erstellt organisierten Pfad für Stream
        
        Struktur: audio_archive/streams/YYYY/MM/DD/HH/persona_streamid/
        """
        if not timestamp:
            timestamp = datetime.now()
        
        # Hierarchische Ordnerstruktur
        year = timestamp.strftime("%Y")
        month = timestamp.strftime("%m")
        day = timestamp.strftime("%d")
        hour = timestamp.strftime("%H")
        
        stream_folder = f"{persona}_{stream_id}"
        
        stream_path = (
            self.structure["streams"] / 
            year / month / day / hour / 
            stream_folder
        )
        
        stream_path.mkdir(parents=True, exist_ok=True)
        return stream_path
    
    def get_segment_path(
        self,
        persona: str,
        segment_type: str,
        timestamp: Optional[datetime] = None
    ) -> Path:
        """
        Pfad für einzelne Voice-Segmente
        
        Struktur: audio_archive/segments/persona/YYYY-MM/segment_type/
        """
        if not timestamp:
            timestamp = datetime.now()
        
        year_month = timestamp.strftime("%Y-%m")
        
        segment_path = (
            self.structure["segments"] /
            persona / year_month / segment_type
        )
        
        segment_path.mkdir(parents=True, exist_ok=True)
        return segment_path
    
    def organize_stream_files(
        self,
        temp_files: List[Dict[str, Any]],
        stream_id: str,
        persona: str,
        stream_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organisiert temporäre Stream-Dateien in finale Struktur
        """
        timestamp = datetime.now()
        stream_path = self.get_stream_path(stream_id, persona, timestamp)
        
        logger.info(f"📁 Organisiere Stream-Dateien: {stream_path}")
        
        organized_files = {
            "stream_path": str(stream_path),
            "audio_files": [],
            "metadata_file": None,
            "manifest_file": None,
            "timestamp": timestamp.isoformat()
        }
        
        # Audio-Dateien kopieren und umbenennen
        for file_info in temp_files:
            audio_file_path = file_info.get("audio_file")
            
            # Überspringe Dateien ohne gültigen Pfad
            if not audio_file_path:
                logger.warning(f"⚠️ Überspringe Datei ohne Pfad: {file_info.get('segment_type', 'unknown')}")
                continue
                
            temp_file = Path(audio_file_path)
            
            if temp_file.exists():
                # Neuer Dateiname mit Zeitstempel
                segment_order = file_info.get("segment_order", 0)
                segment_type = file_info.get("segment_type", "unknown")
                
                new_filename = f"{segment_order:02d}_{segment_type}_{timestamp.strftime('%H%M%S')}.mp3"
                new_path = stream_path / new_filename
                
                # Datei kopieren
                shutil.copy2(temp_file, new_path)
                
                # Metadaten aktualisieren
                file_info["audio_file"] = str(new_path)
                file_info["organized_filename"] = new_filename
                
                organized_files["audio_files"].append(file_info)
                
                logger.debug(f"📄 Datei organisiert: {new_filename}")
            else:
                logger.warning(f"⚠️ Temporäre Datei nicht gefunden: {temp_file}")
        
        # Stream-Metadaten speichern
        metadata_file = stream_path / "stream_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(stream_metadata, f, indent=2, ensure_ascii=False)
        organized_files["metadata_file"] = str(metadata_file)
        
        # Stream-Manifest erstellen
        manifest = self._create_stream_manifest(
            stream_id, persona, organized_files, stream_metadata, timestamp
        )
        manifest_file = stream_path / "stream_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        organized_files["manifest_file"] = str(manifest_file)
        
        logger.success(f"✅ Stream organisiert: {len(organized_files['audio_files'])} Dateien")
        return organized_files
    
    def _create_stream_manifest(
        self,
        stream_id: str,
        persona: str,
        organized_files: Dict[str, Any],
        stream_metadata: Dict[str, Any],
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Erstellt detailliertes Stream-Manifest"""
        
        return {
            "stream_info": {
                "stream_id": stream_id,
                "persona": persona,
                "created_at": timestamp.isoformat(),
                "created_date": timestamp.strftime("%Y-%m-%d"),
                "created_time": timestamp.strftime("%H:%M:%S"),
                "weekday": timestamp.strftime("%A"),
                "timezone": "Europe/Zurich"
            },
            "audio_files": organized_files["audio_files"],
            "file_structure": {
                "total_files": len(organized_files["audio_files"]),
                "total_duration_seconds": sum(
                    f.get("duration_seconds", 0) for f in organized_files["audio_files"]
                ),
                "file_sizes_mb": [
                    round(Path(f["audio_file"]).stat().st_size / (1024*1024), 2)
                    for f in organized_files["audio_files"]
                    if Path(f["audio_file"]).exists()
                ]
            },
            "stream_metadata": stream_metadata,
            "archive_info": {
                "archive_path": str(organized_files["stream_path"]),
                "can_be_archived_after": (timestamp + timedelta(days=30)).isoformat(),
                "backup_status": "pending"
            }
        }
    
    def archive_old_streams(self, days_old: int = 30) -> Dict[str, Any]:
        """
        Archiviert alte Streams (komprimiert und verschiebt)
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archived_count = 0
        archived_size_mb = 0
        
        logger.info(f"🗄️ Archiviere Streams älter als {days_old} Tage...")
        
        # Durchsuche Stream-Ordner
        streams_dir = self.structure["streams"]
        
        for year_dir in streams_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue
                    
                for day_dir in month_dir.iterdir():
                    if not day_dir.is_dir():
                        continue
                    
                    # Prüfe Datum
                    try:
                        folder_date = datetime.strptime(
                            f"{year_dir.name}-{month_dir.name}-{day_dir.name}",
                            "%Y-%m-%d"
                        )
                        
                        if folder_date < cutoff_date:
                            # Archiviere ganzen Tag
                            archive_path = self._archive_day_folder(day_dir, folder_date)
                            if archive_path:
                                archived_count += 1
                                archived_size_mb += self._get_folder_size_mb(day_dir)
                                
                    except ValueError:
                        logger.warning(f"Ungültiger Ordnername: {day_dir}")
        
        return {
            "archived_streams": archived_count,
            "archived_size_mb": round(archived_size_mb, 2),
            "archive_date": datetime.now().isoformat()
        }
    
    def _archive_day_folder(self, day_folder: Path, folder_date: datetime) -> Optional[Path]:
        """Archiviert einen ganzen Tag-Ordner"""
        
        archive_name = f"streams_{folder_date.strftime('%Y%m%d')}.tar.gz"
        archive_path = self.structure["archive"] / archive_name
        
        try:
            # Komprimiere Ordner
            shutil.make_archive(
                str(archive_path.with_suffix('')),
                'gztar',
                str(day_folder.parent),
                str(day_folder.name)
            )
            
            # Lösche Original-Ordner
            shutil.rmtree(day_folder)
            
            logger.info(f"📦 Archiviert: {archive_name}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Archivierung fehlgeschlagen für {day_folder}: {e}")
            return None
    
    def _get_folder_size_mb(self, folder: Path) -> float:
        """Berechnet Ordnergröße in MB"""
        total_size = 0
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Holt detaillierte Speicher-Statistiken"""
        
        stats = {
            "total_size_mb": 0,
            "folder_stats": {},
            "file_counts": {},
            "recent_streams": [],
            "storage_health": "good"
        }
        
        # Statistiken pro Ordner
        for folder_name, folder_path in self.structure.items():
            if folder_path.exists():
                size_mb = self._get_folder_size_mb(folder_path)
                file_count = len(list(folder_path.rglob("*.mp3")))
                
                stats["folder_stats"][folder_name] = {
                    "size_mb": round(size_mb, 2),
                    "file_count": file_count,
                    "path": str(folder_path)
                }
                
                stats["total_size_mb"] += size_mb
                stats["file_counts"][folder_name] = file_count
        
        # Neueste Streams finden
        streams_dir = self.structure["streams"]
        recent_manifests = []
        
        for manifest_file in streams_dir.rglob("stream_manifest.json"):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    manifest["manifest_path"] = str(manifest_file)
                    recent_manifests.append(manifest)
            except Exception:
                continue
        
        # Nach Datum sortieren
        recent_manifests.sort(
            key=lambda x: x.get("stream_info", {}).get("created_at", ""),
            reverse=True
        )
        
        stats["recent_streams"] = recent_manifests[:10]  # Top 10
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        # Storage Health bewerten
        if stats["total_size_mb"] > 10000:  # > 10GB
            stats["storage_health"] = "warning"
        if stats["total_size_mb"] > 50000:  # > 50GB
            stats["storage_health"] = "critical"
        
        return stats
    
    def cleanup_temp_files(self, hours_old: int = 24) -> int:
        """Löscht alte temporäre Dateien"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours_old)
        deleted_count = 0
        
        temp_dir = self.structure["temp"]
        
        for temp_file in temp_dir.rglob("*"):
            if temp_file.is_file():
                file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                
                if file_time < cutoff_time:
                    try:
                        temp_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Konnte temp Datei nicht löschen {temp_file}: {e}")
        
        logger.info(f"🧹 {deleted_count} temporäre Dateien gelöscht")
        return deleted_count
    
    def export_stream_for_broadcast(
        self,
        stream_manifest_path: str,
        export_format: str = "mp3"
    ) -> Optional[Path]:
        """
        Exportiert Stream für Broadcast (kombiniert alle Segmente)
        """
        try:
            with open(stream_manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            stream_info = manifest["stream_info"]
            audio_files = manifest["audio_files"]
            
            # Export-Dateiname
            export_filename = (
                f"{stream_info['persona']}_{stream_info['stream_id']}_"
                f"{stream_info['created_date']}_{stream_info['created_time'].replace(':', '')}.{export_format}"
            )
            
            export_path = self.structure["exports"] / export_filename
            
            # TODO: Hier würde Audio-Mixing stattfinden
            # Für jetzt kopiere erstes Audio-File als Platzhalter
            if audio_files:
                first_audio = Path(audio_files[0]["audio_file"])
                if first_audio.exists():
                    shutil.copy2(first_audio, export_path)
                    logger.success(f"📻 Stream exportiert: {export_filename}")
                    return export_path
            
            return None
            
        except Exception as e:
            logger.error(f"Export fehlgeschlagen: {e}")
            return None 