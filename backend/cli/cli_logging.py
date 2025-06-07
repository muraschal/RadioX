#!/usr/bin/env python3
"""
📋 RadioX Content Logging Service - Standalone CLI
Supabase Content Logging Testing
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.content_logging_service import ContentLoggingService
from loguru import logger


async def test_news_logging():
    """Test News Logging functionality"""
    
    logger.info("📋 === CLI NEWS LOGGING TEST ===")
    
    try:
        # Initialize service
        logging_service = ContentLoggingService()
        
        # Mock collected news (ALL news that was gathered)
        mock_collected_news = [
            {
                "source": "Reuters RSS",
                "title": "Bitcoin Reaches New All-Time High of $100,000",
                "summary": "Cryptocurrency enthusiasts celebrate as Bitcoin crosses historic milestone",
                "url": "https://reuters.com/bitcoin-100k",
                "primary_category": "bitcoin_crypto",
                "priority_score": 0.95
            },
            {
                "source": "TechCrunch RSS", 
                "title": "AI Breakthrough: New Language Model Surpasses GPT-4",
                "summary": "Revolutionary AI model shows unprecedented capabilities",
                "url": "https://techcrunch.com/ai-breakthrough",
                "primary_category": "tech",
                "priority_score": 0.88
            },
            {
                "source": "Swiss News RSS",
                "title": "Zurich Weather Update: Sunny 18°C",
                "summary": "Pleasant weather conditions continue in Zurich",
                "url": "https://swissnews.com/weather-zurich",
                "primary_category": "weather",
                "priority_score": 0.45
            },
            {
                "source": "Financial Times RSS",
                "title": "European Markets Show Mixed Results",
                "summary": "Stock markets across Europe show varying performance",
                "url": "https://ft.com/european-markets",
                "primary_category": "finance",
                "priority_score": 0.70
            },
            {
                "source": "BBC RSS",
                "title": "Global Climate Summit Discusses Carbon Targets",
                "summary": "World leaders meet to discuss new environmental goals",
                "url": "https://bbc.com/climate-summit",
                "primary_category": "environment",
                "priority_score": 0.65
            }
        ]
        
        # Mock selected news (only news chosen for broadcast)
        mock_selected_news = [
            mock_collected_news[0],  # Bitcoin news (highest priority)
            mock_collected_news[1],  # AI news (second highest)
        ]
        
        # Mock collection metadata
        mock_collection_metadata = {
            "collection_timestamp": datetime.now().isoformat(),
            "rss_sources_count": 5,
            "total_articles_found": len(mock_collected_news),
            "selection_criteria": "priority_score > 0.8",
            "target_time": "14:30"
        }
        
        # Test news logging
        logger.info("📋 Testing news logging...")
        result = await logging_service.log_collected_news(
            session_id="cli_logging_test",
            collected_news=mock_collected_news,
            selected_news=mock_selected_news,
            collection_metadata=mock_collection_metadata
        )
        
        if result.get("success"):
            logger.success("✅ News Logging Test Successful!")
            logger.info(f"📊 Total News Logged: {result.get('total_news_logged')}")
            logger.info(f"✅ Selected for Broadcast: {result.get('selected_for_broadcast')}")
            logger.info(f"📁 JSON Log Path: {result.get('json_log_path')}")
            
            # Check duplicate analysis
            duplicate_analysis = result.get("duplicate_analysis", {})
            if duplicate_analysis:
                logger.info(f"🔍 Duplicate Analysis:")
                logger.info(f"   Unique Hashes: {duplicate_analysis.get('total_unique_hashes')}")
                logger.info(f"   Duplicates Found: {duplicate_analysis.get('duplicate_hashes')}")
        else:
            logger.error(f"❌ News Logging Failed: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        logger.error(f"❌ CLI News Logging Test Error: {e}")
        return False


async def test_script_logging():
    """Test Script Logging functionality"""
    
    logger.info("📝 === CLI SCRIPT LOGGING TEST ===")
    
    try:
        # Initialize service
        logging_service = ContentLoggingService()
        
        # Mock final script
        mock_script = """
MARCEL: [excited] Good afternoon, and welcome to RadioX! I'm Marcel, your enthusiastic host.

JARVIS: [analytical] And I'm Jarvis, your AI co-host. Today we have some fascinating developments in the cryptocurrency world.

MARCEL: [impressed] Absolutely incredible news today - Bitcoin has officially crossed the $100,000 milestone! [whispers] That's absolutely mind-blowing.

JARVIS: [sarcastic] Well, Marcel, for those of us who've been analyzing the data patterns, this was quite predictable given the current market dynamics.

MARCEL: [laughs] Leave it to you, Jarvis, to take the excitement out of a historic moment! [laughs harder]

JARVIS: [curious] But let's dive deeper into what this means for the broader cryptocurrency ecosystem and institutional adoption trends.

MARCEL: [excited] We're also covering a major AI breakthrough today - a new language model that's reportedly surpassing GPT-4 capabilities!

JARVIS: [mischievously] As an AI myself, I find these developments particularly... interesting. Perhaps I'll have some new colleagues soon.

MARCEL: [excited] That's all for today's RadioX broadcast! Thanks for tuning in, everyone!

