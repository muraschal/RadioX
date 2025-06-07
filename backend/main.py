#!/usr/bin/env python3

"""
RadioX Master - CLEAN ARCHITECTURE
===================================

Maximale Orchestrierung mit klarer Separation of Concerns.
Nur zwei Hauptschritte: data_collection → data_processing

DESIGN PRINCIPLES:
- Clean Architecture (Layered Design)
- Domain-Driven Design (Service Organization)
- Single Responsibility (Each function has one job)
- Separation of Concerns (Clear boundaries)

USAGE:
python main.py                    # Vollständiger Workflow
python main.py --data-only        # Nur Datensammlung
python main.py --processing-only  # Nur Verarbeitung
python main.py --test             # System Tests
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for clean imports
sys.path.append(str(Path(__file__).parent / "src"))

# Clean Architecture Imports - Domain-driven
from services.data import DataCollectionService
from services.processing import ContentProcessingService


class RadioXMaster:
    """
    RadioX Master - Clean Architecture
    
    Orchestriert den kompletten RadioX Workflow mit maximaler
    Separation of Concerns und Clean Architecture Prinzipien.
    
    ARCHITECTURE:
    ┌─────────────────┐
    │  Orchestration  │  ← RadioX Master (this class)
    ├─────────────────┤
    │   Processing    │  ← Content Processing Layer (inkl. Show Service)
    ├─────────────────┤
    │      Data       │  ← Data Collection Layer
    └─────────────────┘
    """
    
    def __init__(self):
        """Initialize with dependency injection pattern"""
        
        # Data Layer
        self.data_collector = DataCollectionService()
        
        # Processing Layer (Show Service ist hier integriert)
        self.content_processor = ContentProcessingService()
        
        # Configuration
        self.config = {
            "workflow_version": "2.1.0",
            "architecture": "clean_layered_with_shows",
            "max_news_count": 4,
            "default_max_age_hours": 12,  # Erhöht für bessere News-Sammlung
            "supported_presets": ["zurich", "crypto", "tech", "geopolitik", "news"],
            "quality_threshold": 0.7
        }
        
        print("🚀 RadioX Master Architecture initialized")
        print(f"📋 Version: {self.config['workflow_version']}")
        print(f"🏗️ Architecture: {self.config['architecture']}")
        print(f"🎭 Show Service: Integrated in Processing Layer")
    
    async def run_complete_workflow(
        self,
        preset_name: Optional[str] = None,
        max_age_hours: int = 12,  # Erhöht für bessere News-Sammlung
        target_news_count: int = 4,
        target_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Führt den kompletten RadioX Workflow aus
        
        WORKFLOW:
        1. Show Configuration (Show-Preset laden)
        2. Data Collection (alle Datenquellen)
        3. Data Processing (intelligente Verarbeitung)
        
        Args:
            preset_name: Show Preset (zurich, crypto, tech, etc.)
            max_age_hours: Maximales Alter der News
            target_news_count: Gewünschte Anzahl News
            target_time: Zielzeit für zeitspezifische Optimierung
            
        Returns:
            Dict mit allen Workflow-Ergebnissen
        """
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("🎙️ RADIOX MASTER - COMPLETE WORKFLOW")
        print("=" * 60)
        print(f"🆔 Workflow ID: {workflow_id}")
        print(f"🎯 Preset: {preset_name or 'default'}")
        print(f"📰 Target News: {target_news_count}")
        print(f"⏰ Max Age: {max_age_hours}h")
        print(f"🕐 Target Time: {target_time or 'current'}")
        
        try:
            # STEP 1: SHOW CONFIGURATION
            print("🎭 STEP 1/3: SHOW CONFIGURATION")
            print("-" * 40)
            
            show_config = await self.run_show_configuration(preset_name)
            
            if not show_config or not show_config.get("success"):
                raise Exception("Show configuration failed")
            
            print("✅ Show Configuration completed successfully")
            
            # STEP 2: DATA COLLECTION
            print("📊 STEP 2/3: DATA COLLECTION")
            print("-" * 40)
            
            collected_data = await self.run_data_collection(
                preset_name=preset_name,
                max_age_hours=max_age_hours
            )
            
            if not collected_data or not collected_data.get("success"):
                raise Exception("Data collection failed")
            
            print("✅ Data Collection completed successfully")
            
            # STEP 3: DATA PROCESSING
            print("🔄 STEP 3/3: DATA PROCESSING")
            print("-" * 40)
            
            processed_data = await self.run_data_processing(
                raw_data=collected_data["data"],
                target_news_count=target_news_count,
                target_time=target_time,
                preset_name=preset_name,
                show_config=show_config["data"]  # Show-Konfiguration weitergeben
            )
            
            if not processed_data or not processed_data.get("success"):
                raise Exception("Data processing failed")
            
            print("✅ Data Processing completed successfully")
            
            # Combine results
            workflow_result = {
                "success": True,
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "preset_name": preset_name,
                    "target_news_count": target_news_count,
                    "max_age_hours": max_age_hours,
                    "target_time": target_time
                },
                "show_configuration": show_config,
                "data_collection": collected_data,
                "data_processing": processed_data,
                "quality_metrics": self._calculate_workflow_quality(
                    collected_data, processed_data
                )
            }
            
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print(f"🎭 Show: {show_config['data']['show']['display_name']}")
            print(f"🎤 Speaker: {show_config['data']['speaker']['voice_name']}")
            print(f"📊 Quality Score: {workflow_result['quality_metrics']['overall_score']:.2f}")
            print(f"📰 News Selected: {len(processed_data['data']['selected_news'])}")
            
            return workflow_result
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_data_collection(
        self,
        preset_name: Optional[str] = None,
        max_age_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Führt nur die Datensammlung aus (Step 1)
        
        SINGLE RESPONSIBILITY: Nur Datensammlung, keine Verarbeitung
        
        Args:
            preset_name: Show Preset für fokussierte Sammlung
            max_age_hours: Maximales Alter der News
            
        Returns:
            Dict mit gesammelten Rohdaten
        """
        
        print("📡 Starting Data Collection...")
        
        try:
            # Delegate to Data Layer
            raw_data = await self.data_collector.collect_all_data(
                max_age_hours=max_age_hours
            )
            
            # Validate data quality
            data_quality = self._validate_collected_data(raw_data)
            
            result = {
                "success": True,
                "data": raw_data,
                "quality_metrics": data_quality,
                "collection_timestamp": datetime.now().isoformat(),
                "preset_used": preset_name,
                "max_age_hours": max_age_hours
            }
            
            print(f"📊 Data Collection Quality: {data_quality['score']:.2f}")
            print(f"📰 News Collected: {data_quality['news_count']}")
            print(f"🔗 Sources Active: {data_quality['active_sources']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Data Collection Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_data_processing(
        self,
        raw_data: Dict[str, Any],
        target_news_count: int = 4,
        target_time: Optional[str] = None,
        preset_name: Optional[str] = None,
        show_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Führt nur die Datenverarbeitung aus (Step 2)
        
        SINGLE RESPONSIBILITY: Nur Verarbeitung, keine Sammlung
        
        Args:
            raw_data: Rohdaten von der Datensammlung
            target_news_count: Gewünschte Anzahl News
            target_time: Zielzeit für Optimierung
            preset_name: Show Preset für Fokus-Bestimmung
            show_config: Show-Konfiguration
            
        Returns:
            Dict mit verarbeiteten Daten
        """
        
        print("🔄 Starting Data Processing...")
        
        try:
            # Delegate to Processing Layer
            processed_content = await self.content_processor.process_content(
                raw_data=raw_data,
                target_news_count=target_news_count,
                target_time=target_time,
                preset_name=preset_name,
                show_config=show_config
            )
            
            if not processed_content:
                raise Exception("Content processing returned None")
            
            # Validate processing quality
            processing_quality = self._validate_processed_data(processed_content)
            
            result = {
                "success": True,
                "data": processed_content,
                "quality_metrics": processing_quality,
                "processing_timestamp": datetime.now().isoformat(),
                "target_news_count": target_news_count,
                "preset_used": preset_name
            }
            
            print(f"🔄 Processing Quality: {processing_quality['score']:.2f}")
            print(f"📰 News Selected: {len(processed_content['selected_news'])}")
            print(f"🎯 Content Focus: {processed_content.get('content_focus', {}).get('focus', 'unknown')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Data Processing Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_system(self) -> Dict[str, Any]:
        """
        Testet alle System-Komponenten
        
        SEPARATION OF CONCERNS: Jede Schicht wird isoliert getestet
        
        Returns:
            Dict mit Test-Ergebnissen
        """
        
        print("🧪 SYSTEM TESTS")
        print("=" * 50)
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "architecture": "clean_layered",
            "tests": {}
        }
        
        # Test Data Layer
        print("📊 Testing Data Layer...")
        try:
            data_test = await self.data_collector.test_connections()
            all_passed = all(data_test.values()) if data_test else False
            test_results["tests"]["data_layer"] = {
                "status": "✅ PASS" if all_passed else "❌ FAIL",
                "details": data_test
            }
            print(f"   Data Layer: {'✅ PASS' if all_passed else '❌ FAIL'}")
        except Exception as e:
            test_results["tests"]["data_layer"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"   Data Layer: ❌ FAIL - {e}")
        
        # Test Processing Layer
        print("🔄 Testing Processing Layer...")
        try:
            processing_test = await self.content_processor.test_processing()
            test_results["tests"]["processing_layer"] = {
                "status": "✅ PASS" if processing_test else "❌ FAIL",
                "details": "Content processing service"
            }
            print(f"   Processing Layer: {'✅ PASS' if processing_test else '❌ FAIL'}")
        except Exception as e:
            test_results["tests"]["processing_layer"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"   Processing Layer: ❌ FAIL - {e}")
        
        # Calculate overall success
        passed_tests = sum(1 for test in test_results["tests"].values() if "✅ PASS" in test["status"])
        total_tests = len(test_results["tests"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "overall_status": "✅ HEALTHY" if success_rate >= 75 else "⚠️ ISSUES" if success_rate >= 50 else "❌ CRITICAL"
        }
        
        print(f"📊 Test Summary: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        print(f"🎯 System Status: {test_results['summary']['overall_status']}")
        
        return test_results
    
    async def run_show_configuration(
        self,
        preset_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lädt die Show-Konfiguration (Step 0)
        
        SINGLE RESPONSIBILITY: Nur Show-Konfiguration laden
        
        Args:
            preset_name: Show Preset (zurich, crypto, tech, etc.)
            
        Returns:
            Dict mit Show-Konfiguration
        """
        
        print("🎭 Loading Show Configuration...")
        
        try:
            # Fallback auf default preset wenn keines angegeben
            if not preset_name:
                preset_name = "zurich"  # Default Show
                print(f"🎯 No preset specified, using default: {preset_name}")
            
            # Delegate to Processing Layer (Show Service ist dort integriert)
            show_config = await self.content_processor.get_show_configuration(preset_name)
            
            if not show_config:
                raise Exception(f"Show configuration for '{preset_name}' not found")
            
            result = {
                "success": True,
                "data": show_config,
                "preset_name": preset_name,
                "configuration_timestamp": datetime.now().isoformat()
            }
            
            print(f"🎭 Show: {show_config['show']['display_name']}")
            print(f"🎤 Speaker: {show_config['speaker']['voice_name']}")
            print(f"🏙️ Focus: {show_config['show']['city_focus']}")
            print(f"📰 Categories: {', '.join(show_config['content']['categories'][:3])}...")
            
            return result
            
        except Exception as e:
            print(f"❌ Show Configuration Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "preset_name": preset_name,
                "timestamp": datetime.now().isoformat()
            }
    
    # ==================== PRIVATE VALIDATION METHODS ====================
    
    def _validate_collected_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert die Qualität der gesammelten Daten"""
        
        if not raw_data:
            return {"score": 0.0, "news_count": 0, "active_sources": 0}
        
        # Count news - neue DataCollectionService Format
        news_count = 0
        if "news" in raw_data and raw_data["news"]:
            news_count = len(raw_data["news"])
        
        # Count active sources - neue DataCollectionService Format
        active_sources = 0
        if raw_data.get("weather"):
            active_sources += 1
        if raw_data.get("crypto"):
            active_sources += 1
        if raw_data.get("news"):
            active_sources += 1
        
        # Calculate quality score
        score = 0.0
        if news_count > 0:
            score += min(0.6, news_count / 50)  # Max 0.6 for news (up to 50 news)
        if active_sources > 0:
            score += min(0.4, active_sources / 3)  # Max 0.4 for sources (up to 3 sources)
        
        return {
            "score": round(score, 2),
            "news_count": news_count,
            "active_sources": active_sources,
            "quality_level": "excellent" if score >= 0.8 else "good" if score >= 0.6 else "fair" if score >= 0.4 else "poor"
        }
    
    def _validate_processed_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert die Qualität der verarbeiteten Daten"""
        
        if not processed_data:
            return {"score": 0.0, "selected_news": 0, "content_focus": "unknown"}
        
        selected_news = processed_data.get("selected_news", [])
        content_focus = processed_data.get("content_focus", {}).get("focus", "unknown")
        quality_score = processed_data.get("quality_score", 0.0)
        
        # Normalize quality score to 0-1 range
        normalized_score = min(1.0, quality_score / 100) if quality_score > 1 else quality_score
        
        return {
            "score": round(normalized_score, 2),
            "selected_news": len(selected_news),
            "content_focus": content_focus,
            "quality_level": "excellent" if normalized_score >= 0.8 else "good" if normalized_score >= 0.6 else "fair" if normalized_score >= 0.4 else "poor"
        }
    
    def _calculate_workflow_quality(
        self, 
        collection_result: Dict[str, Any], 
        processing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Berechnet die Gesamtqualität des Workflows"""
        
        collection_quality = collection_result.get("quality_metrics", {}).get("score", 0.0)
        processing_quality = processing_result.get("quality_metrics", {}).get("score", 0.0)
        
        # Weighted average (Collection 40%, Processing 60%)
        overall_score = (collection_quality * 0.4) + (processing_quality * 0.6)
        
        return {
            "overall_score": round(overall_score, 2),
            "collection_score": collection_quality,
            "processing_score": processing_quality,
            "quality_level": "excellent" if overall_score >= 0.8 else "good" if overall_score >= 0.6 else "fair" if overall_score >= 0.4 else "poor"
        }


async def main():
    """
    Main CLI function mit Clean Architecture
    """
    
    parser = argparse.ArgumentParser(
        description="RadioX Master - Clean Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python main.py                           # Vollständiger Workflow
  python main.py --preset zurich           # Zürich Show
  python main.py --data-only               # Nur Datensammlung
  python main.py --processing-only         # Nur Verarbeitung (benötigt --data-file)
  python main.py --test                    # System Tests
  python main.py --preset crypto --news 6  # Bitcoin Show mit 6 News

ARCHITECTURE:
  Clean Layered Architecture mit Domain-driven Design
  Maximale Separation of Concerns und Testability
        """
    )
    
    # Workflow Options
    parser.add_argument("--preset", type=str, help="Show Preset (zurich, crypto, tech, geopolitik, news)")
    parser.add_argument("--news", type=int, default=4, help="Anzahl News (default: 4)")
    parser.add_argument("--max-age", type=int, default=1, help="Max Age in Stunden (default: 1)")
    parser.add_argument("--time", type=str, help="Zielzeit (HH:MM)")
    
    # Single Step Options
    parser.add_argument("--data-only", action="store_true", help="Nur Datensammlung")
    parser.add_argument("--processing-only", action="store_true", help="Nur Verarbeitung")
    parser.add_argument("--data-file", type=str, help="Datei mit Rohdaten für --processing-only")
    
    # System Options
    parser.add_argument("--test", action="store_true", help="System Tests")
    
    args = parser.parse_args()
    
    # Initialize Master
    try:
        master = RadioXMaster()
    except Exception as e:
        print(f"❌ Failed to initialize RadioX Master: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    try:
        if args.test:
            # System Tests
            result = await master.test_system()
            
        elif args.data_only:
            # Nur Datensammlung
            result = await master.run_data_collection(
                preset_name=args.preset,
                max_age_hours=args.max_age
            )
            
        elif args.processing_only:
            # Nur Verarbeitung
            if not args.data_file:
                print("❌ --processing-only benötigt --data-file")
                sys.exit(1)
            
            # TODO: Load data from file
            print("❌ --data-file loading not implemented yet")
            sys.exit(1)
            
        else:
            # Vollständiger Workflow
            result = await master.run_complete_workflow(
                preset_name=args.preset,
                max_age_hours=args.max_age,
                target_news_count=args.news,
                target_time=args.time
            )
        
        # Output results
        if result.get("success"):
            print("🎉 RadioX Master completed successfully!")
            if "quality_metrics" in result:
                quality = result["quality_metrics"]
                print(f"📊 Overall Quality: {quality.get('overall_score', 'N/A')}")
        else:
            print("❌ RadioX Master failed!")
            if "error" in result:
                print(f"Error: {result['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("⚠️ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 