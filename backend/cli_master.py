#!/usr/bin/env python3
"""
RadioX Master CLI
=================

Master CLI für die neue modulare Service-Architektur:
🔊 Audio Generation Service (separat)
🎨 Image Generation Service (separat)  
🔗 Content Combiner Service (Audio + Cover zusammenfügen)
📋 Content Logging Service (News + Script Protokollierung)
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add the src directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent / "src"))

from services.audio_generation_service import AudioGenerationService
from services.image_generation_service import ImageGenerationService
from services.content_combiner_service import ContentCombinerService
from services.content_logging_service import ContentLoggingService
from services.broadcast_generation_service import BroadcastGenerationService
from services.data_collection_service import DataCollectionService
from loguru import logger


async def full_modular_workflow():
    """Vollständiger modularer Workflow: Data → Script → Audio → Cover → Combine → Log"""
    
    logger.info("🚀 === RADIOX MODULARE ARCHITEKTUR WORKFLOW ===")
    
    session_id = f"modular_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    target_time = "15:00"
    
    try:
        # === STEP 1: DATA COLLECTION ===
        logger.info("📡 Step 1/6: Data Collection...")
        data_service = DataCollectionService()
        data_result = await data_service.collect_all_data()
        
        if not data_result.get("success"):
            logger.error("❌ Data collection failed")
            return False
        
        logger.success("✅ Data collection successful")
        collected_news = data_result.get("aggregated_data", {}).get("news", [])
        context_data = data_result.get("aggregated_data", {})
        
        # === STEP 2: BROADCAST SCRIPT GENERATION ===
        logger.info("📝 Step 2/6: Script Generation...")
        broadcast_service = BroadcastGenerationService()
        script_result = await broadcast_service.generate_broadcast(
            session_id=session_id,
            target_time=target_time,
            collected_data=data_result["aggregated_data"]
        )
        
        if not script_result.get("success"):
            logger.error("❌ Script generation failed")
            return False
        
        logger.success("✅ Script generation successful")
        script_content = script_result.get("script_content", "")
        selected_news = script_result.get("broadcast_metadata", {}).get("selected_news", [])
        
        # === STEP 3: AUDIO GENERATION (SEPARAT) ===
        logger.info("🔊 Step 3/6: Audio Generation...")
        audio_service = AudioGenerationService()
        audio_result = await audio_service.generate_audio({
            "session_id": session_id,
            "script_content": script_content
        })
        
        if not audio_result.get("success"):
            logger.error("❌ Audio generation failed")
            return False
        
        logger.success("✅ Audio generation successful")
        
        # === STEP 4: COVER GENERATION (SEPARAT) ===
        logger.info("🎨 Step 4/6: Cover Art Generation...")
        image_service = ImageGenerationService()
        cover_result = await image_service.generate_cover_art(
            session_id=session_id,
            broadcast_content={
                "selected_news": selected_news,
                "context_data": context_data
            },
            target_time=target_time
        )
        
        if not cover_result.get("success"):
            logger.warning("⚠️ Cover generation failed, continuing without cover")
        else:
            logger.success("✅ Cover generation successful")
        
        # === STEP 5: AUDIO + COVER COMBINATION ===
        logger.info("🔗 Step 5/6: Audio + Cover Combination...")
        combiner_service = ContentCombinerService()
        final_result = await combiner_service.combine_audio_and_cover(
            session_id=session_id,
            audio_result=audio_result,
            cover_result=cover_result,
            broadcast_metadata={
                "session_id": session_id,
                "target_time": target_time,
                "selected_news": selected_news,
                "context_data": context_data
            }
        )
        
        if not final_result.get("success"):
            logger.error("❌ Audio + Cover combination failed")
            return False
        
        logger.success("✅ Audio + Cover combination successful")
        
        # === STEP 6: CONTENT LOGGING ===
        logger.info("📋 Step 6/6: Content Logging...")
        logging_service = ContentLoggingService()
        
        # Log ALL collected news
        news_log_result = await logging_service.log_collected_news(
            session_id=session_id,
            collected_news=collected_news,
            selected_news=selected_news,
            collection_metadata={
                "target_time": target_time,
                "collection_timestamp": datetime.now().isoformat(),
                "total_sources": len(data_result.get("source_details", {}))
            }
        )
        
        # Log final script
        script_log_result = await logging_service.log_final_script(
            session_id=session_id,
            script_content=script_content,
            script_metadata={
                "target_time": target_time,
                "voice_config": {"marcel": "Rachel", "jarvis": "Bella"},
                "context_data": context_data
            }
        )
        
        if news_log_result.get("success") and script_log_result.get("success"):
            logger.success("✅ Content logging successful")
        else:
            logger.warning("⚠️ Content logging partially failed")
        
        # === FINAL SUMMARY ===
        logger.info("\n🎉 === MODULAR WORKFLOW COMPLETE ===")
        logger.info(f"📁 Session ID: {session_id}")
        logger.info(f"🔊 Final Audio: {final_result.get('final_audio_filename')}")
        logger.info(f"🎨 Cover Embedded: {final_result.get('cover_embedded')}")
        logger.info(f"📊 Quality Rating: {final_result.get('quality_check', {}).get('quality_rating')}")
        logger.info(f"📋 News Logged: {news_log_result.get('total_news_logged', 0)}")
        logger.info(f"📝 Script Logged: {'Yes' if script_log_result.get('success') else 'No'}")
        logger.info(f"⏱️ Total Duration: {audio_result.get('duration_seconds', 0)}s")
        logger.info(f"📏 File Size: {final_result.get('file_size_mb', 0)} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Modular Workflow Error: {e}")
        return False


async def test_all_services():
    """Teste alle Services einzeln"""
    
    logger.info("🧪 === TESTING ALL SERVICES ===")
    
    test_results = {}
    
    # Test Audio Service
    logger.info("🔊 Testing Audio Generation Service...")
    try:
        audio_service = AudioGenerationService()
        test_results["audio"] = await audio_service.test_audio()
    except Exception as e:
        logger.error(f"Audio test error: {e}")
        test_results["audio"] = False
    
    # Test Image Service
    logger.info("🎨 Testing Image Generation Service...")
    try:
        from cli_image import test_image_generation
        test_results["image"] = await test_image_generation()
    except Exception as e:
        logger.error(f"Image test error: {e}")
        test_results["image"] = False
    
    # Test Combiner Service
    logger.info("🔗 Testing Content Combiner Service...")
    try:
        combiner_service = ContentCombinerService()
        test_results["combiner"] = await combiner_service.test_combiner()
    except Exception as e:
        logger.error(f"Combiner test error: {e}")
        test_results["combiner"] = False
    
    # Test Logging Service
    logger.info("📋 Testing Content Logging Service...")
    try:
        logging_service = ContentLoggingService()
        test_results["logging"] = await logging_service.test_content_logging()
    except Exception as e:
        logger.error(f"Logging test error: {e}")
        test_results["logging"] = False
    
    # Test Data Collection Service
    logger.info("📡 Testing Data Collection Service...")
    try:
        data_service = DataCollectionService()
        test_results["data"] = await data_service.test_all_services()
    except Exception as e:
        logger.error(f"Data test error: {e}")
        test_results["data"] = False
    
    # Test Broadcast Generation Service
    logger.info("📝 Testing Broadcast Generation Service...")
    try:
        broadcast_service = BroadcastGenerationService()
        test_results["broadcast"] = await broadcast_service.test_broadcast_generation()
    except Exception as e:
        logger.error(f"Broadcast test error: {e}")
        test_results["broadcast"] = False
    
    # Summary
    successful = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    logger.info("\n📊 === TEST RESULTS SUMMARY ===")
    for service, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{service.capitalize()}: {status}")
    
    logger.info(f"\n🎯 Overall: {successful}/{total} services passed")
    
    return successful == total


async def generate_status_report():
    """Generiere Status-Report der modularen Architektur"""
    
    logger.info("📊 === RADIOX MODULAR ARCHITECTURE STATUS ===")
    
    # Service Status
    services = {
        "🔊 Audio Generation": "Separate V3 English TTS service",
        "🎨 Image Generation": "Separate DALL-E cover art service", 
        "🔗 Content Combiner": "Audio + Cover combination service",
        "📋 Content Logging": "News & Script logging with SQLite",
        "📡 Data Collection": "RSS + Crypto + Weather aggregation",
        "📝 Broadcast Generation": "V3 English script generation"
    }
    
    logger.info("\n🏗️ MODULAR SERVICES:")
    for service, description in services.items():
        logger.info(f"   {service}: {description}")
    
    # Output Directories
    output_dirs = [
        ("🔊 Audio", "output/audio"),
        ("🎨 Covers", "output/covers"), 
        ("🔗 Final", "output/final"),
        ("📋 Logs", "logs/content"),
        ("📊 Reports", "logs/reports")
    ]
    
    logger.info("\n📁 OUTPUT DIRECTORIES:")
    for name, path in output_dirs:
        dir_path = Path(path)
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*")))
            logger.info(f"   {name}: {path} ({file_count} files)")
        else:
            logger.info(f"   {name}: {path} (not created yet)")
    
    # API Keys Status
    from config.settings import get_settings
    settings = get_settings()
    api_keys = {
        "🎤 ElevenLabs": bool(settings.elevenlabs_api_key),
        "🎨 OpenAI": bool(settings.openai_api_key),
        "💰 CoinMarketCap": bool(settings.coinmarketcap_api_key),
        "🌤️ Weather": bool(settings.weather_api_key),
        "🗄️ Supabase": bool(settings.supabase_url)
    }
    
    logger.info("\n🔑 API KEYS STATUS:")
    for service, available in api_keys.items():
        status = "✅ Available" if available else "❌ Missing"
        logger.info(f"   {service}: {status}")
    
    # CLI Scripts
    cli_scripts = [
        "cli_master.py - Master orchestrator",
        "cli_audio.py - Audio generation testing",
        "cli_image.py - Cover art testing", 
        "cli_combiner.py - Audio+Cover combination",
        "cli_logging.py - Content logging testing",
        "cli_broadcast.py - Script generation",
        "cli_crypto.py - Crypto data testing",
        "cli_rss.py - RSS feed testing",
        "cli_overview.py - System overview"
    ]
    
    logger.info("\n⚡ CLI SCRIPTS:")
    for script in cli_scripts:
        logger.info(f"   {script}")
    
    logger.info("\n🎯 ARCHITECTURE: Fully modular, each service separate and testable")
    logger.info("🔄 WORKFLOW: Data → Script → Audio → Cover → Combine → Log")
    logger.info("🌍 LANGUAGE: English V3 by default, German fallback")


async def quick_test_workflow():
    """Schneller Test-Workflow ohne vollständige Datensammlung"""
    
    logger.info("⚡ === QUICK TEST WORKFLOW ===")
    
    session_id = f"quick_{datetime.now().strftime('%H%M%S')}"
    
    try:
        # Mock-Daten für schnellen Test
        mock_script = {
            "session_id": session_id,
            "script_content": """
