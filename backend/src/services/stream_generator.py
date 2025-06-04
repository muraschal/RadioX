"""
RadioX Stream Generator - Orchestriert die komplette Stream-Generierung für Radio Stations
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from .content_mixer import ContentMixer
from .news_summarizer import NewsSummarizer
from .voice_generator import VoiceGenerator
from .weather_service import WeatherService, get_weather_segment_for_station
from ..models.radio_stations import RadioStationType, get_station, get_default_station


class StreamGenerator:
    """Orchestriert die komplette RadioX Stream-Generierung für Radio Stations"""
    
    def __init__(self):
        self.content_mixer = ContentMixer()
        self.news_summarizer = NewsSummarizer()
        self.voice_generator = VoiceGenerator()
        self.weather_service = WeatherService()
    
    async def generate_stream(
        self,
        station_type: RadioStationType,
        template_name: Optional[str] = None,
        stream_id: Optional[str] = None,
        duration_minutes: int = 60,
        include_weather: bool = True
    ) -> Dict[str, Any]:
        """
        Generiert einen kompletten RadioX Stream für eine Radio Station
        
        Args:
            station_type: Radio Station Typ
            template_name: Content-Template Override
            stream_id: Eindeutige Stream-ID
            duration_minutes: Ziel-Dauer des Streams
            include_weather: Wetter-Updates einschließen
            
        Returns:
            Stream-Generierung Ergebnis
        """
        try:
            # Stream ID generieren falls nicht vorhanden
            if not stream_id:
                stream_id = f"{station_type.value}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"🎙️ Generiere Stream für {station_type.value} (ID: {stream_id})")
            
            # Station-Konfiguration laden
            station_config = get_station(station_type)
            
            # Phase 1: Content-Mix erstellen
            logger.info("📊 Phase 1: Content-Mix erstellen...")
            content_mix = await self.content_mixer.create_comprehensive_content_mix(
                stream_template=template_name or "balanced_news",
                target_duration_minutes=duration_minutes
            )
            
            # Phase 2: Wetter-Daten hinzufügen (falls aktiviert)
            weather_data = None
            if include_weather and station_config.weather_updates:
                logger.info("🌤️ Wetter-Daten abrufen...")
                weather_data = await self.weather_service.get_weather_for_station(station_config.station_id)
                
                # Wetter zu Content-Mix hinzufügen
                if weather_data and weather_data.get("radio_current"):
                    content_mix["weather_segment"] = {
                        "type": "weather",
                        "location": weather_data["location"],
                        "current_text": weather_data["radio_current"],
                        "forecast_text": weather_data.get("radio_forecast", ""),
                        "priority": 8,  # Hohe Priorität für Wetter
                        "estimated_duration_seconds": 30
                    }
            
            # Phase 3: Radio-Skript erstellen
            logger.info("📝 Phase 2: Radio-Skript erstellen...")
            radio_script = await self.news_summarizer.create_news_script(
                content_mix=content_mix,
                persona_name=station_config.station_id  # Verwende station_id als persona_name
            )
            
            # Phase 4: Voice-Over generieren
            logger.info("🎤 Phase 3: Voice-Over generieren...")
            voice_generation = await self.voice_generator.generate_complete_stream(
                radio_script=radio_script,
                persona_name=station_config.station_id,  # Verwende station_id als persona_name
                stream_id=stream_id
            )
            
            # Ergebnis zusammenstellen
            result = {
                "stream_id": stream_id,
                "station_id": station_config.station_id,
                "station_name": station_config.display_name,
                "status": "completed",
                "generated_at": datetime.now().isoformat(),
                "estimated_duration_minutes": duration_minutes,
                "total_segments": len(voice_generation.get("audio_files", [])),
                "audio_files": voice_generation.get("audio_files", []),
                "station_config": {
                    "station_id": station_config.station_id,
                    "display_name": station_config.display_name,
                    "tagline": station_config.tagline,
                    "tone": station_config.tone,
                    "energy_level": station_config.energy_level,
                    "content_profile": station_config.content_profile.model_dump(),
                    "voice_profile": station_config.voice_profile.model_dump()
                },
                "generation_pipeline": {
                    "content_mixer": content_mix.get("summary", {}),
                    "weather_included": weather_data is not None,
                    "weather_location": weather_data["location"] if weather_data else None,
                    "news_summarizer": radio_script.get("summary", {}),
                    "voice_generator": voice_generation.get("summary", {})
                },
                "ready_for_broadcast": True
            }
            
            logger.info(f"✅ Stream {stream_id} erfolgreich generiert!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Stream-Generierung: {e}")
            return {
                "stream_id": stream_id or "unknown",
                "status": "failed",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _get_template_for_station(self, station_type: RadioStationType) -> str:
        """Leitet Template aus Radio Station ab"""
        
        template_mapping = {
            RadioStationType.BITCOIN_OG: "bitcoin_focus",
            RadioStationType.TRADFI_NEWS: "business_focus", 
            RadioStationType.ZUERI_STYLE: "swiss_local",
            RadioStationType.SWISS_LOCAL: "swiss_local",
            RadioStationType.BREAKING_NEWS: "balanced_news",
            RadioStationType.TECH_INSIDER: "balanced_news"  # Tech-fokussiert aber ausgewogen
        }
        
        return template_mapping.get(station_type, "balanced_news")
    
    def _finalize_stream_data(
        self,
        stream_data: Dict[str, Any],
        content_mix: Dict[str, Any],
        radio_script: Dict[str, Any],
        station: Any,
        template_name: str
    ) -> Dict[str, Any]:
        """Finalisiert Stream-Daten mit allen Metadaten"""
        
        # Basis-Stream-Daten
        final_stream = stream_data.copy()
        
        # Erweiterte Metadaten
        final_stream.update({
            "template_used": template_name,
            "station_config": {
                "station_id": station.station_id,
                "display_name": station.display_name,
                "tagline": station.tagline,
                "target_audience": station.target_audience,
                "tone": station.tone,
                "energy_level": station.energy_level,
                "formality": station.formality,
                "news_format": station.news_format,
                "segment_style": station.segment_style,
                "content_profile": station.content_profile.dict(),
                "voice_profile": station.voice_profile.dict(),
                "special_features": {
                    "weather_updates": station.weather_updates,
                    "traffic_updates": station.traffic_updates,
                    "bitcoin_price_updates": station.bitcoin_price_updates,
                    "breaking_news_priority": station.breaking_news_priority
                }
            },
            "generation_pipeline": {
                "content_mixer": {
                    "template": content_mix.get("template"),
                    "quality_score": content_mix.get("quality_score"),
                    "total_items": content_mix.get("total_items"),
                    "categories_used": len(content_mix.get("categories", {}))
                },
                "news_summarizer": {
                    "segments_created": len(radio_script.get("segments", [])),
                    "estimated_duration_seconds": radio_script.get("metadata", {}).get("estimated_duration_seconds", 0),
                    "has_weather": radio_script.get("metadata", {}).get("has_weather", False),
                    "has_intro_jingle": "intro_jingle" in radio_script,
                    "has_outro_jingle": "outro_jingle" in radio_script
                },
                "voice_generator": {
                    "audio_files_created": len(stream_data.get("audio_files", [])),
                    "total_duration_seconds": stream_data.get("total_duration_seconds", 0),
                    "voice_settings": stream_data.get("audio_files", [{}])[0].get("voice_settings", {})
                }
            },
            "content_breakdown": content_mix.get("content_breakdown", {}),
            "ready_for_broadcast": True
        })
        
        return final_stream
    
    def _get_completed_phases(self, error: Exception) -> List[str]:
        """Ermittelt welche Phasen erfolgreich abgeschlossen wurden"""
        
        error_str = str(error).lower()
        
        if "content" in error_str or "mixer" in error_str:
            return []
        elif "summarizer" in error_str or "gpt" in error_str:
            return ["content_mix"]
        elif "voice" in error_str or "elevenlabs" in error_str:
            return ["content_mix", "radio_script"]
        else:
            return ["content_mix", "radio_script", "voice_generation"]
    
    async def generate_multiple_streams(
        self,
        stations: List[RadioStationType],
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Generiert mehrere Streams parallel für verschiedene Radio Stations
        
        Args:
            stations: Liste von Radio Station Typen
            duration_minutes: Ziel-Dauer pro Stream
            
        Returns:
            Dict mit allen generierten Streams
        """
        
        logger.info(f"🎙️ Generiere {len(stations)} Streams parallel...")
        
        # Streams parallel generieren (aber Rate-Limited)
        semaphore = asyncio.Semaphore(2)  # Max 2 gleichzeitige Streams
        
        async def generate_single_stream(station_type: RadioStationType) -> tuple[RadioStationType, Dict[str, Any]]:
            async with semaphore:
                stream_data = await self.generate_stream(
                    station_type=station_type,
                    duration_minutes=duration_minutes
                )
                return station_type, stream_data
        
        # Alle Streams starten
        tasks = [generate_single_stream(station) for station in stations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse sammeln
        streams = {}
        successful = 0
        failed = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Stream-Generierung fehlgeschlagen: {result}")
                failed += 1
            else:
                station_type, stream_data = result
                streams[station_type.value] = stream_data
                
                if stream_data.get("status") == "completed":
                    successful += 1
                else:
                    failed += 1
        
        logger.info(f"✅ Multi-Stream Generierung abgeschlossen: {successful} erfolgreich, {failed} fehlgeschlagen")
        
        return {
            "batch_id": str(uuid.uuid4())[:8],
            "generated_at": datetime.now().isoformat(),
            "total_streams": len(stations),
            "successful_streams": successful,
            "failed_streams": failed,
            "streams": streams,
            "summary": {
                "total_duration_minutes": sum(
                    stream.get("estimated_duration_minutes", 0) 
                    for stream in streams.values()
                ),
                "total_audio_files": sum(
                    len(stream.get("audio_files", [])) 
                    for stream in streams.values()
                ),
                "stations_generated": list(streams.keys())
            }
        }
    
    async def get_stream_preview(
        self,
        station_type: RadioStationType,
        template_name: Optional[str] = None,
        include_weather: bool = True
    ) -> Dict[str, Any]:
        """
        Erstellt eine Vorschau eines Streams ohne Audio-Generierung
        
        Args:
            station_type: Radio Station Typ
            template_name: Content-Template Override
            include_weather: Wetter-Updates einschließen
            
        Returns:
            Stream-Preview
        """
        try:
            preview_id = f"preview_{station_type.value}_{uuid.uuid4().hex[:6]}"
            
            logger.info(f"👀 Erstelle Preview für {station_type.value}")
            
            # Station-Konfiguration
            station_config = get_station(station_type)
            
            # Content-Mix Preview
            content_mix = await self.content_mixer.create_comprehensive_content_mix(
                stream_template=template_name or "balanced_news",
                target_duration_minutes=60
            )
            
            # Wetter-Preview
            weather_preview = None
            if include_weather and station_config.weather_updates:
                weather_data = await self.weather_service.get_weather_for_station(station_config.station_id)
                if weather_data:
                    weather_preview = {
                        "location": weather_data["location"],
                        "current_summary": weather_data["radio_current"][:100] + "..." if weather_data.get("radio_current") else None,
                        "has_forecast": bool(weather_data.get("radio_forecast"))
                    }
            
            # Radio-Skript Preview
            radio_script = await self.news_summarizer.create_news_script(
                content_mix=content_mix,
                persona_name=station_config.station_id  # Verwende station_id als persona_name
            )
            
            result = {
                "preview_id": preview_id,
                "station_id": station_config.station_id,
                "station_name": station_config.display_name,
                "template": template_name or "balanced_news",
                "generated_at": datetime.now().isoformat(),
                "content_mix_summary": content_mix.get("summary", {}),
                "weather_preview": weather_preview,
                "script_summary": radio_script.get("summary", {}),
                "voice_segments": radio_script.get("segments", [])[:5],  # Erste 5 Segmente
                "station_config": {
                    "tagline": station_config.tagline,
                    "tone": station_config.tone,
                    "energy_level": station_config.energy_level,
                    "voice_profile": {
                        "voice_name": station_config.voice_profile.voice_name,
                        "voice_id": station_config.voice_profile.voice_id,
                        "speed": station_config.voice_profile.speed
                    }
                },
                "ready_for_audio_generation": True
            }
            
            logger.info(f"✅ Preview {preview_id} erstellt")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Preview-Erstellung: {e}")
            return {
                "preview_id": "error",
                "status": "failed",
                "error": str(e)
            }
    
    async def get_default_stream_preview(self) -> Dict[str, Any]:
        """Erstellt Preview für die Default Radio Station (Breaking News)"""
        
        default_station = get_default_station()
        return await self.get_stream_preview(RadioStationType.BREAKING_NEWS)
    
    def get_available_stations(self) -> List[Dict[str, Any]]:
        """Gibt alle verfügbaren Radio Stations zurück"""
        
        from ..models.radio_stations import list_stations
        
        stations_info = []
        for station in list_stations():
            # Top Content-Kategorie finden
            content_dict = station.content_profile.dict()
            top_category = max(content_dict.items(), key=lambda x: x[1])
            
            stations_info.append({
                "station_id": station.station_id,
                "display_name": station.display_name,
                "tagline": station.tagline,
                "description": station.description,
                "target_audience": station.target_audience,
                "tone": station.tone,
                "energy_level": station.energy_level,
                "top_content": f"{top_category[0]} ({top_category[1]}%)",
                "voice_name": station.voice_profile.voice_name,
                "special_features": {
                    "weather": station.weather_updates,
                    "traffic": station.traffic_updates,
                    "bitcoin_price": station.bitcoin_price_updates,
                    "breaking_news": station.breaking_news_priority
                }
            })
        
        return stations_info 