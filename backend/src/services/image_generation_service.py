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
import subprocess

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
        
        # Output-Verzeichnis - DIREKT IM ROOT (nicht in backend/)
        self.output_dir = Path(__file__).parent.parent.parent.parent / "output"
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
        """Bettet Cover-Art in MP3-Datei ein mit ffmpeg"""
        
        logger.info(f"🏷️ Bette Cover in MP3 ein: {audio_file.name}")
        
        try:
            # FFmpeg-Pfade für verschiedene Systeme
            ffmpeg_paths = [
                str(Path(__file__).parent.parent.parent.parent / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe"),
                "ffmpeg"  # Fallback für System-PATH
            ]
            
            # Finde verfügbares ffmpeg
            ffmpeg_cmd = None
            for ffmpeg_path in ffmpeg_paths:
                try:
                    result = subprocess.run([ffmpeg_path, '-version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        ffmpeg_cmd = ffmpeg_path
                        break
                except:
                    continue
            
            if not ffmpeg_cmd:
                logger.warning("⚠️ ffmpeg nicht gefunden - Cover-Embedding übersprungen")
                return False
            
            # Erstelle temporäre Ausgabedatei
            temp_output = audio_file.parent / f"temp_with_cover_{audio_file.stem}.mp3"
            
            # ffmpeg Kommando für Cover-Embedding
            ffmpeg_command = [
                ffmpeg_cmd, '-y',  # Überschreibe Ausgabedatei
                '-i', str(audio_file),  # Audio-Input
                '-i', str(cover_file),  # Cover-Input
                '-map', '0:0',  # Audio-Stream
                '-map', '1:0',  # Cover-Stream
                '-c', 'copy',  # Kopiere Audio ohne Re-Encoding
                '-id3v2_version', '3',  # ID3v2.3 für bessere Kompatibilität
                '-metadata:s:v', 'title="Album cover"',
                '-metadata:s:v', 'comment="Cover"',
                '-metadata', 'title=RadioX AI News',
                '-metadata', 'artist=RadioX',
                '-metadata', 'album=AI News Broadcast',
                str(temp_output)
            ]
            
            # Führe ffmpeg aus
            result = subprocess.run(ffmpeg_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Ersetze Original-Datei mit Cover-Version
                import shutil
                shutil.move(str(temp_output), str(audio_file))
                
                logger.success(f"✅ Cover erfolgreich in MP3 eingebettet: {audio_file.name}")
                return True
            else:
                logger.error(f"❌ ffmpeg Cover-Embedding fehlgeschlagen: {result.stderr}")
                # Lösche temporäre Datei falls vorhanden
                if temp_output.exists():
                    temp_output.unlink()
                return False
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Cover-Embedding: {e}")
            return False
    
    # Private Methods
    
    def _create_dalle_prompt(self, broadcast_content: Dict[str, Any], target_time: Optional[str] = None) -> str:
        """Erstellt spezifischen DALL-E Prompt basierend auf Broadcast-Inhalten"""
        
        # Extrahiere Broadcast-Informationen
        script_content = broadcast_content.get("script_content", "")
        selected_news = broadcast_content.get("selected_news", [])
        broadcast_style = broadcast_content.get("broadcast_style", "Unknown")
        
        # Analysiere Inhalte für spezifische Elemente
        topics = self._analyze_broadcast_topics(script_content, selected_news)
        time_context = self._get_time_context(target_time, broadcast_style)
        
        # VERBESSERTER PROMPT MIT FOKUS AUF 2-3 HAUPTTHEMEN
        prompt = f"""A professional radio studio scene with a futuristic AI news theme. The main focus should be on displaying today's TOP 3 NEWS TOPICS prominently in the background.

MAIN VISUAL ELEMENTS:
- A modern radio host at a sleek broadcast desk with professional microphone
- Large, prominent holographic displays showing: {topics['topic_display_1']}, {topics['topic_display_2']}, and {topics['topic_display_3']}
- An AI assistant hologram with {time_context['ai_style']} appearance
- {time_context['color_scheme']} lighting creating {time_context['mood_tones']}

TOPIC FOCUS:
The background should clearly show these news topics as large, readable displays:
1. {topics['topic_text_1']}
2. {topics['topic_text_2']} 
3. {topics['topic_text_3']}

STYLE: Professional broadcast studio, high-tech news environment, {broadcast_style.lower()} energy, cinematic lighting, sharp focus on the topic displays, modern UI elements.

The image should make it immediately clear what the main news topics are about."""
        
        logger.debug(f"🎨 VERBESSERTE DALL-E Prompt erstellt mit Topic-Fokus")
        return prompt
    
    def _analyze_broadcast_topics(self, script_content: str, selected_news: list) -> Dict[str, str]:
        """Analysiert Broadcast-Inhalte für spezifische Cover-Elemente"""
        
        # VERBESSERTE TOPIC-EXTRAKTION FÜR COVER-ART
        topics = {
            # Alte Format-Kompatibilität
            "screen_content": "news ticker",
            "topic_icon_1": "📰 breaking news",
            "topic_icon_2": "💰 financial data", 
            "topic_icon_3": "🌍 global updates",
            
            # NEUE TOPIC-DISPLAYS FÜR COVER-ART
            "topic_display_1": "BREAKING NEWS",
            "topic_display_2": "MARKET DATA",
            "topic_display_3": "GLOBAL UPDATES",
            "topic_text_1": "Latest Breaking News",
            "topic_text_2": "Financial Markets",
            "topic_text_3": "World Updates"
        }
        
        # Analysiere Script-Content für Schlüsselwörter
        content_lower = script_content.lower()
        
        # PRIORITÄT 1: BITCOIN/CRYPTO DETECTION
        if any(keyword in content_lower for keyword in ["bitcoin", "crypto", "blockchain", "ethereum", "btc"]):
            topics.update({
                "topic_display_1": "₿ BITCOIN LIVE",
                "topic_display_2": "CRYPTO MARKETS", 
                "topic_display_3": "BLOCKCHAIN NEWS",
                "topic_text_1": "Bitcoin Price Update",
                "topic_text_2": "Cryptocurrency Markets",
                "topic_text_3": "Blockchain Technology"
            })
        
        # PRIORITÄT 2: POLITIK/GOVERNMENT
        elif any(keyword in content_lower for keyword in ["government", "politics", "election", "policy", "parliament", "minister"]):
            topics.update({
                "topic_display_1": "🏛️ POLITICS LIVE",
                "topic_display_2": "GOVERNMENT NEWS",
                "topic_display_3": "POLICY UPDATES", 
                "topic_text_1": "Political Developments",
                "topic_text_2": "Government Decisions",
                "topic_text_3": "Policy Changes"
            })
        
        # PRIORITÄT 3: TECH/AI DETECTION
        elif any(keyword in content_lower for keyword in ["ai", "artificial intelligence", "technology", "innovation", "tech"]):
            topics.update({
                "topic_display_1": "🤖 AI TECH",
                "topic_display_2": "INNOVATION NEWS",
                "topic_display_3": "TECH UPDATES",
                "topic_text_1": "AI Technology",
                "topic_text_2": "Tech Innovation", 
                "topic_text_3": "Digital Trends"
            })
        
        # PRIORITÄT 4: WEATHER DETECTION
        elif any(keyword in content_lower for keyword in ["weather", "temperature", "sunny", "rain", "snow", "celsius"]):
            topics.update({
                "topic_display_1": "🌤️ WEATHER LIVE",
                "topic_display_2": "TEMPERATURE",
                "topic_display_3": "FORECAST",
                "topic_text_1": "Current Weather",
                "topic_text_2": "Temperature Update",
                "topic_text_3": "Weather Forecast"
            })
        
        # ANALYSIERE NEWS-TITEL FÜR SPEZIFISCHE THEMEN
        if selected_news and len(selected_news) >= 2:
            try:
                # Nimm die ersten 3 News-Titel als Topics
                for i, news in enumerate(selected_news[:3]):
                    title = news.get("title", "").strip()
                    if title and len(title) > 10:  # Nur aussagekräftige Titel
                        # Kürze Titel für Display
                        display_title = title[:25] + "..." if len(title) > 25 else title
                        text_title = title[:40] + "..." if len(title) > 40 else title
                        
                        topics[f"topic_display_{i+1}"] = display_title.upper()
                        topics[f"topic_text_{i+1}"] = text_title
                        
                        # Icon basierend auf Inhalt
                        title_lower = title.lower()
                        if "bitcoin" in title_lower or "crypto" in title_lower:
                            topics[f"topic_display_{i+1}"] = f"₿ {display_title.upper()}"
                        elif "weather" in title_lower or "temperature" in title_lower:
                            topics[f"topic_display_{i+1}"] = f"🌤️ {display_title.upper()}"
                        elif "politics" in title_lower or "government" in title_lower:
                            topics[f"topic_display_{i+1}"] = f"🏛️ {display_title.upper()}"
                        elif "tech" in title_lower or "ai" in title_lower:
                            topics[f"topic_display_{i+1}"] = f"🤖 {display_title.upper()}"
                        elif "traffic" in title_lower or "transport" in title_lower:
                            topics[f"topic_display_{i+1}"] = f"🚗 {display_title.upper()}"
                        else:
                            topics[f"topic_display_{i+1}"] = f"📰 {display_title.upper()}"
                            
            except Exception as e:
                logger.warning(f"⚠️ Fehler bei News-Titel-Analyse: {e}")
        
        # SCHWEIZ-SPEZIFISCHE ANPASSUNGEN
        if any(keyword in content_lower for keyword in ["switzerland", "swiss", "zurich", "basel", "bern", "geneva"]):
            # Füge Schweiz-Kontext hinzu
            if "🇨🇭" not in topics["topic_display_1"]:
                topics["topic_display_3"] = f"🇨🇭 SWISS NEWS"
                topics["topic_text_3"] = "Switzerland Updates"
        
        return topics
    
    def _get_time_context(self, target_time: Optional[str], broadcast_style: str) -> Dict[str, str]:
        """Bestimmt Zeit-spezifische visuelle Elemente"""
        
        # Parse Zeit falls verfügbar
        hour = 12  # Default
        if target_time:
            try:
                hour = int(target_time.split(":")[0])
            except:
                pass
        
        # Morning Context (6-11)
        if 6 <= hour <= 11:
            return {
                "color_scheme": "warm golden sunrise",
                "host_appearance": "energetic professional in casual business attire",
                "desk_style": "modern glass and chrome",
                "drink_type": "coffee",
                "ai_style": "bright blue energy",
                "mood_tones": "warm golden tones and soft morning light"
            }
        
        # Afternoon Context (12-17)
        elif 12 <= hour <= 17:
            return {
                "color_scheme": "bright daylight blue",
                "host_appearance": "focused professional in sharp business wear",
                "desk_style": "sleek metallic",
                "drink_type": "espresso",
                "ai_style": "crisp white hologram",
                "mood_tones": "bright professional lighting with cool blue accents"
            }
        
        # Evening Context (18-22)
        elif 18 <= hour <= 22:
            return {
                "color_scheme": "warm amber evening",
                "host_appearance": "relaxed professional in smart casual",
                "desk_style": "warm wood and metal",
                "drink_type": "tea",
                "ai_style": "soft purple glow",
                "mood_tones": "warm amber tones with soft evening atmosphere"
            }
        
        # Night Context (23-5)
        else:
            return {
                "color_scheme": "deep blue night with neon accents",
                "host_appearance": "calm night host in comfortable attire",
                "desk_style": "dark minimalist",
                "drink_type": "herbal tea",
                "ai_style": "ethereal green hologram",
                "mood_tones": "deep blue night tones with neon highlights"
            }
    
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