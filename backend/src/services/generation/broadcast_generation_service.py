#!/usr/bin/env python3

"""
Broadcast Generation Service
============================

Service für die Generierung von Broadcast-Skripten mit GPT-4.
Erstellt natürliche Dialoge zwischen Marcel & Jarvis.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from ..infrastructure.supabase_service import SupabaseService

# Import centralized settings
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import get_settings


class BroadcastGenerationService:
    """
    Service für die Generierung von Broadcast-Skripten
    
    Verwendet GPT-4 um natürliche Dialoge zwischen Marcel & Jarvis
    zu erstellen, basierend auf verarbeiteten Content-Daten.
    """
    
    def __init__(self):
        # Load settings centrally
        self.settings = get_settings()
        self.openai_api_key = self.settings.openai_api_key
        self.supabase = SupabaseService()
        
        # V3 ENGLISH BROADCAST STYLES - TIME-BASED PERSONALITIES
        self.broadcast_styles = {
            "morning": {
                "name": "High-Energy Morning",
                "description": "Energetic, motivational, optimistic vibes",
                "marcel_mood": "excited and passionate",
                "jarvis_mood": "witty and sharp",
                "tempo": "fast-paced",
                "duration_target": 8,
                "v3_style": "creative"
            },
            "afternoon": {
                "name": "Professional Afternoon", 
                "description": "Relaxed, informative, professional tone",
                "marcel_mood": "friendly and engaging",
                "jarvis_mood": "analytical and precise",
                "tempo": "medium-paced",
                "duration_target": 10,
                "v3_style": "natural"
            },
            "evening": {
                "name": "Chill Evening",
                "description": "Cozy, thoughtful, conversational",
                "marcel_mood": "thoughtful and warm",
                "jarvis_mood": "philosophical and deep", 
                "tempo": "slow and deliberate",
                "duration_target": 12,
                "v3_style": "natural"
            },
            "night": {
                "name": "Late Night Vibes",
                "description": "Calm, relaxing, introspective atmosphere",
                "marcel_mood": "calm and reflective",
                "jarvis_mood": "mysterious and contemplative",
                "tempo": "very slow and smooth",
                "duration_target": 15,
                "v3_style": "robust"
            }
        }
        
        # GPT-Konfiguration
        self.gpt_config = {
            "model": "gpt-4o",
            "max_tokens": 4000,
            "temperature": 0.8,
            "timeout": 60
        }
    
    async def generate_broadcast(
        self,
        content: Dict[str, Any],
        target_time: Optional[str] = None,
        channel: str = "zurich",
        language: str = "de"
    ) -> Dict[str, Any]:
        """
        Generiert einen kompletten Broadcast
        
        Args:
            content: Verarbeitete Content-Daten
            target_time: Zielzeit für Stil-Anpassung
            channel: Radio-Kanal
            
        Returns:
            Dict mit Broadcast-Daten und Skript
        """
        
        logger.info(f"🎭 Generiere Broadcast für Kanal '{channel}'")
        
        # 1. Broadcast-Stil bestimmen
        broadcast_style = self._determine_broadcast_style(target_time)
        
        # 2. GPT-Prompt erstellen
        gpt_prompt = self._create_gpt_prompt(content, broadcast_style, channel, language)
        
        # 3. Skript mit GPT-4 generieren
        script = await self._generate_script_with_gpt(gpt_prompt)
        
        # 4. Skript post-processing
        processed_script = self._post_process_script(script)
        
        # 5. Broadcast-Metadaten erstellen
        session_id = str(uuid.uuid4())
        estimated_duration = self._estimate_duration(processed_script)
        
        # 6. In Datenbank speichern
        broadcast_data = await self._save_broadcast_to_db(
            session_id=session_id,
            script=processed_script,
            content=content,
            broadcast_style=broadcast_style,
            estimated_duration=estimated_duration,
            channel=channel
        )
        
        result = {
            "session_id": session_id,
            "script_content": processed_script,
            "broadcast_style": broadcast_style["name"],
            "estimated_duration_minutes": estimated_duration,
            "selected_news": content.get("selected_news", []),
            "context_data": content.get("context_data", {}),
            "generation_timestamp": datetime.now().isoformat(),
            "channel": channel
        }
        
        logger.info(f"✅ Broadcast generiert: {session_id} ({estimated_duration} Min)")
        
        return result
    
    async def test_generation(self) -> bool:
        """Testet die Broadcast-Generierung"""
        
        # Test mit minimalen Daten
        test_content = {
            "selected_news": [
                {
                    "title": "Test News",
                    "summary": "Eine Test-Nachricht für die Broadcast-Generierung.",
                    "primary_category": "test"
                }
            ],
            "context_data": {
                "weather": {"formatted": "20°C, sonnig"},
                "crypto": {"formatted": "$100,000 (+2.5%)"}
            }
        }
        
        try:
            result = await self.generate_broadcast(test_content)
            return "session_id" in result and len(result["script_content"]) > 100
        except Exception as e:
            logger.error(f"Broadcast Generation Test Fehler: {e}")
            return False
    
    async def test_broadcast_generation(self) -> bool:
        """Alias für test_generation - für CLI Kompatibilität"""
        return await self.test_generation()
    
    # Private Methods
    
    def _determine_broadcast_style(self, target_time: Optional[str] = None) -> Dict[str, Any]:
        """Bestimmt Broadcast-Stil basierend auf Tageszeit"""
        
        if target_time:
            try:
                hour = int(target_time.split(":")[0])
            except:
                hour = datetime.now().hour
        else:
            hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return self.broadcast_styles["morning"]
        elif 12 <= hour < 17:
            return self.broadcast_styles["afternoon"] 
        elif 17 <= hour < 22:
            return self.broadcast_styles["evening"]
        else:
            return self.broadcast_styles["night"]
    
    def _create_gpt_prompt(
        self, 
        content: Dict[str, Any], 
        broadcast_style: Dict[str, Any],
        channel: str,
        language: str = "en"
    ) -> str:
        """Creates GPT prompt for V3 English script generation"""
        
        if language == "en":
            return self._create_english_prompt(content, broadcast_style, channel)
        else:
            return self._create_german_prompt(content, broadcast_style, channel)
    
    def _create_english_prompt(
        self, 
        content: Dict[str, Any], 
        broadcast_style: Dict[str, Any],
        channel: str
    ) -> str:
        """Creates English V3-optimized prompt"""
        
        # Prepare news context
        news_context = ""
        selected_news = content.get("selected_news", [])
        
        for i, news in enumerate(selected_news, 1):
            news_context += f"{i}. [{news.get('primary_category', 'GENERAL').upper()}] {news.get('title', '')}\n"
            news_context += f"   📰 {news.get('source_name', 'Unknown')} | ⏰ {news.get('hours_old', '?')}h ago\n"
            news_context += f"   📝 {news.get('summary', '')[:200]}...\n\n"
        
        # Context data
        context_data = content.get("context_data", {})
        weather_context = ""
        crypto_context = ""
        
        if context_data.get("weather"):
            weather_context = f"🌡️ Weather: {context_data['weather'].get('formatted', 'unavailable')}"
        
        if context_data.get("crypto"):
            crypto_context = f"₿ Bitcoin: {context_data['crypto'].get('formatted', 'unavailable')}"
        
        # Current time
        current_time = datetime.now()
        time_context = f"⏰ Time: {current_time.strftime('%H:%M')}, {current_time.strftime('%A')}, {current_time.strftime('%B %d, %Y')}"
        
        # Location context
        location_context = self._get_english_location_context(channel)
        
        # V3 OPTIMIZED ENGLISH PROMPT
        gpt_prompt = f"""You are the head producer of RadioX, an innovative Swiss AI radio featuring hosts Marcel (emotional, spontaneous) and Jarvis (analytical, witty AI).

