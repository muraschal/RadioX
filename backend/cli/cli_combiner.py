#!/usr/bin/env python3
"""
CLI Content Combiner
====================

Standalone CLI für Content Combiner Service Testing
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent / "src"))

from services.content_combiner_service import ContentCombinerService
from loguru import logger


async def test_content_combiner():
    """Test Content Combiner Service"""
    
    logger.info("🔗 === CLI CONTENT COMBINER TEST ===")
    
    try:
        # Initialize service
        combiner_service = ContentCombinerService()
        
        # Mock audio result
        mock_audio_result = {
            "success": True,
            "session_id": "cli_combiner_test",
            "audio_path": "output/audio/test_audio.mp3",
            "duration_seconds": 120,
            "generation_timestamp": "2024-12-19T14:30:00"
        }
        
        # Mock cover result  
        mock_cover_result = {
            "success": True,
            "session_id": "cli_combiner_test",
            "cover_path": "output/covers/test_cover.png",
            "cover_type": "fallback",
            "generation_timestamp": "2024-12-19T14:30:00"
        }
        
        # Mock broadcast metadata
        mock_broadcast_metadata = {
            "session_id": "cli_combiner_test",
            "target_time": "14:30",
            "selected_news": [
                {
                    "title": "Test News Article",
                    "summary": "This is a test news article for combiner testing",
                    "primary_category": "tech"
                }
            ],
            "context_data": {
                "weather": {"formatted": "18°C in Zurich"},
                "crypto": {"formatted": "$103,180 (+2.5%)"}
            }
        }
        
        # Test basic validation
        logger.info("🔍 Testing input validation...")
        result = await combiner_service.test_combiner()
        
        if result:
            logger.success("✅ Content Combiner Validation Test Passed!")
        else:
            logger.warning("⚠️ Content Combiner Validation Test Failed!")
        
        # Test full combination (simulation)
        logger.info("🔗 Testing audio + cover combination (simulation)...")
        combination_result = await combiner_service.combine_audio_and_cover(
            session_id="cli_combiner_test",
            audio_result=mock_audio_result,
            cover_result=mock_cover_result,
            broadcast_metadata=mock_broadcast_metadata
        )
        
        if combination_result.get("success"):
            logger.success("✅ Audio + Cover Combination Test Successful!")
            logger.info(f"📁 Final Audio: {combination_result.get('final_audio_filename')}")
            logger.info(f"🎨 Cover Embedded: {combination_result.get('cover_embedded')}")
            logger.info(f"📊 Quality Score: {combination_result.get('quality_check', {}).get('quality_rating', 'Unknown')}")
            logger.info(f"📏 File Size: {combination_result.get('file_size_mb', 0)} MB")
        else:
            logger.error(f"❌ Audio + Cover Combination Failed: {combination_result.get('error')}")
        
        return result and combination_result.get("success", False)
        
    except Exception as e:
        logger.error(f"❌ CLI Combiner Test Error: {e}")
        return False


async def test_quality_checks():
    """Test quality check functionality"""
    
    logger.info("📊 === TESTING QUALITY CHECKS ===")
    
    combiner_service = ContentCombinerService()
    
    # Test quality check on existing files
    output_dir = Path("output/audio")
    audio_files = list(output_dir.glob("*.mp3"))
    
    if audio_files:
        test_file = audio_files[0]
        logger.info(f"🔍 Testing quality check on: {test_file.name}")
        
        quality_result = await combiner_service._perform_quality_check(test_file)
        
        logger.info(f"📊 Quality Results:")
        logger.info(f"   File Exists: {quality_result.get('file_exists')}")
        logger.info(f"   File Size: {quality_result.get('file_size_mb')} MB")
        logger.info(f"   Quality Score: {quality_result.get('quality_score')}/100")
        logger.info(f"   Quality Rating: {quality_result.get('quality_rating')}")
        
        return quality_result.get("quality_score", 0) > 50
    else:
        logger.warning("⚠️ No audio files found for quality testing")
        return False


async def simulate_full_workflow():
    """Simulate a full audio + cover workflow"""
    
    logger.info("🔄 === SIMULATING FULL WORKFLOW ===")
    
    # Step 1: Import required services
    try:
        from services.audio_generation_service import AudioGenerationService
        from services.image_generation_service import ImageGenerationService
        
        audio_service = AudioGenerationService()
        image_service = ImageGenerationService()
        combiner_service = ContentCombinerService()
        
        # Step 2: Generate test script
        test_script = {
            "session_id": "workflow_test",
            "script_content": """
MARCEL: Hello everyone, welcome to RadioX!
JARVIS: Today we're covering some exciting tech news.
MARCEL: Bitcoin has reached incredible new heights!
JARVIS: Let's dive into the technical analysis...
MARCEL: That's all for today's RadioX broadcast!
            """.strip()
        }
        
        # Step 3: Generate audio
        logger.info("🔊 Step 1/3: Generating audio...")
        audio_result = await audio_service.generate_audio(test_script)
        
        if not audio_result.get("success"):
            logger.error("❌ Audio generation failed")
            return False
        
        logger.success("✅ Audio generated successfully")
        
        # Step 4: Generate cover
        logger.info("🎨 Step 2/3: Generating cover...")
        test_content = {
            "selected_news": [
                {"title": "Bitcoin News", "primary_category": "bitcoin_crypto"}
            ],
            "context_data": {"crypto": {"formatted": "$100K"}}
        }
        
        cover_result = await image_service.generate_cover_art(
            "workflow_test",
            test_content,
            "15:00"
        )
        
        if not cover_result.get("success"):
            logger.warning("⚠️ Cover generation failed, continuing without cover")
        else:
            logger.success("✅ Cover generated successfully")
        
        # Step 5: Combine
        logger.info("🔗 Step 3/3: Combining audio + cover...")
        final_result = await combiner_service.combine_audio_and_cover(
            "workflow_test",
            audio_result,
            cover_result,
            {"target_time": "15:00", "selected_news": test_content["selected_news"]}
        )
        
        if final_result.get("success"):
            logger.success("🎉 Full workflow completed successfully!")
            logger.info(f"📁 Final file: {final_result.get('final_audio_filename')}")
            return True
        else:
            logger.error("❌ Final combination failed")
            return False
        
    except ImportError as e:
        logger.error(f"❌ Service import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Workflow error: {e}")
        return False


async def main():
    """Main CLI function"""
    
    logger.info("🔗 RadioX Content Combiner CLI")
    logger.info("===============================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            success = await test_content_combiner()
            sys.exit(0 if success else 1)
            
        elif command == "quality":
            success = await test_quality_checks()
            sys.exit(0 if success else 1)
            
        elif command == "workflow":
            success = await simulate_full_workflow()
            sys.exit(0 if success else 1)
            
        elif command == "help":
            print("""
RadioX Content Combiner CLI Commands:
====================================

python cli_combiner.py test       - Test basic combiner functionality
python cli_combiner.py quality    - Test quality check functionality
python cli_combiner.py workflow   - Simulate full audio+cover workflow
python cli_combiner.py help       - Show this help

Examples:
python cli_combiner.py test
python cli_combiner.py workflow
            """)
            sys.exit(0)
        
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Use 'python cli_combiner.py help' for available commands")
            sys.exit(1)
    
    else:
        # Default: run basic test
        logger.info("Running default combiner test...")
        success = await test_content_combiner()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 