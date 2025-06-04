"""
RadioX GPT Enhancement Service
Verwandelt rohe Radio-Texte in professionelle, natürlich klingende Radio-Ansagen
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from dataclasses import dataclass
import json

import openai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from root directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


@dataclass
class EnhancedSegment:
    """Veredeltes Radio-Segment"""
    original_content: str
    enhanced_content: str
    segment_type: str
    voice_instructions: str
    timing_notes: str
    metadata: Dict[str, Any]


class GPTEnhancementService:
    """GPT Service für Radio-Text Veredelung"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.error("❌ OpenAI API Key nicht gefunden!")
            logger.info("💡 Prüfe OPENAI_API_KEY in der .env Datei")
            raise ValueError("❌ OpenAI API Key fehlt!")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info("✅ OpenAI Client initialisiert")
        
        # Radio Station Persönlichkeiten
        self.station_personalities = {
            "breaking_news": {
                "voice": "JARVIS",
                "style": "Professionell, autoritativ, AI-artig, präzise",
                "tone": "Seriös aber zugänglich, leicht futuristisch",
                "pace": "Mittleres Tempo, klare Artikulation",
                "personality": "Wie ein intelligenter AI-Assistent der Nachrichten präsentiert"
            },
            "zueri_style": {
                "voice": "Bella",
                "style": "Lokal, freundlich, Schweizer Charme",
                "tone": "Warm, einladend, stolz auf Zürich",
                "pace": "Entspannt, gemütlich",
                "personality": "Wie eine lokale Züricherin die ihre Stadt liebt"
            },
            "bitcoin_og": {
                "voice": "Rachel",
                "style": "Energisch, tech-savvy, Bitcoin-enthusiastisch",
                "tone": "Aufgeregt, optimistisch, rebellisch",
                "pace": "Schnell, dynamisch",
                "personality": "Wie eine Bitcoin-Expertin die für die Revolution brennt"
            }
        }
    
    async def enhance_radio_script(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Veredelt ein komplettes Radio-Skript"""
        logger.info("🤖 Starte GPT-Veredelung des Radio-Skripts...")
        
        station_type = script_data.get('metadata', {}).get('station_type', 'breaking_news')
        segments = script_data.get('segments', [])
        
        enhanced_segments = []
        
        for i, segment in enumerate(segments):
            logger.info(f"🔄 Veredle Segment {i+1}/{len(segments)}: {segment.get('type', 'unknown')}")
            
            enhanced_segment = await self.enhance_segment(
                segment=segment,
                station_type=station_type,
                context={
                    'script_id': script_data.get('script_id'),
                    'target_hour': script_data.get('target_hour'),
                    'total_segments': len(segments),
                    'segment_index': i
                }
            )
            
            if enhanced_segment:
                # Original Segment mit enhanced content updaten
                updated_segment = segment.copy()
                updated_segment['enhanced_content'] = enhanced_segment.enhanced_content
                updated_segment['voice_instructions'] = enhanced_segment.voice_instructions
                updated_segment['timing_notes'] = enhanced_segment.timing_notes
                updated_segment['gpt_enhanced'] = True
                updated_segment['enhancement_metadata'] = enhanced_segment.metadata
                
                enhanced_segments.append(updated_segment)
            else:
                # Fallback: Original Segment beibehalten
                enhanced_segments.append(segment)
        
        # Enhanced Script zusammenstellen
        enhanced_script = script_data.copy()
        enhanced_script['segments'] = enhanced_segments
        enhanced_script['metadata']['gpt_enhanced'] = True
        enhanced_script['metadata']['enhancement_timestamp'] = datetime.utcnow().isoformat()
        enhanced_script['metadata']['enhanced_segments'] = len([s for s in enhanced_segments if s.get('gpt_enhanced')])
        
        logger.info(f"✅ GPT-Veredelung abgeschlossen: {len(enhanced_segments)} Segmente")
        
        return enhanced_script
    
    async def enhance_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any] = None
    ) -> Optional[EnhancedSegment]:
        """Veredelt ein einzelnes Radio-Segment"""
        
        segment_type = segment.get('type', 'unknown')
        original_content = segment.get('content', '')
        
        if not original_content:
            logger.warning(f"⚠️ Leerer Content für {segment_type} Segment")
            return None
        
        try:
            # Segment-spezifische Veredelung
            if segment_type == 'intro':
                return await self._enhance_intro_segment(segment, station_type, context)
            elif segment_type == 'news':
                return await self._enhance_news_segment(segment, station_type, context)
            elif segment_type == 'weather':
                return await self._enhance_weather_segment(segment, station_type, context)
            elif segment_type == 'music':
                return await self._enhance_music_segment(segment, station_type, context)
            elif segment_type == 'tweet':
                return await self._enhance_tweet_segment(segment, station_type, context)
            elif segment_type == 'outro':
                return await self._enhance_outro_segment(segment, station_type, context)
            else:
                logger.warning(f"⚠️ Unbekannter Segment-Typ: {segment_type}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Fehler bei Segment-Veredelung: {e}")
            return None
    
    async def _enhance_intro_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any]
    ) -> EnhancedSegment:
        """Veredelt Intro-Segment"""
        
        personality = self.station_personalities.get(station_type, self.station_personalities['breaking_news'])
        target_hour = context.get('target_hour', '').split('T')[1][:5] if context.get('target_hour') else 'jetzt'
        
        prompt = f"""
Du bist ein professioneller Radio-Moderator für {station_type.replace('_', ' ').title()}.

PERSÖNLICHKEIT: {personality['personality']}
STIL: {personality['style']}
TONFALL: {personality['tone']}
TEMPO: {personality['pace']}

Verwandle diesen rohen Intro-Text in eine professionelle Radio-Ansage:

ORIGINAL: "{segment.get('content', '')}"

KONTEXT:
- Sendezeit: {target_hour}
- Station: {station_type.replace('_', ' ').title()}
- Voice: {personality['voice']}

ANFORDERUNGEN:
- Natürlich und einladend
- Passend zur Station-Persönlichkeit
- Kurz und prägnant (max. 15 Sekunden)
- Keine Füllwörter
- Professioneller Radio-Sound

Antworte nur mit dem verbesserten Text, ohne Anführungszeichen oder Erklärungen.
"""

        response = await self._call_gpt(prompt)
        
        return EnhancedSegment(
            original_content=segment.get('content', ''),
            enhanced_content=response,
            segment_type='intro',
            voice_instructions=f"Voice: {personality['voice']}, Style: {personality['style']}",
            timing_notes="Langsam beginnen, Energie aufbauen",
            metadata={
                'station_personality': personality,
                'enhancement_type': 'intro',
                'target_duration': segment.get('duration_seconds', 8)
            }
        )
    
    async def _enhance_news_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any]
    ) -> EnhancedSegment:
        """Veredelt News-Segment"""
        
        personality = self.station_personalities.get(station_type, self.station_personalities['breaking_news'])
        metadata = segment.get('metadata', {})
        
        prompt = f"""
Du bist ein professioneller Nachrichten-Moderator für {station_type.replace('_', ' ').title()}.

PERSÖNLICHKEIT: {personality['personality']}
STIL: {personality['style']}
TONFALL: {personality['tone']}

Verwandle diese rohe Nachricht in eine professionelle Radio-Nachricht:

ORIGINAL: "{segment.get('content', '')}"

ZUSÄTZLICHE INFOS:
- Quelle: {metadata.get('source', 'N/A')}
- Kategorie: {metadata.get('category', 'N/A')}
- Priorität: {metadata.get('priority', 'N/A')}

ANFORDERUNGEN:
- Professioneller Nachrichtenstil
- Klare, verständliche Sprache
- Wichtigste Info zuerst
- Passend zur Station-Persönlichkeit
- 10-20 Sekunden Sprechzeit
- Keine Quellenangabe im Text (wird automatisch hinzugefügt)

Antworte nur mit dem verbesserten Nachrichtentext, ohne Anführungszeichen oder Erklärungen.
"""

        response = await self._call_gpt(prompt)
        
        return EnhancedSegment(
            original_content=segment.get('content', ''),
            enhanced_content=response,
            segment_type='news',
            voice_instructions=f"Voice: {personality['voice']}, Nachrichtenstil, autoritativ",
            timing_notes="Klare Artikulation, Pausen nach wichtigen Punkten",
            metadata={
                'news_source': metadata.get('source'),
                'news_category': metadata.get('category'),
                'enhancement_type': 'news',
                'target_duration': segment.get('duration_seconds', 15)
            }
        )
    
    async def _enhance_weather_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any]
    ) -> EnhancedSegment:
        """Veredelt Wetter-Segment"""
        
        personality = self.station_personalities.get(station_type, self.station_personalities['breaking_news'])
        metadata = segment.get('metadata', {})
        
        prompt = f"""
Du bist ein Radio-Moderator für {station_type.replace('_', ' ').title()}.

PERSÖNLICHKEIT: {personality['personality']}
STIL: {personality['style']}
TONFALL: {personality['tone']}

Verwandle diesen rohen Wetterbericht in eine natürliche Radio-Ansage:

ORIGINAL: "{segment.get('content', '')}"

WETTER-DETAILS:
- Stadt: {metadata.get('city', 'N/A')}
- Temperatur: {metadata.get('temperature', 'N/A')}°C
- Bedingungen: {metadata.get('condition', 'N/A')}

ANFORDERUNGEN:
- Natürlich und gesprächig
- Passend zur Station-Persönlichkeit
- Kurz und informativ
- Freundlicher Ton
- 15-25 Sekunden Sprechzeit

Antworte nur mit dem verbesserten Wettertext, ohne Anführungszeichen oder Erklärungen.
"""

        response = await self._call_gpt(prompt)
        
        return EnhancedSegment(
            original_content=segment.get('content', ''),
            enhanced_content=response,
            segment_type='weather',
            voice_instructions=f"Voice: {personality['voice']}, freundlich, informativ",
            timing_notes="Entspannt, wie ein Gespräch",
            metadata={
                'weather_city': metadata.get('city'),
                'temperature': metadata.get('temperature'),
                'enhancement_type': 'weather',
                'target_duration': segment.get('duration_seconds', 20)
            }
        )
    
    async def _enhance_music_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any]
    ) -> EnhancedSegment:
        """Veredelt Musik-Segment"""
        
        personality = self.station_personalities.get(station_type, self.station_personalities['breaking_news'])
        metadata = segment.get('metadata', {})
        
        prompt = f"""
Du bist ein Radio-DJ für {station_type.replace('_', ' ').title()}.

PERSÖNLICHKEIT: {personality['personality']}
STIL: {personality['style']}
TONFALL: {personality['tone']}

Verwandle diese rohe Musik-Ansage in eine professionelle DJ-Ansage:

ORIGINAL: "{segment.get('content', '')}"

TRACK-INFO:
- Titel: {metadata.get('track_title', 'N/A')}
- Artist: {metadata.get('artist', 'N/A')}
- Genre: {metadata.get('genre', 'N/A')}

ANFORDERUNGEN:
- Kurz und prägnant (3-8 Sekunden)
- Passend zur Station-Persönlichkeit
- Energie passend zum Genre
- Professioneller DJ-Sound
- Keine langen Erklärungen

Antworte nur mit der verbesserten Musik-Ansage, ohne Anführungszeichen oder Erklärungen.
"""

        response = await self._call_gpt(prompt)
        
        return EnhancedSegment(
            original_content=segment.get('content', ''),
            enhanced_content=response,
            segment_type='music',
            voice_instructions=f"Voice: {personality['voice']}, DJ-Stil, energisch",
            timing_notes="Schnell, über Musik-Intro sprechen",
            metadata={
                'track_title': metadata.get('track_title'),
                'artist': metadata.get('artist'),
                'genre': metadata.get('genre'),
                'enhancement_type': 'music',
                'target_duration': 5  # Kurze Ansage
            }
        )
    
    async def _enhance_tweet_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any]
    ) -> EnhancedSegment:
        """Veredelt Tweet-Segment"""
        
        personality = self.station_personalities.get(station_type, self.station_personalities['breaking_news'])
        metadata = segment.get('metadata', {})
        
        prompt = f"""
Du bist ein Radio-Moderator für {station_type.replace('_', ' ').title()}.

PERSÖNLICHKEIT: {personality['personality']}
STIL: {personality['style']}
TONFALL: {personality['tone']}

Verwandle dieses rohe Tweet-Update in eine professionelle Radio-Ansage:

ORIGINAL: "{segment.get('content', '')}"

TWEET-INFO:
- Author: @{metadata.get('author', 'N/A')}
- Likes: {metadata.get('likes', 0)}
- Retweets: {metadata.get('retweets', 0)}

ANFORDERUNGEN:
- Natürlich und gesprächig
- Passend zur Station-Persönlichkeit
- Social Media Kontext erklären
- 15-25 Sekunden Sprechzeit
- Engagement-Zahlen nur erwähnen wenn beeindruckend

Antworte nur mit dem verbesserten Tweet-Text, ohne Anführungszeichen oder Erklärungen.
"""

        response = await self._call_gpt(prompt)
        
        return EnhancedSegment(
            original_content=segment.get('content', ''),
            enhanced_content=response,
            segment_type='tweet',
            voice_instructions=f"Voice: {personality['voice']}, social media Ton",
            timing_notes="Locker, wie ein Gespräch über Social Media",
            metadata={
                'tweet_author': metadata.get('author'),
                'engagement': {
                    'likes': metadata.get('likes', 0),
                    'retweets': metadata.get('retweets', 0)
                },
                'enhancement_type': 'tweet',
                'target_duration': segment.get('duration_seconds', 20)
            }
        )
    
    async def _enhance_outro_segment(
        self, 
        segment: Dict[str, Any], 
        station_type: str,
        context: Dict[str, Any]
    ) -> EnhancedSegment:
        """Veredelt Outro-Segment"""
        
        personality = self.station_personalities.get(station_type, self.station_personalities['breaking_news'])
        
        prompt = f"""
Du bist ein professioneller Radio-Moderator für {station_type.replace('_', ' ').title()}.

PERSÖNLICHKEIT: {personality['personality']}
STIL: {personality['style']}
TONFALL: {personality['tone']}

Verwandle diesen rohen Outro-Text in eine professionelle Radio-Verabschiedung:

ORIGINAL: "{segment.get('content', '')}"

KONTEXT:
- Station: {station_type.replace('_', ' ').title()}
- Voice: {personality['voice']}

ANFORDERUNGEN:
- Professioneller Abschluss
- Passend zur Station-Persönlichkeit
- Kurz und prägnant (max. 10 Sekunden)
- Einladend für nächste Sendung
- Warmer, abschließender Ton

Antworte nur mit dem verbesserten Outro-Text, ohne Anführungszeichen oder Erklärungen.
"""

        response = await self._call_gpt(prompt)
        
        return EnhancedSegment(
            original_content=segment.get('content', ''),
            enhanced_content=response,
            segment_type='outro',
            voice_instructions=f"Voice: {personality['voice']}, abschließend, warm",
            timing_notes="Langsam ausklingen lassen",
            metadata={
                'station_personality': personality,
                'enhancement_type': 'outro',
                'target_duration': segment.get('duration_seconds', 6)
            }
        )
    
    async def _call_gpt(self, prompt: str, model: str = "gpt-4") -> str:
        """Ruft GPT API auf"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Du bist ein professioneller Radio-Texter. Antworte immer nur mit dem gewünschten Text, ohne zusätzliche Erklärungen oder Anführungszeichen."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"💥 GPT API Fehler: {e}")
            raise


# Convenience Functions
async def enhance_radio_script(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """Veredelt ein komplettes Radio-Skript"""
    service = GPTEnhancementService()
    return await service.enhance_radio_script(script_data)

async def enhance_segment(
    segment: Dict[str, Any], 
    station_type: str,
    context: Dict[str, Any] = None
) -> Optional[EnhancedSegment]:
    """Veredelt ein einzelnes Radio-Segment"""
    service = GPTEnhancementService()
    return await service.enhance_segment(segment, station_type, context) 