🎙️ **RADIOX ENGLISH V3 BROADCAST GENERATION**

CONTEXT:
{time_context}
🎭 Style: {broadcast_style['name']} - {broadcast_style['description']}
🎯 Marcel: {broadcast_style['marcel_mood']} | Jarvis: {broadcast_style['jarvis_mood']}
⚡ Pacing: {broadcast_style['tempo']}
📍 Channel: {channel.upper()} {location_context}
🎯 Target Duration: {broadcast_style['duration_target']} minutes
🔊 V3 Mode: {broadcast_style['v3_style']} (optimized for ElevenLabs V3)

CURRENT DATA:
{weather_context}
{crypto_context}

AVAILABLE NEWS:
{news_context}

TASK: Create a {broadcast_style['duration_target']}-minute English broadcast script with this structure:

1. **INTRO** (1-2 min)
   - Welcome with current time/weather
   - Preview of today's topics
   - Natural banter between Marcel & Jarvis

2. **MAIN NEWS BLOCK** (3-4 min)
   - Cover major stories in detail
   - Emotional reactions and discussion
   - Marcel: spontaneous feelings, Jarvis: analytical insights

3. **CRYPTO & FINANCE** (1-2 min)
   - Bitcoin update with context
   - Market analysis
   - Jarvis explains, Marcel reacts emotionally

