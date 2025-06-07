#!/usr/bin/env python3

"""
RadioX Master Control Script
============================

Zentrales Script für die komplette RadioX Broadcast-Generierung.
Alle Funktionalitäten sind modular aufgebaut und erweiterbar.

Usage:
    python radiox_master.py --action generate_broadcast --time 16:00
    python radiox_master.py --action analyze_news --max_age 1
    python radiox_master.py --action test_services
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.data_collection_service import DataCollectionService
from src.services.content_processing_service import ContentProcessingService
from src.services.broadcast_generation_service import BroadcastGenerationService
from src.services.audio_generation_service import AudioGenerationService
from src.services.system_monitoring_service import SystemMonitoringService


class RadioXMaster:
    """
    Master Controller für RadioX
    
    Koordiniert alle Services und stellt eine einheitliche API bereit.
    """
    
    def __init__(self):
        self.data_collector = DataCollectionService()
        self.content_processor = ContentProcessingService()
        self.broadcast_generator = BroadcastGenerationService()
        self.audio_generator = AudioGenerationService()
        self.system_monitor = SystemMonitoringService()
        
        # Konfiguration
        self.config = {
            "default_news_count": 4,
            "max_news_age_hours": 6,
            "default_broadcast_duration": 10,
            "supported_languages": ["de", "en"],
            "radio_channels": ["zurich", "basel", "bern"],
            "broadcast_styles": ["morning", "afternoon", "evening", "night"]
        }
    
    async def generate_complete_broadcast(
        self, 
        target_time: Optional[str] = None,
        channel: str = "zurich",
        news_count: int = 4,
        max_news_age: int = 6,
        generate_audio: bool = False,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generiert einen kompletten Broadcast
        
        Args:
            target_time: Zielzeit (HH:MM) oder None für jetzt
            channel: Radio-Kanal (zurich, basel, bern)
            news_count: Anzahl News für den Broadcast
            max_news_age: Maximales Alter der News in Stunden
            generate_audio: Ob Audio-Dateien generiert werden sollen
            language: Sprache des Broadcasts (de, en)
            
        Returns:
            Dict mit allen Broadcast-Daten
        """
        
        logger.info(f"🎙️ RADIOX MASTER V3 - {'🇺🇸 ENGLISH' if language == 'en' else '🇩🇪 GERMAN'} BROADCAST GENERATION")
        logger.info("=" * 60)
        
        try:
            # 1. DATENSAMMLUNG
            logger.info("📊 Phase 1: Datensammlung")
            data = await self.data_collector.collect_all_data(
                channel=channel,
                max_news_age_hours=max_news_age or self.config["max_news_age_hours"]  # Standard: 6 Stunden
            )
            
            # 2. CONTENT-VERARBEITUNG
            logger.info("🔄 Phase 2: Content-Verarbeitung")
            processed_content = await self.content_processor.process_content(
                raw_data=data,
                target_news_count=news_count,
                target_time=target_time
            )
            
            # 3. BROADCAST-GENERIERUNG
            logger.info(f"🎭 Phase 3: {'🇺🇸 English V3' if language == 'en' else '🇩🇪 German'} Broadcast Generation")
            broadcast_script = await self.broadcast_generator.generate_broadcast(
                content=processed_content,
                target_time=target_time,
                channel=channel,
                language=language
            )
            
            # 4. AUDIO-GENERIERUNG MIT COVER (optional)
            audio_files = None
            if generate_audio:
                logger.info("🔊🎨 Phase 4: Audio- und Cover-Generierung")
                audio_files = await self.audio_generator.generate_complete_broadcast(
                    script=broadcast_script,
                    include_music=False,
                    include_cover=True,
                    export_format="mp3"
                )
            
            # 5. SYSTEM-MONITORING
            await self.system_monitor.log_broadcast_creation(
                broadcast_id=broadcast_script["session_id"],
                metrics={
                    "news_count": len(processed_content["selected_news"]),
                    "duration_minutes": broadcast_script["estimated_duration_minutes"],
                    "audio_generated": generate_audio
                }
            )
            
            result = {
                "success": True,
                "broadcast": broadcast_script,
                "audio_files": audio_files,
                "raw_data": data,
                "processed_content": processed_content,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("✅ BROADCAST ERFOLGREICH GENERIERT!")
            logger.info(f"📁 Session ID: {broadcast_script['session_id']}")
            logger.info(f"⏱️ Dauer: {broadcast_script['estimated_duration_minutes']} Min")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Broadcast-Generierung: {e}")
            await self.system_monitor.log_error("broadcast_generation", str(e))
            raise
    
    async def analyze_news_only(
        self, 
        channel: str = "zurich",
        max_age_hours: int = 1
    ) -> Dict[str, Any]:
        """Analysiert nur die News ohne Broadcast-Generierung"""
        
        logger.info("📰 RADIOX MASTER - NEWS-ANALYSE")
        
        raw_data = await self.data_collector.collect_news_data(
            channel=channel,
            max_age_hours=max_age_hours
        )
        
        analysis = await self.content_processor.analyze_news(raw_data["news"])
        
        return {
            "success": True,
            "news_analysis": analysis,
            "raw_news": raw_data["news"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def test_all_services(self) -> Dict[str, Any]:
        """Testet alle Services auf Funktionalität"""
        
        logger.info("🔧 RADIOX MASTER - SERVICE-TESTS")
        
        results = {}
        
        # Test Data Collection
        try:
            await self.data_collector.test_connections()
            results["data_collection"] = "✅ OK"
        except Exception as e:
            results["data_collection"] = f"❌ FEHLER: {e}"
        
        # Test Content Processing
        try:
            await self.content_processor.test_processing()
            results["content_processing"] = "✅ OK"
        except Exception as e:
            results["content_processing"] = f"❌ FEHLER: {e}"
        
        # Test Broadcast Generation
        try:
            await self.broadcast_generator.test_generation()
            results["broadcast_generation"] = "✅ OK"
        except Exception as e:
            results["broadcast_generation"] = f"❌ FEHLER: {e}"
        
        # Test Audio Generation
        try:
            await self.audio_generator.test_audio()
            results["audio_generation"] = "✅ OK"
        except Exception as e:
            results["audio_generation"] = f"❌ FEHLER: {e}"
        
        # Test System Monitoring
        try:
            await self.system_monitor.test_monitoring()
            results["system_monitoring"] = "✅ OK"
        except Exception as e:
            results["system_monitoring"] = f"❌ FEHLER: {e}"
        
        return {
            "success": True,
            "service_tests": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Holt den aktuellen System-Status"""
        
        status_data = await self.system_monitor.get_system_status()
        
        # Erweitere um success und timestamp für einheitliche API
        return {
            "success": True,
            "system_status": status_data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup_old_data(self, days_old: int = 7) -> Dict[str, Any]:
        """Räumt alte Daten auf"""
        
        logger.info(f"🧹 RADIOX MASTER - CLEANUP (älter als {days_old} Tage)")
        
        cleanup_results = await self.system_monitor.cleanup_old_data(days_old)
        
        return {
            "success": True,
            "cleanup_results": cleanup_results,
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Hauptfunktion mit CLI-Interface"""
    
    parser = argparse.ArgumentParser(description="RadioX Master Control Script")
    
    parser.add_argument(
        "--action", 
        choices=[
            "generate_broadcast", 
            "analyze_news", 
            "test_services", 
            "system_status", 
            "cleanup"
        ],
        required=True,
        help="Aktion die ausgeführt werden soll"
    )
    
    parser.add_argument("--time", help="Zielzeit für Broadcast (HH:MM)")
    parser.add_argument("--channel", default="zurich", help="Radio-Kanal")
    parser.add_argument("--language", choices=["de", "en"], default="en", help="Language: English (en) or German (de)")
    parser.add_argument("--news-count", type=int, default=4, help="Anzahl News")
    parser.add_argument("--max-age", type=int, default=6, help="Max. News-Alter (Stunden)")
    parser.add_argument("--generate-audio", action="store_true", help="Audio generieren")
    parser.add_argument("--cleanup-days", type=int, default=7, help="Cleanup-Alter (Tage)")
    
    args = parser.parse_args()
    
    # Setup Logging
    logger.add(
        "logs/radiox_master_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    master = RadioXMaster()
    
    try:
        if args.action == "generate_broadcast":
            result = await master.generate_complete_broadcast(
                target_time=args.time,
                channel=args.channel,
                news_count=args.news_count,
                max_news_age=args.max_age,
                generate_audio=args.generate_audio,
                language=args.language
            )
            
        elif args.action == "analyze_news":
            result = await master.analyze_news_only(
                channel=args.channel,
                max_age_hours=args.max_age
            )
            
        elif args.action == "test_services":
            result = await master.test_all_services()
            
        elif args.action == "system_status":
            result = await master.get_system_status()
            
        elif args.action == "cleanup":
            result = await master.cleanup_old_data(args.cleanup_days)
        
        # Ausgabe der Ergebnisse
        print("\n" + "="*60)
        print("RADIOX MASTER - ERGEBNIS")
        print("="*60)
        
        if result["success"]:
            print("✅ ERFOLGREICH")
        else:
            print("❌ FEHLER")
        
        # Spezifische Ausgaben je nach Aktion
        if args.action == "generate_broadcast" and result["success"]:
            broadcast = result["broadcast"]
            print(f"📁 Session ID: {broadcast['session_id']}")
            print(f"🎭 Stil: {broadcast['broadcast_style']}")
            print(f"⏱️ Dauer: {broadcast['estimated_duration_minutes']} Minuten")
            print(f"📰 News: {len(result['processed_content']['selected_news'])}")
            
        elif args.action == "test_services":
            print("\nSERVICE-STATUS:")
            for service, status in result["service_tests"].items():
                print(f"  {service}: {status}")
        
        elif args.action == "system_status":
            print("\nSYSTEM-STATUS:")
            status = result["system_status"]
            print(f"  Health Score: {status.get('health_score', 0):.2f}")
            print(f"  Status: {status.get('status', 'unknown')}")
            if status.get('alerts'):
                print(f"  Alerts: {len(status['alerts'])}")
        
        print(f"\n⏰ Zeitstempel: {result['timestamp']}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler: {e}")
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 