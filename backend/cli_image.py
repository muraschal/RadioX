#!/usr/bin/env python3
"""
CLI Image Generation
===================

Standalone CLI für Image Generation Service Testing
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent / "src"))

from services.image_generation_service import ImageGenerationService
from loguru import logger


async def test_image_generation():
    """Test Image Generation Service"""
    
    logger.info("🎨 === CLI IMAGE GENERATION TEST ===")
    
    try:
        # Initialize service
        image_service = ImageGenerationService()
        
        # Mock broadcast content
        test_content = {
            "selected_news": [
                {
                    "title": "Bitcoin Reaches New All-Time High",
                    "summary": "Cryptocurrency soars past $100,000 milestone",
                    "primary_category": "bitcoin_crypto"
                },
                {
                    "title": "AI Technology Breakthrough",
                    "summary": "New AI model shows remarkable capabilities",
                    "primary_category": "tech"
                }
            ],
            "context_data": {
                "weather": {"formatted": "18°C in Zurich"},
                "crypto": {"formatted": "$103,180 (+2.5%)"}
            }
        }
        
        # Test cover art generation
        logger.info("🎨 Testing cover art generation...")
        result = await image_service.generate_cover_art(
            session_id="cli_test_image",
            broadcast_content=test_content,
            target_time="14:30"
        )
        
        if result.get("success"):
            logger.success(f"✅ Cover Art Generated Successfully!")
            logger.info(f"📁 Cover Path: {result.get('cover_path')}")
            logger.info(f"🏷️ Cover Type: {result.get('cover_type')}")
            logger.info(f"📏 Cover Filename: {result.get('cover_filename')}")
            
            if result.get("dalle_prompt"):
                logger.info(f"🎭 DALL-E Prompt: {result['dalle_prompt'][:100]}...")
        else:
            logger.warning(f"⚠️ Cover Art Generation Failed: {result.get('error', 'Unknown error')}")
        
        # Test cover embedding (mock)
        if result.get("success") and result.get("cover_path"):
            logger.info("🏷️ Testing cover embedding (mock)...")
            
            mock_audio_path = Path("test_audio.mp3")
            cover_path = Path(result["cover_path"])
            
            embed_result = await image_service.embed_cover_in_mp3(
                mock_audio_path,
                cover_path,
                {"session_id": "cli_test", "target_time": "14:30"}
            )
            
            if embed_result:
                logger.success("✅ Cover Embedding Test Passed!")
            else:
                logger.warning("⚠️ Cover Embedding Test Failed!")
        
        return result.get("success", False)
        
    except Exception as e:
        logger.error(f"❌ CLI Image Test Error: {e}")
        return False


async def generate_test_covers():
    """Generate multiple test covers"""
    
    logger.info("🎨 === GENERATING MULTIPLE TEST COVERS ===")
    
    image_service = ImageGenerationService()
    
    test_scenarios = [
        {
            "name": "Bitcoin News",
            "content": {
                "selected_news": [{"title": "Bitcoin Hits $100K", "primary_category": "bitcoin_crypto"}],
                "context_data": {"crypto": {"formatted": "$100,000 (+10%)"}}
            },
            "time": "09:00"
        },
        {
            "name": "Tech News",
            "content": {
                "selected_news": [{"title": "AI Breakthrough", "primary_category": "tech"}],
                "context_data": {"weather": {"formatted": "20°C Sunny"}}
            },
            "time": "15:00"
        },
        {
            "name": "Evening News",
            "content": {
                "selected_news": [{"title": "Market Summary", "primary_category": "finance"}],
                "context_data": {}
            },
            "time": "20:00"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios):
        logger.info(f"🎭 Generating {scenario['name']} cover...")
        
        result = await image_service.generate_cover_art(
            session_id=f"test_multi_{i}",
            broadcast_content=scenario["content"],
            target_time=scenario["time"]
        )
        
        results.append({
            "scenario": scenario["name"],
            "success": result.get("success", False),
            "cover_path": result.get("cover_path"),
            "cover_type": result.get("cover_type")
        })
        
        if result.get("success"):
            logger.success(f"✅ {scenario['name']} cover generated!")
        else:
            logger.error(f"❌ {scenario['name']} cover failed!")
    
    # Summary
    successful = len([r for r in results if r["success"]])
    logger.info(f"📊 Generated {successful}/{len(results)} covers successfully")
    
    return results


async def main():
    """Main CLI function"""
    
    logger.info("🎨 RadioX Image Generation CLI")
    logger.info("================================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            success = await test_image_generation()
            sys.exit(0 if success else 1)
            
        elif command == "multi":
            results = await generate_test_covers()
            successful = len([r for r in results if r["success"]])
            sys.exit(0 if successful > 0 else 1)
            
        elif command == "help":
            print("""
RadioX Image Generation CLI Commands:
=====================================

python cli_image.py test     - Test basic image generation
python cli_image.py multi    - Generate multiple test covers  
python cli_image.py help     - Show this help

Examples:
python cli_image.py test
python cli_image.py multi
            """)
            sys.exit(0)
        
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Use 'python cli_image.py help' for available commands")
            sys.exit(1)
    
    else:
        # Default: run basic test
        logger.info("Running default image generation test...")
        success = await test_image_generation()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 