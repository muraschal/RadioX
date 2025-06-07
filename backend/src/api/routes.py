from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import glob
from datetime import datetime
from pathlib import Path

router = APIRouter()

# Output-Verzeichnis
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "outplay"

@router.get("/api/latest-broadcast")
async def get_latest_broadcast():
    """Gibt die neueste MP3-Datei und Cover-Info zurück"""
    try:
        # Suche nach MP3-Dateien im Output-Ordner
        mp3_pattern = str(OUTPUT_DIR / "RadioX_Final_*.mp3")
        mp3_files = glob.glob(mp3_pattern)
        
        if not mp3_files:
            raise HTTPException(status_code=404, detail="Keine MP3-Dateien gefunden")
        
        # Sortiere nach Dateiname (enthält Timestamp) - neueste zuerst
        mp3_files.sort(reverse=True)
        latest_mp3 = mp3_files[0]
        
        # Extrahiere Timestamp aus Dateiname (z.B. RadioX_Final_20250603_2035.mp3)
        filename = os.path.basename(latest_mp3)
        timestamp_part = filename.replace("RadioX_Final_", "").replace(".mp3", "")
        
        # Suche nach entsprechendem Cover - erst exakte Übereinstimmung, dann ähnliche
        cover_path = None
        
        # 1. Exakte Übereinstimmung
        cover_pattern = str(OUTPUT_DIR / f"RadioX_Cover_{timestamp_part}.png")
        cover_files = glob.glob(cover_pattern)
        
        if not cover_files:
            # 2. Suche nach Cover-Dateien mit ähnlichem Datum (gleicher Tag)
            date_part = timestamp_part.split('_')[0]  # z.B. "20250603"
            cover_pattern_similar = str(OUTPUT_DIR / f"RadioX_Cover_{date_part}_*.png")
            cover_files_similar = glob.glob(cover_pattern_similar)
            
            if cover_files_similar:
                # Nimm das neueste Cover vom gleichen Tag
                cover_files_similar.sort(reverse=True)
                cover_files = [cover_files_similar[0]]
        
        cover_path = cover_files[0] if cover_files else None
        
        # Suche nach Info-Datei
        info_pattern = str(OUTPUT_DIR / f"RadioX_Final_Info_{timestamp_part}.txt")
        info_files = glob.glob(info_pattern)
        info_path = info_files[0] if info_files else None
        
        # Lese Info-Datei für Metadaten
        metadata = {}
        if info_path and os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extrahiere Titel und andere Infos
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('Timestamp:'):
                            metadata['timestamp'] = line.split(':', 1)[1].strip()
                        elif line.startswith('Duration:'):
                            metadata['duration'] = line.split(':', 1)[1].strip()
                        elif 'MARCEL:' in line or 'JARVIS:' in line:
                            # Erste Zeile mit Sprecher als Titel verwenden
                            if 'title' not in metadata:
                                metadata['title'] = line.strip()
                            break
            except Exception as e:
                print(f"Fehler beim Lesen der Info-Datei: {e}")
        
        # Dateigröße ermitteln
        file_size = os.path.getsize(latest_mp3)
        
        return JSONResponse({
            "success": True,
            "mp3_file": filename,
            "mp3_path": f"/api/audio/{filename}",
            "cover_file": os.path.basename(cover_path) if cover_path else None,
            "cover_path": f"/api/cover/{os.path.basename(cover_path)}" if cover_path else None,
            "file_size": file_size,
            "timestamp": timestamp_part,
            "metadata": metadata
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Broadcast-Daten: {str(e)}")

@router.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    """Serviert MP3-Dateien"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists() or not filename.endswith('.mp3'):
        raise HTTPException(status_code=404, detail="Audio-Datei nicht gefunden")
    
    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        filename=filename
    )

@router.get("/api/cover/{filename}")
async def serve_cover(filename: str):
    """Serviert Cover-Bilder"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists() or not filename.endswith('.png'):
        raise HTTPException(status_code=404, detail="Cover-Bild nicht gefunden")
    
    return FileResponse(
        path=str(file_path),
        media_type="image/png",
        filename=filename
    )

@router.get("/api/broadcasts")
async def list_broadcasts():
    """Listet alle verfügbaren Broadcasts auf"""
    try:
        mp3_pattern = str(OUTPUT_DIR / "RadioX_Final_*.mp3")
        mp3_files = glob.glob(mp3_pattern)
        
        broadcasts = []
        for mp3_file in sorted(mp3_files, reverse=True):
            filename = os.path.basename(mp3_file)
            timestamp_part = filename.replace("RadioX_Final_", "").replace(".mp3", "")
            
            # Suche Cover
            cover_pattern = str(OUTPUT_DIR / f"RadioX_Cover_{timestamp_part}.png")
            cover_files = glob.glob(cover_pattern)
            
            broadcasts.append({
                "filename": filename,
                "timestamp": timestamp_part,
                "mp3_path": f"/api/audio/{filename}",
                "cover_path": f"/api/cover/RadioX_Cover_{timestamp_part}.png" if cover_files else None,
                "file_size": os.path.getsize(mp3_file)
            })
        
        return JSONResponse({
            "success": True,
            "broadcasts": broadcasts,
            "total": len(broadcasts)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Broadcast-Liste: {str(e)}") 