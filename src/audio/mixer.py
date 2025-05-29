from pathlib import Path
from typing import List, Optional
from pydub import AudioSegment
from loguru import logger

class AudioMixer:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_mix: Optional[AudioSegment] = None
        
    def load_audio(self, file_path: str) -> AudioSegment:
        """Lädt eine Audiodatei."""
        try:
            return AudioSegment.from_file(file_path)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Audiodatei {file_path}: {e}")
            raise
            
    def add_segment(self, audio: AudioSegment, crossfade: int = 2000) -> None:
        """Fügt ein Audio-Segment zum Mix hinzu."""
        if self.current_mix is None:
            self.current_mix = audio
        else:
            self.current_mix = self.current_mix.append(audio, crossfade=crossfade)
            
    def mix_segments(self, segments: List[AudioSegment], crossfade: int = 2000) -> AudioSegment:
        """Mischt mehrere Audio-Segmente zusammen."""
        if not segments:
            raise ValueError("Keine Segmente zum Mischen vorhanden")
            
        result = segments[0]
        for segment in segments[1:]:
            result = result.append(segment, crossfade=crossfade)
        return result
        
    def export(self, filename: str, format: str = "mp3", bitrate: str = "320k") -> str:
        """Exportiert den Mix als Datei."""
        if self.current_mix is None:
            raise ValueError("Kein Mix zum Exportieren vorhanden")
            
        output_path = self.output_dir / filename
        self.current_mix.export(
            str(output_path),
            format=format,
            bitrate=bitrate
        )
        logger.info(f"Mix exportiert nach {output_path}")
        return str(output_path)
        
    def clear(self) -> None:
        """Setzt den aktuellen Mix zurück."""
        self.current_mix = None 