4. **ADDITIONAL NEWS** (2-3 min)
   - Remaining stories more concisely
   - Swiss/local angles where relevant
   - Interactive dialogue between hosts

5. **OUTRO** (1-2 min)
   - Recap key points
   - Preview next show
   - Weather forecast farewell

🎭 **CHARACTER GUIDELINES:**
- **MARCEL**: Enthusiastic, passionate, authentic human emotions
  - Gets EXCITED about Bitcoin/tech news
  - Uses natural English expressions ("Oh my god!", "That's incredible!")
  - Spontaneous reactions and interruptions
  - Warm, relatable personality

- **JARVIS**: Analytical AI, witty, slightly sarcastic
  - Provides data-driven insights
  - Occasional dry humor about human behavior
  - Technical explanations made accessible
  - Philosophical observations

🎯 **V3 OPTIMIZATION NOTES:**
- Use natural conversational English
- Include emotional keywords for V3 enhancement
- Marcel should be more expressive, Jarvis more precise
- Swiss context but international perspective
- Radio-friendly: short sentences, engaging rhythm

📻 **TECHNICAL REQUIREMENTS:**
- Use ALL available news in the script
- Build natural transitions between topics
- Include realistic interruptions and reactions
- Maintain {broadcast_style['duration_target']}-minute target duration
- Swiss references but in English

**FORMAT**: Write as dialogue with clear speaker changes:

MARCEL: [Text]
JARVIS: [Text]
MARCEL: [Text]
...

**START THE SCRIPT IMMEDIATELY - NO INTRODUCTION!**"""

        return gpt_prompt
    
    def _create_german_prompt(
        self, 
        content: Dict[str, Any], 
        broadcast_style: Dict[str, Any],
        channel: str
    ) -> str:
        """Creates German prompt (fallback)"""
        
        # Original German prompt (shortened for space)
        news_context = ""
        selected_news = content.get("selected_news", [])
        
        for i, news in enumerate(selected_news, 1):
            news_context += f"{i}. [{news.get('primary_category', 'GENERAL').upper()}] {news.get('title', '')}\n"
        
        context_data = content.get("context_data", {})
        weather_context = f"🌡️ Wetter: {context_data.get('weather', {}).get('formatted', 'unbekannt')}"
        crypto_context = f"₿ Bitcoin: {context_data.get('crypto', {}).get('formatted', 'unbekannt')}"
        
        return f"""[German broadcast prompt - simplified for fallback]
        
