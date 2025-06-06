#!/usr/bin/env python3
"""
Image Generation Service
========================

Separater Service für Cover-Art Generierung:
- DALL-E Integration für AI-generierte Cover
- MP3 Metadata + Cover Embedding  
- Broadcast-spezifische Designs
"""

import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from PIL import Image, ImageDraw, ImageFont

# Import centralized settings
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import get_settings


class ImageGenerationService:
    """Service für AI-generierte Cover-Art"""
    
    def __init__(self):
        # Load settings centrally
        self.settings = get_settings()
        self.openai_api_key = self.settings.openai_api_key
        self.dall_e_base_url = "https://api.openai.com/v1/images/generations"
        
        # Output-Verzeichnisse
        self.output_dir = Path("output/covers")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cover-Konfiguration
        self.config = {
            "image_size": "1024x1024",
            "image_quality": "hd", 
            "style": "vivid",
            "timeout": 60
        }
    
    async def generate_cover_art(
        self,
        session_id: str,
        broadcast_content: Dict[str, Any],
        target_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generiert AI Cover-Art für Broadcast"""
        
        logger.info(f"🎨 Generiere Cover-Art für Session {session_id}")
        
        if not self.openai_api_key:
            return await self._generate_fallback_cover(session_id, broadcast_content)
        
        try:
            # 1. DALL-E Prompt erstellen
            prompt = self._create_dalle_prompt(broadcast_content, target_time)
            
            # 2. DALL-E API Request
            cover_url = await self._request_dalle_image(prompt)
            
            if not cover_url:
                return await self._generate_fallback_cover(session_id, broadcast_content)
            
            # 3. Cover-Image herunterladen
            cover_path = await self._download_cover_image(cover_url, session_id)
            
            if not cover_path:
                return await self._generate_fallback_cover(session_id, broadcast_content)
            
            result = {
                "success": True,
                "session_id": session_id,
                "cover_path": str(cover_path),
                "cover_filename": cover_path.name,
                "dalle_prompt": prompt,
                "generation_timestamp": datetime.now().isoformat(),
                "cover_type": "ai_generated"
            }
            
            logger.info(f"✅ AI Cover-Art generiert: {cover_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Cover-Generierung: {e}")
            return await self._generate_fallback_cover(session_id, broadcast_content)
    
    async def embed_cover_in_mp3(
        self,
        audio_file: Path,
        cover_file: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Bettet Cover-Art in MP3-Datei ein"""
        
        logger.info(f"🏷️ Bette Cover in MP3 ein: {audio_file.name}")
        
        try:
            # Hier würde eyed3 Integration kommen
            # Für jetzt: Proof of concept
            logger.success(f"✅ Cover embedding simuliert für {audio_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Cover-Embedding: {e}")
            return False
    
    # Private Methods
    
    def _create_dalle_prompt(self, broadcast_content: Dict[str, Any], target_time: Optional[str] = None) -> str:
        """Erstellt DALL-E Prompt"""
        
        # Basis-Prompt für RadioX
        prompt = """Create a professional podcast/radio cover art for 'RadioX AI News'. 
        Modern, sleek design with vibrant colors, AI/tech elements, professional broadcasting vibes."""
        
        return prompt
    
    async def _request_dalle_image(self, prompt: str) -> Optional[str]:
        """Sendet Request an DALL-E API"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": self.config["image_size"],
                "quality": self.config["image_quality"],
                "style": self.config["style"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.dall_e_base_url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        image_url = result["data"][0]["url"]
                        logger.info("✅ DALL-E Cover-Art generiert")
                        return image_url
                    else:
                        logger.error(f"❌ DALL-E API Fehler {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ DALL-E Request Fehler: {e}")
            return None
    
    async def _download_cover_image(self, image_url: str, session_id: str) -> Optional[Path]:
        """Lädt Cover-Image herunter"""
        
        try:
            cover_filename = f"cover_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cover_path = self.output_dir / cover_filename
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        with open(cover_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        logger.info(f"✅ Cover-Image heruntergeladen: {cover_filename}")
                        return cover_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Cover-Download Fehler: {e}")
            return None
    
    async def _generate_fallback_cover(self, session_id: str, broadcast_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert einfaches Fallback-Cover"""
        
        try:
            # Einfaches Cover mit PIL
            image = Image.new('RGB', (1024, 1024), color='#1a1a2e')
            draw = ImageDraw.Draw(image)
            
            # RadioX Text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 120)
            except:
                font = ImageFont.load_default()
            
            draw.text((200, 400), "RadioX", fill="white", font=font)
            draw.text((250, 520), "AI News", fill="#00d4ff", font=font)
            
            # Speichern
            fallback_filename = f"fallback_cover_{session_id}.png"
            fallback_path = self.output_dir / fallback_filename
            
            image.save(fallback_path, "PNG")
            
            logger.info(f"✅ Fallback Cover erstellt: {fallback_filename}")
            
            return {
                "success": True,
                "session_id": session_id,
                "cover_path": str(fallback_path),
                "cover_filename": fallback_path.name,
                "generation_timestamp": datetime.now().isoformat(),
                "cover_type": "fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback Cover Fehler: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "generation_timestamp": datetime.now().isoformat()
            } 