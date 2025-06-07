#!/usr/bin/env python3
"""
🔊 RadioX Audio Generation Service - Standalone CLI
ElevenLabs V3 TTS Audio Generation Testing
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.audio_generation_service import AudioGenerationService
from loguru import logger


async def test_audio_generation():
    """Test Audio Generation Service"""
    
    logger.info("🔊 === CLI AUDIO GENERATION TEST ===")
    
    try:
        # Initialize service
        audio_service = AudioGenerationService()
        
        # Test script
        test_script = {
            "session_id": "cli_audio_test",
            "script_content": """
MARCEL: [excited] Hello everyone, welcome to RadioX!
JARVIS: [analytical] Today we're testing our new V3 English audio system.
MARCEL: [impressed] The quality is absolutely incredible!
JARVIS: [sarcastic] Well, Marcel, it's just technology doing what it's supposed to do.
MARCEL: [laughs] You always know how to bring me down to earth! [laughs harder]
JARVIS: [whispers] But between you and me... this is pretty impressive.
MARCEL: [excited] Thanks for listening to our audio test!
            """.strip()
        }
        
        # Test audio generation
        logger.info("🔊 Testing audio generation...")
        result = await audio_service.generate_audio(test_script)
        
        if result.get("success"):
            logger.success("✅ Audio Generation Test Successful!")
            logger.info(f"📁 Final Audio: {result.get('final_audio_file')}")
            logger.info(f"⏱️ Duration: {result.get('duration_seconds', 0)}s")
            logger.info(f"📊 Segments: {len(result.get('segment_files', []))}")
            
            # Show audio metadata
            metadata = result.get("metadata", {})
            if metadata:
                logger.info(f"🎤 Audio Metadata:")
                logger.info(f"   Total Duration: {metadata.get('total_duration_seconds', 0)}s")
                logger.info(f"   Audio Quality: {metadata.get('audio_quality', 'Unknown')}")
        else:
            logger.error(f"❌ Audio Generation Failed: {result.get('error', 'Unknown error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        logger.error(f"❌ CLI Audio Test Error: {e}")
        return False


async def test_voice_configuration():
    """Test Voice Configuration"""
    
    logger.info("🎭 === TESTING VOICE CONFIGURATION ===")
    
    audio_service = AudioGenerationService()
    
    # Test different voice combinations
    test_scripts = [
        {
            "name": "English Default",
            "script": {
                "session_id": "voice_test_en",
                "script_content": "MARCEL: Testing English voice.\nJARVIS: Analyzing audio quality."
            }
        },
        {
            "name": "Alternative Voices",
            "script": {
                "session_id": "voice_test_alt",
                "script_content": "MARCEL_ALT: Testing alternative voice.\nJARVIS_ALT: Alternative AI voice test."
            }
        }
    ]
    
    results = []
    
    for test in test_scripts:
        logger.info(f"🎤 Testing {test['name']}...")
        
        result = await audio_service.generate_audio(test["script"])
        results.append({
            "name": test["name"],
            "success": result.get("success", False),
            "duration": result.get("duration_seconds", 0),
            "file": result.get("final_audio_file")
        })
        
        if result.get("success"):
            logger.success(f"✅ {test['name']} voice test successful!")
        else:
            logger.error(f"❌ {test['name']} voice test failed!")
    
    # Summary
    successful = len([r for r in results if r["success"]])
    logger.info(f"🎯 Voice Tests: {successful}/{len(results)} successful")
    
    return successful == len(results)


async def test_v3_emotional_tags():
    """Test V3 Emotional Tags"""
    
    logger.info("🎭 === TESTING V3 EMOTIONAL TAGS ===")
    
    audio_service = AudioGenerationService()
    
    # Test script with all V3 emotional tags
    emotional_script = {
        "session_id": "v3_emotions_test",
        "script_content": """
MARCEL: [excited] Welcome to the V3 emotional tags test!
JARVIS: [analytical] We're testing various emotional expressions.
MARCEL: [impressed] This technology is absolutely mind-blowing!
JARVIS: [sarcastic] Obviously, Marcel. It's just advanced AI processing.
MARCEL: [laughs] You're such a comedian! [laughs harder]
JARVIS: [curious] But I must admit, the emotional range is quite fascinating.
MARCEL: [whispers] Between you and me, this is revolutionary.
JARVIS: [whispers] Agreed. The future of AI voice is here.
        """.strip()
    }
    
    logger.info("🎭 Generating audio with V3 emotional tags...")
    result = await audio_service.generate_audio(emotional_script)
    
    if result.get("success"):
        logger.success("✅ V3 Emotional Tags Test Successful!")
        logger.info(f"📁 Emotional Audio: {result.get('final_audio_file')}")
        logger.info("🎭 Tags used: [excited], [analytical], [impressed], [sarcastic], [laughs], [curious], [whispers]")
        return True
    else:
        logger.error("❌ V3 Emotional Tags Test Failed!")
        return False


async def main():
    """Main CLI function"""
    
    logger.info("🔊 RadioX Audio Generation CLI")
    logger.info("===============================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            success = await test_audio_generation()
            sys.exit(0 if success else 1)
            
        elif command == "voices":
            success = await test_voice_configuration()
            sys.exit(0 if success else 1)
            
        elif command == "emotions":
            success = await test_v3_emotional_tags()
            sys.exit(0 if success else 1)
            
        elif command == "help":
            print("""
RadioX Audio Generation CLI Commands:
====================================

python cli_audio.py test       - Test basic audio generation
python cli_audio.py voices     - Test voice configurations
python cli_audio.py emotions   - Test V3 emotional tags
python cli_audio.py help       - Show this help

Examples:
python cli_audio.py test
python cli_audio.py emotions
            """)
            sys.exit(0)
        
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Use 'python cli_audio.py help' for available commands")
            sys.exit(1)
    
    else:
        # Default: run basic test
        logger.info("Running default audio generation test...")
        success = await test_audio_generation()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 