JARVIS: [whispers] Until next time, keep questioning the patterns around you.
        """.strip()
        
        # Mock script metadata
        mock_script_metadata = {
            "target_time": "14:30",
            "generation_timestamp": datetime.now().isoformat(),
            "voice_config": {
                "marcel_voice": "Rachel (English V3)",
                "jarvis_voice": "Bella (English V3)",
                "model": "eleven_multilingual_v2"
            },
            "context_data": {
                "weather": {"formatted": "18°C in Zurich"},
                "crypto": {"formatted": "$100,180 (+5.2%)"},
                "news_sources": ["Reuters", "TechCrunch", "BBC"]
            }
        }
        
        # Test script logging
        logger.info("📝 Testing script logging...")
        result = await logging_service.log_final_script(
            session_id="cli_logging_test",
            script_content=mock_script,
            script_metadata=mock_script_metadata
        )
        
        if result.get("success"):
            logger.success("✅ Script Logging Test Successful!")
            logger.info(f"🔐 Script Hash: {result.get('script_hash')}")
            logger.info(f"📊 Word Count: {result.get('word_count')}")
            logger.info(f"⏱️ Estimated Duration: {result.get('estimated_duration_seconds')}s")
            logger.info(f"📁 Script File: {result.get('script_file_path')}")
        else:
            logger.error(f"❌ Script Logging Failed: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        logger.error(f"❌ CLI Script Logging Test Error: {e}")
        return False


async def test_content_reports():
    """Test Content Report Generation"""
    
    logger.info("📊 === CLI CONTENT REPORTS TEST ===")
    
    try:
        # Initialize service
        logging_service = ContentLoggingService()
        
        # Test different report types
        report_types = ["summary", "detailed", "analytics"]
        
        for report_type in report_types:
            logger.info(f"📊 Generating {report_type} report...")
            
            # Generate report for last 7 days
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
            end_date = datetime.now().isoformat()
            
            result = await logging_service.generate_content_report(
                start_date=start_date,
                end_date=end_date,
                report_type=report_type
            )
            
            if result.get("success"):
                logger.success(f"✅ {report_type.title()} Report Generated!")
                logger.info(f"📁 Report File: {result.get('report_file_path')}")
                
                # Show some report data
                report_data = result.get("report_data", {})
                if "news_stats" in report_data:
                    news_stats = report_data["news_stats"]
                    logger.info(f"📰 News Stats:")
                    logger.info(f"   Total Collected: {news_stats.get('total_collected', 0)}")
                    logger.info(f"   Selected for Broadcast: {news_stats.get('selected_for_broadcast', 0)}")
                    logger.info(f"   Selection Rate: {news_stats.get('selection_rate', 0)}%")
                
                if "script_stats" in report_data:
                    script_stats = report_data["script_stats"]
                    logger.info(f"📝 Script Stats:")
                    logger.info(f"   Total Scripts: {script_stats.get('total_scripts', 0)}")
                    logger.info(f"   Average Words: {script_stats.get('avg_words_per_script', 0)}")
            else:
                logger.error(f"❌ {report_type.title()} Report Failed: {result.get('error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CLI Content Reports Test Error: {e}")
        return False


async def test_full_logging_workflow():
    """Test complete logging workflow"""
    
    logger.info("🔄 === FULL LOGGING WORKFLOW TEST ===")
    
    try:
        # Step 1: Test news logging
        logger.info("Step 1/3: Testing news logging...")
        news_result = await test_news_logging()
        
        if not news_result:
            logger.error("❌ News logging failed")
            return False
        
        # Step 2: Test script logging
        logger.info("Step 2/3: Testing script logging...")
        script_result = await test_script_logging()
        
        if not script_result:
            logger.error("❌ Script logging failed")
            return False
        
        # Step 3: Generate reports
        logger.info("Step 3/3: Testing report generation...")
        report_result = await test_content_reports()
        
        if not report_result:
            logger.error("❌ Report generation failed")
            return False
        
        logger.success("🎉 Full logging workflow completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Full Logging Workflow Error: {e}")
        return False


async def main():
    """Main CLI function"""
    
    logger.info("📋 RadioX Content Logging CLI")
    logger.info("==============================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "news":
            success = await test_news_logging()
            sys.exit(0 if success else 1)
            
        elif command == "script":
            success = await test_script_logging()
            sys.exit(0 if success else 1)
            
        elif command == "reports":
            success = await test_content_reports()
            sys.exit(0 if success else 1)
            
        elif command == "workflow":
            success = await test_full_logging_workflow()
            sys.exit(0 if success else 1)
            
        elif command == "help":
            print("""
RadioX Content Logging CLI Commands:
===================================

python cli_logging.py news       - Test news logging functionality
python cli_logging.py script     - Test script logging functionality
python cli_logging.py reports    - Test report generation
python cli_logging.py workflow   - Test complete logging workflow
python cli_logging.py help       - Show this help

Examples:
python cli_logging.py news
python cli_logging.py workflow
            """)
            sys.exit(0)
        
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Use 'python cli_logging.py help' for available commands")
            sys.exit(1)
    
    else:
        # Default: run full workflow test
        logger.info("Running default logging workflow test...")
        success = await test_full_logging_workflow()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 