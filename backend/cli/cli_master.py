#!/usr/bin/env python3
"""
🚀 RadioX Master CLI - Enterprise Architecture
Orchestriert alle Services für Development & Testing
Inkl. Show Preset Generation für Production
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.data_collection_service import DataCollectionService
from src.services.content_processing_service import ContentProcessingService
from src.services.broadcast_generation_service import BroadcastGenerationService
from src.services.audio_generation_service import AudioGenerationService
from src.services.image_generation_service import ImageGenerationService
from src.services.content_combiner_service import ContentCombinerService
from src.services.content_logging_service import ContentLoggingService
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
        "📋 Content Logging": "News & Script logging with Supabase",
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
    
    # API Keys Status mit verbesserter Validierung
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        # Verbesserte API Key Validierung
        def validate_api_key(key, key_type="generic"):
            if not key:
                return "❌ Missing"
            if key.startswith("your_") or key.endswith("_here"):
                return "⚠️ Template Value"
            if key_type == "openai" and not key.startswith("sk-"):
                return "⚠️ Invalid Format"
            if key_type == "supabase_url" and not (key.startswith("https://") and "supabase" in key):
                return "⚠️ Invalid Format"
            return "✅ Valid"
        
        api_keys = {
            "🎤 ElevenLabs": validate_api_key(settings.elevenlabs_api_key),
            "🎨 OpenAI": validate_api_key(settings.openai_api_key, "openai"),
            "💰 CoinMarketCap": validate_api_key(settings.coinmarketcap_api_key),
            "🌤️ Weather": validate_api_key(settings.weather_api_key),
            "🗄️ Supabase URL": validate_api_key(settings.supabase_url, "supabase_url"),
            "🗄️ Supabase Key": validate_api_key(settings.supabase_anon_key)
        }
        
        logger.info("\n🔑 API KEYS STATUS:")
        valid_count = 0
        total_count = len(api_keys)
        
        for service, status in api_keys.items():
            logger.info(f"   {service}: {status}")
            if status == "✅ Valid":
                valid_count += 1
        
        logger.info(f"\n📊 API Keys Summary: {valid_count}/{total_count} properly configured")
        
        if valid_count == 0:
            logger.warning("⚠️ No API keys configured - please edit .env file")
        elif valid_count < 6:
            logger.warning("⚠️ Some required API keys missing - limited functionality")
        else:
            logger.success("✅ All required API keys configured")
            
    except Exception as e:
        logger.error(f"❌ Error loading settings: {e}")
        logger.info("💡 Make sure .env file exists and is properly formatted")
    
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
    
    # Environment Check
    logger.info("\n🔧 ENVIRONMENT:")
    env_file = Path("../.env")
    if env_file.exists():
        logger.info(f"   📄 .env file: ✅ Found ({env_file.stat().st_size} bytes)")
    else:
        logger.warning("   📄 .env file: ❌ Missing")
    
    # Dependencies Check
    logger.info("\n📦 DEPENDENCIES:")
    try:
        import openai
        logger.info("   🤖 OpenAI: ✅ Installed")
    except ImportError:
        logger.error("   🤖 OpenAI: ❌ Missing")
    
    try:
        import requests
        logger.info("   🌐 Requests: ✅ Installed")
    except ImportError:
        logger.error("   🌐 Requests: ❌ Missing")
    
    try:
        import eyed3
        logger.info("   🎵 eyed3: ✅ Installed")
    except ImportError:
        logger.warning("   🎵 eyed3: ⚠️ Missing (Cover embedding disabled)")
    
    # System Tools Check
    logger.info("\n🔧 SYSTEM TOOLS:")
    
    # ffmpeg Check
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("   🎵 ffmpeg: ✅ Installiert")
        else:
            logger.warning("   🎵 ffmpeg: ❌ Fehler beim Ausführen")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        logger.warning("   🎵 ffmpeg: ❌ Nicht installiert (Audio-Fallback aktiv)")
        logger.info("      📥 Download: https://www.gyan.dev/ffmpeg/builds/")
    
    # Python Version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 11):
        logger.info(f"   🐍 Python: ✅ {python_version}")
    else:
        logger.warning(f"   🐍 Python: ⚠️ {python_version} (empfohlen: 3.11+)")
    
    logger.info("\n🎯 ARCHITECTURE: Fully modular, each service separate and testable")
    logger.info("🔄 WORKFLOW: Data → Script → Audio → Cover → Combine → Log")
    logger.info("🌍 LANGUAGE: English V3 by default, German fallback")
    
    # Next Steps
    logger.info("\n📋 NEXT STEPS:")
    # Initialize valid_count to 0 since API key validation was skipped due to error
    valid_count = 0
    
    if valid_count == 0:
        logger.info("   1. Edit .env file and add your API keys")
        logger.info("   2. Run 'python cli/cli_master.py status' again")
        logger.info("   3. Test with 'python cli/cli_master.py test'")
    elif valid_count < 6:
        logger.info("   1. Complete missing API keys in .env")
        logger.info("   2. Test with 'python cli/cli_master.py test'")
    else:
        logger.info("   1. Test services: 'python cli/cli_master.py test'")
        logger.info("   2. Quick test: 'python cli/cli_master.py quick'")
        logger.info("   3. Full workflow: 'python cli/cli_master.py full'")


async def generate_show_preset(preset_name: str, duration_minutes: int, output_files: bool = False, target_time: str = None):
    """Generiert Show basierend auf Preset - PRODUCTION READY"""
    
    logger.info(f"🎭 === SHOW GENERATION: {preset_name.upper()} ({duration_minutes}min) ===")
    
    # Preset Mappings
    preset_mappings = {
        "zurich": "zurich",
        "tech": "tech", 
        "bitcoin": "crypto",
        "crypto": "crypto",
        "geopolitik": "geopolitik",
        "news": "news"
    }
    
    # Duration Mappings
    duration_mappings = {
        "short": 1, "s": 1,
        "mid": 2, "m": 2, "medium": 2,
        "long": 3, "l": 3
    }
    
    # Validierung
    if preset_name not in preset_mappings:
        logger.error(f"❌ Unbekanntes Preset: {preset_name}")
        logger.info(f"Verfügbare Presets: {list(preset_mappings.keys())}")
        return False
    
    actual_preset = preset_mappings[preset_name]
    session_id = f"show_{actual_preset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # === STEP 1: DATA COLLECTION ===
        logger.info("📡 Step 1/4: Datensammlung...")
        data_service = DataCollectionService()
        
        max_news_age_hours = min(12, max(6, duration_minutes * 3))
        data = await data_service.collect_all_data_for_preset(
            preset_name=actual_preset,
            max_news_age_hours=max_news_age_hours
        )
        
        logger.success(f"✅ {len(data['news'])} News gesammelt")
        
        # === STEP 2: CONTENT PROCESSING ===
        logger.info("🔄 Step 2/4: Content Processing...")
        content_service = ContentProcessingService()
        
        target_news_count = max(3, min(8, duration_minutes * 2))
        processed_content = await content_service.process_content(
            raw_data=data,
            target_news_count=target_news_count,
            target_time=target_time,
            preset_name=actual_preset
        )
        
        logger.success(f"✅ {len(processed_content.get('selected_news', []))} News ausgewählt")
        
        # === STEP 3: BROADCAST GENERATION ===
        logger.info("📝 Step 3/4: Script Generation...")
        broadcast_service = BroadcastGenerationService()
        
        broadcast_result = await broadcast_service.generate_broadcast(
            content=processed_content,
            target_time=target_time,
            channel="zurich",
            language="en"
        )
        
        if not broadcast_result.get('success'):
            logger.error("❌ Script-Generierung fehlgeschlagen")
            return False
        
        script_content = broadcast_result.get('script_content', '')
        logger.success(f"✅ Script generiert: {len(script_content)} Zeichen")
        
        # === STEP 4: AUDIO & HTML GENERATION (optional) ===
        if output_files:
            logger.info("🔊 Step 4/4: Audio & HTML Generation...")
            
            # Direkte ElevenLabs Integration
            success = await _generate_audio_direct(script_content, session_id)
            if success:
                logger.success("✅ Audio und HTML erfolgreich generiert")
            else:
                logger.error("❌ Audio-Generierung fehlgeschlagen")
                return False
        
        # === SUMMARY ===
        logger.info("\n🎉 === SHOW GENERATION COMPLETE ===")
        logger.info(f"📁 Session ID: {session_id}")
        logger.info(f"🎭 Preset: {actual_preset}")
        logger.info(f"⏱️ Duration: {duration_minutes} min")
        logger.info(f"📝 Script: {len(script_content)} Zeichen")
        logger.info(f"🎯 Focus: {processed_content.get('content_focus', {}).get('primary_focus', 'unknown')}")
        if output_files:
            logger.info(f"📁 Output: backend/output/")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Show Generation Fehler: {e}")
        return False


async def _generate_audio_direct(script_content: str, session_id: str) -> bool:
    """Direkte Audio-Generierung mit ElevenLabs"""
    
    try:
        import requests
        from pathlib import Path
        from config.settings import get_settings
        
        settings = get_settings()
        api_key = settings.elevenlabs_api_key
        
        if not api_key:
            logger.error("❌ ElevenLabs API Key fehlt")
            return False
        
        # Marcel Voice
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json", 
            "xi-api-key": api_key
        }
        
        data = {
            "text": script_content,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=120)
        
        if response.status_code == 200:
            # Output-Verzeichnis
            output_path = Path("output")
            output_path.mkdir(exist_ok=True)
            
            # MP3 speichern
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mp3_file = output_path / f"radiox_show_{timestamp}.mp3"
            
            with open(mp3_file, 'wb') as f:
                f.write(response.content)
            
            # HTML Report
            html_file = output_path / f"radiox_show_{timestamp}.html"
            _create_html_report(script_content, mp3_file, html_file)
            
            logger.info(f"🎵 MP3: {mp3_file}")
            logger.info(f"📄 HTML: {html_file}")
            
            return True
        else:
            logger.error(f"❌ ElevenLabs Fehler: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Audio-Generierung Fehler: {e}")
        return False


def _create_html_report(script_content: str, mp3_file: Path, html_file: Path):
    """Erstellt HTML Report"""
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>RadioX Show Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #1a1a1a; color: white; padding: 20px; border-radius: 8px; }}
        .script {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .audio {{ background: #e8f5e8; padding: 20px; border-radius: 8px; }}
        pre {{ white-space: pre-wrap; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📻 RadioX Show Report</h1>
        <p>Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="audio">
        <h2>🎵 Audio</h2>
        <audio controls style="width: 100%;">
            <source src="{mp3_file.name}" type="audio/mpeg">
            Dein Browser unterstützt kein Audio.
        </audio>
        <p><strong>Datei:</strong> {mp3_file.name}</p>
    </div>
    
    <div class="script">
        <h2>📝 Script</h2>
        <pre>{script_content}</pre>
    </div>
</body>
</html>"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


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
        
        # === EXISTING COMMANDS ===
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
        
        # === NEW SHOW COMMANDS ===
        elif command == "show":
            # Parse show arguments: show <preset> <duration> [--output] [--time HH:MM]
            if len(sys.argv) < 4:
                logger.error("❌ Usage: python cli_master.py show <preset> <duration> [--output] [--time HH:MM]")
                logger.info("Beispiel: python cli_master.py show zurich short --output")
                sys.exit(1)
            
            preset_name = sys.argv[2].lower()
            duration_arg = sys.argv[3].lower()
            
            # Duration mapping
            duration_map = {"short": 1, "s": 1, "mid": 2, "m": 2, "medium": 2, "long": 3, "l": 3}
            duration_minutes = duration_map.get(duration_arg)
            
            if not duration_minutes:
                logger.error(f"❌ Unbekannte Duration: {duration_arg}")
                logger.info(f"Verfügbare Durations: {list(duration_map.keys())}")
                sys.exit(1)
            
            # Parse optional arguments
            output_files = "--output" in sys.argv
            target_time = None
            
            if "--time" in sys.argv:
                try:
                    time_index = sys.argv.index("--time") + 1
                    target_time = sys.argv[time_index]
                except (IndexError, ValueError):
                    logger.error("❌ --time benötigt Format HH:MM")
                    sys.exit(1)
            
            success = await generate_show_preset(preset_name, duration_minutes, output_files, target_time)
            sys.exit(0 if success else 1)
            
        elif command == "help":
            print("""
RadioX Master CLI - Modular Architecture
========================================

DEVELOPMENT COMMANDS:
python cli_master.py full     - Complete modular workflow
python cli_master.py test     - Test all services
python cli_master.py quick    - Quick test workflow  
python cli_master.py status   - Architecture status report

PRODUCTION COMMANDS:
python cli_master.py show <preset> <duration> [--output] [--time HH:MM]

SHOW PRESETS:
zurich, tech, bitcoin/crypto, geopolitik, news

DURATIONS:
short/s (1min), mid/m (2min), long/l (3min)

EXAMPLES:
python cli_master.py show zurich short --output
python cli_master.py show tech mid --time 16:15
python cli_master.py show bitcoin long --output --time 16:15
python cli_master.py show news short

MODULAR SERVICES:
🔊 Audio Generation (cli_audio.py)
🎨 Image Generation (cli_image.py)
🔗 Content Combiner (cli_combiner.py)
📋 Content Logging (cli_logging.py)

WORKFLOW: Data → Script → Audio → Cover → Combine → Log
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