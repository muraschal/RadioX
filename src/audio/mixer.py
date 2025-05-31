from pathlib import Path
from typing import List, Optional
import os
import subprocess
from loguru import logger

class AudioMixer:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.segments: List[str] = []
        
    def load_audio(self, file_path: str) -> str:
        """Lädt eine Audiodatei (gibt Pfad zurück für ffmpeg)."""
        if not os.path.exists(file_path):
            logger.error(f"Audiodatei nicht gefunden: {file_path}")
            raise FileNotFoundError(f"Audiodatei nicht gefunden: {file_path}")
        return file_path
            
    def add_segment(self, audio_path: str, crossfade: int = 2000) -> None:
        """Fügt ein Audio-Segment zum Mix hinzu."""
        self.segments.append(audio_path)
            
    def mix_segments(self, segments: List[str], crossfade: int = 2000) -> str:
        """Mischt mehrere Audio-Segmente mit ffmpeg zusammen."""
        if not segments:
            raise ValueError("Keine Segmente zum Mischen vorhanden")
            
        if len(segments) == 1:
            return segments[0]
            
        # Temporäre Ausgabedatei
        temp_output = self.output_dir / "temp_mix.mp3"
        
        # ffmpeg-Befehl für das Mischen mit Crossfade
        cmd = ["ffmpeg", "-y"]  # -y überschreibt Ausgabedatei
        
        # Eingabedateien hinzufügen
        for segment in segments:
            cmd.extend(["-i", segment])
        
        # Filter für Crossfade zwischen allen Segmenten
        filter_complex = ""
        for i in range(len(segments) - 1):
            if i == 0:
                filter_complex += f"[0][1]acrossfade=d={crossfade/1000}[a{i}];"
            else:
                filter_complex += f"[a{i-1}][{i+1}]acrossfade=d={crossfade/1000}[a{i}];"
        
        if len(segments) > 2:
            cmd.extend(["-filter_complex", filter_complex, "-map", f"[a{len(segments)-2}]"])
        else:
            cmd.extend(["-filter_complex", filter_complex, "-map", "[a0]"])
            
        cmd.append(str(temp_output))
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio-Segmente erfolgreich gemischt: {temp_output}")
            return str(temp_output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Fehler beim Mischen mit ffmpeg: {e}")
            # Fallback: Einfache Konkatenation ohne Crossfade
            return self._simple_concat(segments)
        
    def _simple_concat(self, segments: List[str]) -> str:
        """Einfache Konkatenation ohne Crossfade als Fallback."""
        temp_output = self.output_dir / "temp_concat.mp3"
        
        # Erstelle Dateiliste für ffmpeg concat
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, "w") as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(temp_output)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio-Segmente konkateniert: {temp_output}")
            return str(temp_output)
        except subprocess.CalledProcessError as e:
            logger.error(f"Fehler bei der Konkatenation: {e}")
            raise
        
    def export(self, filename: str, format: str = "mp3", bitrate: str = "320k") -> str:
        """Exportiert den Mix als Datei."""
        if not self.segments:
            raise ValueError("Keine Segmente zum Exportieren vorhanden")
            
        # Mische alle Segmente
        mixed_audio = self.mix_segments(self.segments)
        
        # Kopiere zur finalen Ausgabedatei
        output_path = self.output_dir / filename
        
        cmd = [
            "ffmpeg", "-y",
            "-i", mixed_audio,
            "-b:a", bitrate,
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Mix exportiert nach {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Fehler beim Export: {e}")
            raise
        
    def clear(self) -> None:
        """Setzt den aktuellen Mix zurück."""
        self.segments = [] 