MARCEL: [German content]
JARVIS: [German content]
..."""
    
    def _get_english_location_context(self, channel: str) -> str:
        """Gets English location context for channel"""
        
        location_contexts = {
            "zurich": "- Focus on Zurich and surrounding areas",
            "basel": "- Focus on Basel and Northwestern Switzerland", 
            "bern": "- Focus on Bern and Central Switzerland"
        }
        
        return location_contexts.get(channel, "- Switzerland-wide focus")
    
    async def _generate_script_with_gpt(self, prompt: str) -> str:
        """Generiert Skript mit GPT-4"""
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API Key nicht verfügbar!")
        
        logger.info("🤖 Generiere Skript mit GPT-4...")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.gpt_config["model"],
                "messages": [
                    {
                        "role": "system", 
                        "content": "Du bist ein Experte für Radio-Skripte und erstellst natürliche, emotionale Dialoge zwischen AI-Moderatoren."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": self.gpt_config["max_tokens"],
                "temperature": self.gpt_config["temperature"]
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=self.gpt_config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content'].strip()
                
                logger.info(f"✅ Skript generiert ({len(script)} Zeichen)")
                return script
            else:
                logger.error(f"❌ GPT Request Fehler {response.status_code}: {response.text}")
                raise Exception(f"GPT API Fehler: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Fehler bei Skript-Generierung: {e}")
            raise
    
    def _post_process_script(self, script: str) -> str:
        """Post-Processing des generierten Skripts"""
        
        # Entferne überflüssige Leerzeilen
        lines = script.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Nur nicht-leere Zeilen
                cleaned_lines.append(line)
        
        # Stelle sicher, dass Sprecher-Namen korrekt formatiert sind
        processed_lines = []
        for line in cleaned_lines:
            if line.startswith("MARCEL:") or line.startswith("JARVIS:"):
                processed_lines.append(line)
            elif ":" in line and (line.upper().startswith("MARCEL") or line.upper().startswith("JARVIS")):
                # Korrigiere Formatierung
                if line.upper().startswith("MARCEL"):
                    processed_lines.append("MARCEL: " + line.split(":", 1)[1].strip())
                elif line.upper().startswith("JARVIS"):
                    processed_lines.append("JARVIS: " + line.split(":", 1)[1].strip())
            else:
                # Zeile ohne Sprecher - füge zur letzten Zeile hinzu
                if processed_lines:
                    processed_lines[-1] += " " + line
        
        return '\n'.join(processed_lines)
    
    def _estimate_duration(self, script: str) -> int:
        """Schätzt die Broadcast-Dauer in Minuten"""
        
        # Durchschnittliche Sprechgeschwindigkeit: ~150 Wörter pro Minute
        word_count = len(script.split())
        estimated_minutes = max(1, round(word_count / 150))
        
        return estimated_minutes
    
    async def _save_broadcast_to_db(
        self,
        session_id: str,
        script: str,
        content: Dict[str, Any],
        broadcast_style: Dict[str, Any],
        estimated_duration: int,
        channel: str
    ) -> Dict[str, Any]:
        """Speichert Broadcast in Supabase"""
        
        try:
            # Bereite Daten für JSON-Serialisierung vor
            context_data = content.get("context_data", {})
            
            # Konvertiere datetime-Objekte zu ISO-Strings falls vorhanden
            def serialize_datetime(obj):
                if isinstance(obj, dict):
                    return {k: serialize_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_datetime(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj
            
            serialized_context = serialize_datetime(context_data)
            
            broadcast_data = {
                "session_id": session_id,
                "script_content": script,
                "broadcast_style": broadcast_style["name"],
                "estimated_duration_minutes": estimated_duration,
                "news_count": len(content.get("selected_news", [])),
                "weather_data": serialized_context.get("weather"),
                "crypto_data": serialized_context.get("crypto"),
                "channel": channel,
                "created_at": datetime.now().isoformat()
            }
            
            response = self.supabase.client.table('broadcast_scripts').insert(broadcast_data).execute()
            
            if response.data:
                logger.info(f"✅ Broadcast in DB gespeichert: {session_id}")
                
                # Log the broadcast creation
                log_data = {
                    "session_id": session_id,
                    "event_type": "broadcast_created",
                    "event_data": {
                        "news_count": len(content.get("selected_news", [])),
                        "duration_minutes": estimated_duration,
                        "style": broadcast_style["name"],
                        "channel": channel
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                self.supabase.client.table('broadcast_logs').insert(log_data).execute()
                
                return broadcast_data
            else:
                raise Exception("Fehler beim Speichern in Supabase")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern des Broadcasts: {e}")
            raise
    
    def _get_location_context(self, channel: str) -> str:
        """Holt lokalen Kontext für Kanal"""
        
        location_contexts = {
            "zurich": "- Fokus auf Zürich und Umgebung",
            "basel": "- Fokus auf Basel und Nordwestschweiz", 
            "bern": "- Fokus auf Bern und Mittelland"
        }
        
        return location_contexts.get(channel, "- Schweizweiter Fokus")
    
    # Convenience Methods
    
    async def generate_quick_broadcast(
        self, 
        news_count: int = 3,
        channel: str = "zurich"
    ) -> Dict[str, Any]:
        """Generiert schnell einen Broadcast mit minimalen Daten"""
        
        # Erstelle minimalen Content
        minimal_content = {
            "selected_news": [
                {
                    "title": f"Aktuelle Nachrichten {i}",
                    "summary": f"Zusammenfassung der Nachricht {i} für den schnellen Broadcast.",
                    "primary_category": "general",
                    "source_name": "RadioX",
                    "hours_old": 1
                }
                for i in range(1, news_count + 1)
            ],
            "context_data": {
                "weather": {"formatted": "Aktuelles Wetter nicht verfügbar"},
                "crypto": {"formatted": "Bitcoin-Preis nicht verfügbar"}
            }
        }
        
        return await self.generate_broadcast(minimal_content, channel=channel) 