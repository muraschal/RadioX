"""
RadioX OpenAI API Service
Direkte Integration mit der OpenAI API ohne MCP Dependencies
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from pathlib import Path
import json

from dotenv import load_dotenv

# Load environment variables from root directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


class OpenAIAPIService:
    """Direkter OpenAI API Service ohne MCP Dependencies"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            logger.error("❌ OpenAI API Key nicht gefunden!")
            logger.info("💡 Prüfe OPENAI_API_KEY in der .env Datei")
            raise ValueError("❌ OpenAI API Key fehlt!")
        
        logger.info("✅ OpenAI API Service initialisiert")
        
        # RadioX Station Prompts
        self.station_prompts = {
            "breaking_news": {
                "voice_name": "JARVIS",
                "style": "professionell, AI-artig, präzise",
                "intro_style": "Willkommen bei Breaking News auf RadioX",
                "news_style": "sachlich, informativ, neutral"
            },
            "bitcoin_og": {
                "voice_name": "Rachel",
                "style": "energisch, Bitcoin-enthusiastisch, modern",
                "intro_style": "Stack Sats, Stay Humble",
                "news_style": "Bitcoin-fokussiert, optimistisch"
            },
            "zueri_style": {
                "voice_name": "Bella",
                "style": "freundlich, lokal, Schweizer Dialekt-Einfluss",
                "intro_style": "Zürich hört Zürich",
                "news_style": "lokal, persönlich, nahbar"
            },
            "tradfi_news": {
                "voice_name": "Adam",
                "style": "seriös, wirtschaftlich, traditionell",
                "intro_style": "Ihr Wirtschaftsradio",
                "news_style": "wirtschaftlich, analytisch, fundiert"
            }
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Sendet Chat Completion Request an OpenAI API
        
        Args:
            messages: Liste von Chat-Messages
            model: OpenAI Model (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Kreativität (0.0-2.0)
            max_tokens: Maximale Token-Anzahl
            
        Returns:
            str: Antwort von OpenAI oder None bei Fehler
        """
        
        try:
            logger.info(f"🤖 OpenAI Request: {model} (temp: {temperature})")
            
            # API Endpoint
            url = f"{self.base_url}/chat/completions"
            
            # Request Headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Request Body
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                data["max_tokens"] = max_tokens
            
            # HTTP Request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            
                            # Token-Verbrauch loggen
                            usage = result.get('usage', {})
                            prompt_tokens = usage.get('prompt_tokens', 0)
                            completion_tokens = usage.get('completion_tokens', 0)
                            total_tokens = usage.get('total_tokens', 0)
                            
                            logger.info(f"✅ OpenAI Response: {total_tokens} tokens ({prompt_tokens}+{completion_tokens})")
                            
                            return content
                        else:
                            logger.error("❌ Keine Antwort in OpenAI Response")
                            return None
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ OpenAI API Fehler {response.status}: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"💥 OpenAI API Fehler: {e}")
            return None
    
    async def enhance_radio_script(
        self,
        raw_script: Dict[str, Any],
        station_type: str = "breaking_news"
    ) -> Optional[Dict[str, Any]]:
        """
        Verbessert ein Radio-Script mit GPT-4
        
        Args:
            raw_script: Rohes Radio-Script
            station_type: Station-Typ für spezifische Prompts
            
        Returns:
            Dict: Verbessertes Script oder None bei Fehler
        """
        
        try:
            logger.info(f"📻 Verbessere Radio-Script für {station_type}")
            
            # Station-spezifische Konfiguration
            station_config = self.station_prompts.get(station_type, self.station_prompts['breaking_news'])
            
            # System Prompt
            system_prompt = f"""Du bist ein professioneller Radio-Moderator für RadioX.

STATION: {station_type.replace('_', ' ').title()}
VOICE: {station_config['voice_name']}
STYLE: {station_config['style']}

AUFGABE: Verwandle rohe Radio-Texte in professionelle, natürliche Radio-Ansagen.

REGELN:
1. Behalte die JSON-Struktur bei
2. Verbessere nur die "text" Felder
3. Mache Texte natürlicher und radio-tauglich
4. Verwende den Station-spezifischen Stil
5. Füge passende Übergänge hinzu
6. Behalte alle anderen Felder unverändert

STIL-GUIDE:
- Intro: {station_config['intro_style']}
- News: {station_config['news_style']}
- Wetter: entspannt, freundlich
- Outro: warm, einladend

Antworte NUR mit dem verbesserten JSON, keine Erklärungen."""

            # User Prompt mit Raw Script
            user_prompt = f"Verbessere dieses Radio-Script:\n\n{json.dumps(raw_script, indent=2, ensure_ascii=False)}"
            
            # Messages für OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # OpenAI Request
            enhanced_text = await self.chat_completion(
                messages=messages,
                model="gpt-4",
                temperature=0.7,
                max_tokens=4000
            )
            
            if enhanced_text:
                try:
                    # JSON parsen
                    enhanced_script = json.loads(enhanced_text)
                    logger.info("✅ Radio-Script erfolgreich verbessert")
                    return enhanced_script
                
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON Parse Fehler: {e}")
                    logger.error(f"Raw Response: {enhanced_text[:500]}...")
                    return None
            
            else:
                logger.error("❌ Keine Antwort von OpenAI")
                return None
                
        except Exception as e:
            logger.error(f"💥 Script Enhancement Fehler: {e}")
            return None
    
    async def enhance_single_text(
        self,
        text: str,
        segment_type: str,
        station_type: str = "breaking_news"
    ) -> Optional[str]:
        """
        Verbessert einen einzelnen Text für Radio
        
        Args:
            text: Roher Text
            segment_type: Segment-Typ (intro, news, weather, etc.)
            station_type: Station-Typ
            
        Returns:
            str: Verbesserter Text oder None bei Fehler
        """
        
        try:
            logger.info(f"📝 Verbessere {segment_type} Text für {station_type}")
            
            # Station-spezifische Konfiguration
            station_config = self.station_prompts.get(station_type, self.station_prompts['breaking_news'])
            
            # Segment-spezifische Prompts
            segment_instructions = {
                "intro": f"Erstelle eine professionelle Radio-Intro mit: {station_config['intro_style']}",
                "news": f"Verwandle in eine natürliche Radio-Nachricht: {station_config['news_style']}",
                "weather": "Erstelle eine entspannte, freundliche Wetter-Ansage",
                "outro": "Erstelle einen warmen, einladenden Radio-Outro",
                "music": "Erstelle eine kurze, passende Musik-Ansage"
            }
            
            instruction = segment_instructions.get(segment_type, "Verbessere diesen Text für Radio")
            
            # System Prompt
            system_prompt = f"""Du bist {station_config['voice_name']}, Radio-Moderator für {station_type.replace('_', ' ').title()} auf RadioX.

DEIN STIL: {station_config['style']}

AUFGABE: {instruction}

REGELN:
1. Natürlich und radio-tauglich
2. Passend zum Station-Stil
3. Keine Anführungszeichen oder Formatierung
4. Direkt sprechbar
5. Maximal 2-3 Sätze

Antworte NUR mit dem verbesserten Text, keine Erklärungen."""

            # Messages für OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
            
            # OpenAI Request
            enhanced_text = await self.chat_completion(
                messages=messages,
                model="gpt-4",
                temperature=0.8,
                max_tokens=200
            )
            
            if enhanced_text:
                # Text bereinigen
                enhanced_text = enhanced_text.strip().strip('"').strip("'")
                logger.info(f"✅ Text verbessert: {enhanced_text[:50]}...")
                return enhanced_text
            else:
                logger.error("❌ Keine Antwort von OpenAI")
                return None
                
        except Exception as e:
            logger.error(f"💥 Text Enhancement Fehler: {e}")
            return None
    
    async def generate_news_summary(
        self,
        news_items: List[Dict[str, Any]],
        station_type: str = "breaking_news",
        max_items: int = 5
    ) -> Optional[List[str]]:
        """
        Generiert Radio-taugliche News-Zusammenfassungen
        
        Args:
            news_items: Liste von News-Items
            station_type: Station-Typ
            max_items: Maximale Anzahl News
            
        Returns:
            List[str]: Liste von Radio-News oder None bei Fehler
        """
        
        try:
            logger.info(f"📰 Generiere News-Zusammenfassungen für {station_type}")
            
            # Nur die wichtigsten News nehmen
            top_news = news_items[:max_items]
            
            # Station-spezifische Konfiguration
            station_config = self.station_prompts.get(station_type, self.station_prompts['breaking_news'])
            
            # System Prompt
            system_prompt = f"""Du bist {station_config['voice_name']}, Radio-Moderator für {station_type.replace('_', ' ').title()} auf RadioX.

DEIN STIL: {station_config['style']}
NEWS-STIL: {station_config['news_style']}

AUFGABE: Verwandle News-Items in radio-taugliche Meldungen.

REGELN:
1. Jede News max. 2 Sätze
2. Natürlich sprechbar
3. Wichtigste Info zuerst
4. Passend zum Station-Stil
5. Keine Anführungszeichen

Antworte mit einer nummerierten Liste der Radio-News."""

            # News-Items formatieren
            news_text = ""
            for i, item in enumerate(top_news, 1):
                title = item.get('title', 'Unbekannt')
                summary = item.get('summary', item.get('description', ''))
                source = item.get('source', 'Unbekannt')
                
                news_text += f"{i}. {title}\n"
                if summary:
                    news_text += f"   {summary[:200]}...\n"
                news_text += f"   Quelle: {source}\n\n"
            
            # Messages für OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Verwandle diese News in Radio-Meldungen:\n\n{news_text}"}
            ]
            
            # OpenAI Request
            enhanced_news = await self.chat_completion(
                messages=messages,
                model="gpt-4",
                temperature=0.7,
                max_tokens=1000
            )
            
            if enhanced_news:
                # News-Liste extrahieren
                news_lines = enhanced_news.strip().split('\n')
                radio_news = []
                
                for line in news_lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Nummerierung entfernen
                        clean_line = line.split('.', 1)[-1].strip()
                        clean_line = clean_line.lstrip('- ').strip()
                        if clean_line:
                            radio_news.append(clean_line)
                
                logger.info(f"✅ {len(radio_news)} Radio-News generiert")
                return radio_news
            
            else:
                logger.error("❌ Keine News-Antwort von OpenAI")
                return None
                
        except Exception as e:
            logger.error(f"💥 News Summary Fehler: {e}")
            return None


# Convenience Functions für einfache Nutzung
async def enhance_breaking_news_script(raw_script: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Verbessert Breaking News Script"""
    service = OpenAIAPIService()
    return await service.enhance_radio_script(raw_script, "breaking_news")

async def enhance_bitcoin_og_script(raw_script: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Verbessert Bitcoin OG Script"""
    service = OpenAIAPIService()
    return await service.enhance_radio_script(raw_script, "bitcoin_og")

async def generate_radio_news(news_items: List[Dict[str, Any]], station: str = "breaking_news") -> Optional[List[str]]:
    """Generiert Radio-News für Station"""
    service = OpenAIAPIService()
    return await service.generate_news_summary(news_items, station) 