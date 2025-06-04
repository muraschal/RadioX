"""
RadioX Stream Scheduler - Automatische 30-Minuten-Stream-Generierung
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from src.models.radio_stations import RadioStationType, get_station
from src.services.stream_generator import StreamGenerator


class StreamScheduler:
    """Automatischer Scheduler für RadioX Stream-Generierung alle 30 Minuten"""
    
    def __init__(self):
        self.stream_generator = StreamGenerator()
        self.active_stations = [
            RadioStationType.BREAKING_NEWS,
            RadioStationType.ZUERI_STYLE,
            RadioStationType.BITCOIN_OG,
            RadioStationType.TRADFI_NEWS,
            RadioStationType.TECH_INSIDER,
            RadioStationType.SWISS_LOCAL
        ]
        self.is_running = False
        self.current_streams = {}
        
    async def start_scheduler(self):
        """Startet den 30-Minuten-Scheduler"""
        logger.info("🕐 RadioX Stream Scheduler gestartet - Generierung alle 30 Minuten")
        self.is_running = True
        
        # Erste Generierung sofort
        await self.generate_all_streams()
        
        # Dann alle 30 Minuten
        while self.is_running:
            # Warte bis zur nächsten vollen halben Stunde
            now = datetime.now()
            next_half_hour = self._get_next_half_hour(now)
            wait_seconds = (next_half_hour - now).total_seconds()
            
            logger.info(f"⏰ Nächste Stream-Generierung um {next_half_hour.strftime('%H:%M')} ({wait_seconds:.0f}s)")
            
            await asyncio.sleep(wait_seconds)
            
            if self.is_running:
                await self.generate_all_streams()
    
    def _get_next_half_hour(self, current_time: datetime) -> datetime:
        """Berechnet die nächste volle halbe Stunde"""
        if current_time.minute < 30:
            # Nächste halbe Stunde in derselben Stunde
            return current_time.replace(minute=30, second=0, microsecond=0)
        else:
            # Nächste volle Stunde
            next_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_hour
    
    async def generate_all_streams(self):
        """Generiert Streams für alle aktiven Stationen"""
        generation_time = datetime.now()
        logger.info(f"🎙️ STREAM-GENERIERUNG GESTARTET - {generation_time.strftime('%H:%M:%S')}")
        logger.info("=" * 80)
        
        # Streams parallel generieren
        tasks = []
        for station_type in self.active_stations:
            task = self._generate_station_stream(station_type, generation_time)
            tasks.append(task)
        
        # Alle Streams parallel ausführen
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse auswerten
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            station_type = self.active_stations[i]
            
            if isinstance(result, Exception):
                logger.error(f"❌ {station_type.value}: {result}")
                failed += 1
            elif result and result.get("status") == "completed":
                self.current_streams[station_type.value] = result
                logger.success(f"✅ {station_type.value}: Stream {result['stream_id']} generiert")
                successful += 1
            else:
                logger.error(f"❌ {station_type.value}: Unbekannter Fehler")
                failed += 1
        
        logger.info("=" * 80)
        logger.info(f"🎯 STREAM-GENERIERUNG ABGESCHLOSSEN: {successful} erfolgreich, {failed} fehlgeschlagen")
        
        # Broadcast-Ready Streams anzeigen
        ready_streams = [
            stream_id for stream_id, stream_data in self.current_streams.items()
            if stream_data.get("ready_for_broadcast", False)
        ]
        
        logger.info(f"📻 BROADCAST-READY: {len(ready_streams)} Streams")
        for stream_id in ready_streams:
            stream_data = self.current_streams[stream_id]
            logger.info(f"   • {stream_id}: {stream_data.get('total_segments', 0)} Segmente, {stream_data.get('estimated_duration_minutes', 0)}min")
    
    async def _generate_station_stream(self, station_type: RadioStationType, generation_time: datetime) -> Dict:
        """Generiert Stream für eine spezifische Station"""
        try:
            station_config = get_station(station_type)
            
            # Stream-ID mit Zeitstempel
            stream_id = f"{station_type.value}_{generation_time.strftime('%Y%m%d_%H%M')}"
            
            logger.info(f"🔄 {station_type.value}: Generiere Stream...")
            
            # Stream generieren mit station-spezifischer Dauer
            stream_result = await self.stream_generator.generate_stream(
                station_type=station_type,
                stream_id=stream_id,
                duration_minutes=station_config.stream_duration_minutes,
                include_weather=station_config.weather_updates
            )
            
            return stream_result
            
        except Exception as e:
            logger.error(f"💥 Fehler bei {station_type.value}: {e}")
            return {"status": "failed", "error": str(e)}
    
    def stop_scheduler(self):
        """Stoppt den Scheduler"""
        logger.info("🛑 Stream Scheduler gestoppt")
        self.is_running = False
    
    def get_current_streams(self) -> Dict:
        """Gibt aktuelle Streams zurück"""
        return self.current_streams.copy()
    
    def get_stream_status(self) -> Dict:
        """Gibt Status aller Streams zurück"""
        status = {
            "scheduler_running": self.is_running,
            "total_stations": len(self.active_stations),
            "active_streams": len(self.current_streams),
            "last_generation": None,
            "next_generation": None,
            "streams": {}
        }
        
        # Letzte Generierung finden
        if self.current_streams:
            latest_stream = max(
                self.current_streams.values(),
                key=lambda x: x.get("generated_at", "")
            )
            status["last_generation"] = latest_stream.get("generated_at")
        
        # Nächste Generierung berechnen
        if self.is_running:
            next_half_hour = self._get_next_half_hour(datetime.now())
            status["next_generation"] = next_half_hour.isoformat()
        
        # Stream-Details
        for station_id, stream_data in self.current_streams.items():
            status["streams"][station_id] = {
                "stream_id": stream_data.get("stream_id"),
                "status": stream_data.get("status"),
                "generated_at": stream_data.get("generated_at"),
                "duration_minutes": stream_data.get("estimated_duration_minutes"),
                "segments": stream_data.get("total_segments"),
                "ready_for_broadcast": stream_data.get("ready_for_broadcast", False)
            }
        
        return status


# Globaler Scheduler (Singleton)
_scheduler_instance = None

def get_scheduler() -> StreamScheduler:
    """Gibt Scheduler-Instanz zurück (Singleton)"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = StreamScheduler()
    return _scheduler_instance

async def start_radiox_scheduler():
    """Startet den RadioX Scheduler"""
    scheduler = get_scheduler()
    await scheduler.start_scheduler()

def stop_radiox_scheduler():
    """Stoppt den RadioX Scheduler"""
    scheduler = get_scheduler()
    scheduler.stop_scheduler() 