MARCEL: [excited] Welcome to RadioX quick test!
JARVIS: [analytical] Testing our new modular architecture.
MARCEL: [impressed] This is absolutely incredible technology!
JARVIS: [sarcastic] Well, it's just a test, Marcel.
MARCEL: [laughs] Thanks for listening to RadioX!
            """.strip()
        }
        
        mock_broadcast_content = {
            "selected_news": [{"title": "Test News", "primary_category": "tech"}],
            "context_data": {"crypto": {"formatted": "$100K"}}
        }
        
        # Step 1: Audio
        logger.info("🔊 Generating audio...")
        audio_service = AudioGenerationService()
        audio_result = await audio_service.generate_audio(mock_script)
        
        if not audio_result.get("success"):
            logger.error("❌ Audio failed")
            return False
        
        # Step 2: Cover
        logger.info("🎨 Generating cover...")
        image_service = ImageGenerationService()
        cover_result = await image_service.generate_cover_art(
            session_id, mock_broadcast_content, "15:00"
        )
        
        # Step 3: Combine
        logger.info("🔗 Combining...")
        combiner_service = ContentCombinerService()
        final_result = await combiner_service.combine_audio_and_cover(
            session_id, audio_result, cover_result, {"target_time": "15:00"}
        )
        
        if final_result.get("success"):
            logger.success(f"✅ Quick test successful: {final_result.get('final_audio_filename')}")
            return True
        else:
            logger.error("❌ Quick test failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Quick test error: {e}")
        return False


async def main():
    """Main CLI function"""
    
    logger.info("🚀 RadioX Master CLI - Modular Architecture")
    logger.info("=============================================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "full":
            success = await full_modular_workflow()
            sys.exit(0 if success else 1)
            
        elif command == "test":
            success = await test_all_services()
            sys.exit(0 if success else 1)
            
        elif command == "quick":
            success = await quick_test_workflow()
            sys.exit(0 if success else 1)
            
        elif command == "status":
            await generate_status_report()
            sys.exit(0)
            
        elif command == "help":
            print("""
RadioX Master CLI - Modular Architecture
========================================

python cli_master.py full     - Complete modular workflow
python cli_master.py test     - Test all services
python cli_master.py quick    - Quick test workflow  
python cli_master.py status   - Architecture status report
python cli_master.py help     - Show this help

MODULAR SERVICES:
🔊 Audio Generation (cli_audio.py)
🎨 Image Generation (cli_image.py)
🔗 Content Combiner (cli_combiner.py)
📋 Content Logging (cli_logging.py)

WORKFLOW: Data → Script → Audio → Cover → Combine → Log

Examples:
python cli_master.py full
python cli_master.py test
python cli_master.py status
            """)
            sys.exit(0)
        
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Use 'python cli_master.py help' for available commands")
            sys.exit(1)
    
    else:
        # Default: show status
        await generate_status_report()
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main()) 