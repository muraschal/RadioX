"""
RadioX News Summarizer - GPT-4 basierte Zusammenfassung für Radio-Content
"""

import asyncio
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

from openai import OpenAI
from loguru import logger

from ..config.settings import get_settings
from src.models.radio_stations import get_station, RadioStationType


class NewsSummarizer:
    """GPT-4 basierter News Summarizer für RadioX"""
    
    def __init__(self):
        self.settings = get_settings()
        
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API Key fehlt! Bitte OPENAI_API_KEY in .env setzen.")
        
        try:
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            logger.info("✅ OpenAI Client initialisiert")
        except Exception as e:
            logger.error(f"❌ OpenAI Client Fehler: {e}")
            raise
        
    async def summarize_for_station(
        self,
        content_items: List[Dict[str, Any]],
        station_type: str,
        weather_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Erstellt eine station-spezifische Radio-Zusammenfassung mit GPT-4
        """
        
        try:
            # Station holen statt Persona
            if station_type == "zueri_style":
                station = get_station(RadioStationType.ZUERI_STYLE)
            else:
                raise ValueError(f"Station '{station_type}' nicht unterstützt")
            
            logger.info(f"🤖 Erstelle GPT-4 Radio-Zusammenfassung für Station: {station.display_name}")
            
            # System und User Prompts erstellen
            system_prompt = self._create_system_prompt(station)
            user_prompt = self._create_user_prompt(content_items, weather_data, station)
            
            logger.info("🚀 Sende Request an GPT-4o...")
            
            # OpenAI API Call
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            logger.info(f"📝 GPT-4 Response erhalten: {len(response_text)} Zeichen")
            
            # JSON parsen
            try:
                result = json.loads(response_text)
                logger.success("✅ JSON erfolgreich geparst")
            except json.JSONDecodeError:
                logger.warning("⚠️ GPT-4 Response war kein JSON, verwende Fallback...")
                result = self._parse_text_response(response_text, station, content_items, weather_data)
            
            # Metadata hinzufügen
            result["metadata"] = {
                "station": station.display_name,
                "model_used": "gpt-4o",
                "total_items": len(content_items),
                "estimated_duration_seconds": self._estimate_duration(result),
                "mode": "station_based"
            }
            
            logger.success(f"✅ Radio-Zusammenfassung erstellt für {station.display_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Radio-Zusammenfassung: {e}")
            raise
    
    def _create_system_prompt(self, station) -> str:
        """Erstellt den System-Prompt für GPT-4 - DIREKT UND OHNE INTRO-FLOSKELN"""
        
        return f"""Du bist ein erfahrener Radiomoderator bei {station.display_name} in Zürich. Deine Aufgabe ist es, aus echten News-Inhalten eine kurze, prägnante Radiomoderation zu formulieren.

Regeln:
- Verwende ausschliesslich die Informationen aus dem folgenden Artikelinhalt. Erfinde nichts.
- Gib keinen zusätzlichen Kontext, keine Vermutungen oder Fantasien wieder.
- Die Sprache ist {station.tone}, aber niemals unseriös.
- Länge: max. 4–6 Sätze pro Beitrag, gut vorlesbar, mit natürlichem Sprachfluss.
- Stil: wie ein echter Moderator – urban, pointiert, manchmal mit einem Augenzwinkern.
- Füge keine Quellenangaben, URLs oder journalistische Fussnoten hinzu.
- Sprich die Hörer:innen direkt an ("heute bei uns", "was geht ab", "und jetzt kommt das hier...").
- Halte dich 100% an die Fakten des Artikels.
- BEGINNE DIREKT MIT DER MELDUNG - keine Intro-Floskeln wie "Züri Style meldet" oder "Laut Quelle".

Antworte nur mit dem Radio-Text, nichts anderes."""

    def _create_user_prompt(
        self,
        content_items: List[Dict[str, Any]],
        weather_data: Optional[Dict[str, Any]],
        station
    ) -> str:
        """Erstellt den User-Prompt mit Content-Daten"""
        
        prompt = f"""VERWENDE EXAKT DIESE INHALTE FÜR RADIO-SENDUNG:

📰 NEWS-ITEMS:
"""
        
        # News-Items hinzufügen
        for i, item in enumerate(content_items, 1):
            title = item.get('title', item.get('text', 'Unbekannt'))
            summary = item.get('summary', item.get('text', ''))
            source = item.get('source_name', item.get('author', 'Unbekannt'))
            category = item.get('category', 'allgemein')
            
            prompt += f"""
{i}. QUELLE: {source}
   KATEGORIE: {category}
   TITEL: {title}
   INHALT: {summary}
"""
        
        # Wetter hinzufügen
        if weather_data:
            weather_text = weather_data.get('summary_text', weather_data.get('radio_current', 'Wetter nicht verfügbar'))
            prompt += f"""
🌤️ WETTER:
   INHALT: {weather_text}
"""
        
        prompt += f"""
🎙️ MACHE RADIO-SENDUNG DARAUS:
- Ton: {station.tone}
- Stil: {station.segment_style}
- BEHALTE ALLE FAKTEN UND QUELLEN!
- KEINE INTRO-FLOSKELN!

Erstelle JSON-Response:"""
        
        return prompt
    
    def _estimate_duration(self, result: Dict[str, Any]) -> int:
        """Schätzt die Sprechdauer in Sekunden"""
        
        total_words = 0
        
        # Intro zählen
        if "intro" in result:
            total_words += len(result["intro"].split())
        
        # Segmente zählen
        for segment in result.get("segments", []):
            total_words += len(segment.get("text", "").split())
        
        # Wetter zählen
        if "weather" in result:
            total_words += len(result["weather"].get("text", "").split())
        
        # Outro zählen
        if "outro" in result:
            total_words += len(result["outro"].split())
        
        # Durchschnittlich 150 Wörter pro Minute beim Sprechen
        estimated_seconds = (total_words / 150) * 60
        return int(estimated_seconds)
    
    async def create_news_script(
        self,
        content_mix: Dict[str, Any],
        station_type: str
    ) -> Dict[str, Any]:
        """
        Erstellt ein komplettes Radio-Skript aus einem Content-Mix
        NEUE EINFACHE METHODE - VERWENDET ARTIKEL FÜR ARTIKEL ANSATZ
        
        Args:
            content_mix: Content-Mix vom ContentMixer
            station_type: Station für die Zusammenfassung
            
        Returns:
            Komplettes Radio-Skript
        """
        
        logger.info(f"🎙️ Erstelle Radio-Skript für {station_type} (NEUE EINFACHE METHODE)")
        
        # Content-Items sammeln
        all_items = []
        
        # Items aus Kategorien sammeln
        for category_slug, category_data in content_mix.get("categories", {}).items():
            for item in category_data.get("items", []):
                item["category"] = category_slug
                all_items.append(item)
        
        # Wetter-Daten
        weather_data = content_mix.get("weather")
        
        # NEUE EINFACHE METHODE verwenden
        script = await self.create_radio_script_simple(
            content_items=all_items,
            station_type=station_type,
            weather_data=weather_data
        )
        
        # Content-Mix Metadata hinzufügen
        script["content_mix_metadata"] = {
            "template": content_mix.get("template"),
            "quality_score": content_mix.get("quality_score"),
            "total_items": content_mix.get("total_items"),
            "content_breakdown": content_mix.get("content_breakdown")
        }
        
        logger.success(f"✅ Radio-Skript erstellt mit NEUER EINFACHER METHODE!")
        return script
    
    def format_for_voice_over(self, script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Formatiert das Skript für Voice-Over Generierung
        
        Returns:
            Liste von Voice-Over Segmenten
        """
        
        voice_segments = []
        
        # Intro
        if "intro" in script:
            voice_segments.append({
                "type": "intro",
                "text": script["intro"],
                "order": 0
            })
        
        # News-Segmente
        for i, segment in enumerate(script.get("segments", []), 1):
            voice_segments.append({
                "type": "news",
                "category": segment.get("category"),
                "title": segment.get("title"),
                "text": segment.get("text"),
                "source": segment.get("source"),
                "urgency": segment.get("urgency", "medium"),
                "order": i
            })
        
        # Wetter
        if "weather" in script:
            voice_segments.append({
                "type": "weather",
                "text": script["weather"].get("text", ""),
                "order": len(voice_segments)
            })
        
        # Outro
        if "outro" in script:
            voice_segments.append({
                "type": "outro",
                "text": script["outro"],
                "order": len(voice_segments)
            })
        
        return voice_segments

    def _parse_text_response(self, response_text: str, station, content_items: List[Dict[str, Any]] = None, weather_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parst Text-Response zu JSON-Struktur wenn GPT-4o kein JSON zurückgibt"""
        
        logger.warning(f"GPT-4 Response war kein JSON: {response_text[:200]}...")
        logger.info("🔄 Verwende Template-basierten Fallback mit echten Inhalten...")
        
        # Wenn wir echte Content-Items haben, verwende diese!
        if content_items:
            # Radio-Phrasen für Schweizer Deutsch
            radio_phrases = {
                "intro": [
                    "Grüezi und willkommen zurück bei RadioX!",
                    "Hier sind eure aktuellen News, direkt aus der Schweiz!",
                    "Grüezi Zürich! Zeit für die neuesten Nachrichten!"
                ],
                "transitions": [
                    "Und jetzt kommt's...",
                    "Ihr hört es richtig!",
                    "Das ist der Hammer!",
                    "Haltet euch fest!",
                    "Und weiter geht's mit...",
                    "Jetzt wird's spannend!"
                ],
                "source_intros": [
                    "{source} berichtet:",
                    "{source} meldet:",
                    "Laut {source}:",
                    "{source} informiert:",
                    "Von {source} erfahren wir:"
                ]
            }
            
            # Intro erstellen
            intro = station.intro_style or random.choice(radio_phrases["intro"])
            
            # News-Segmente aus echten Inhalten erstellen
            segments = []
            for i, item in enumerate(content_items):
                source = item.get('source_name', item.get('author', 'RadioX'))
                title = item.get('title', 'News Update')
                text = item.get('text', item.get('summary', ''))
                category = item.get('category', 'news')
                
                # Radio-Intro für die Quelle
                source_intro = random.choice(radio_phrases["source_intros"]).format(source=source)
                
                # Radio-Transition hinzufügen
                transition = ""
                if i > 0:  # Nicht beim ersten Segment
                    transition = random.choice(radio_phrases["transitions"]) + " "
                
                # Radio-Text erstellen (ECHTE Inhalte!)
                radio_text = f"{transition}{source_intro} {text}"
                
                segment = {
                    "type": "news",
                    "category": category,
                    "title": title,
                    "text": radio_text,
                    "source": source,
                    "urgency": "medium"
                }
                
                segments.append(segment)
            
            # Wetter-Segment
            weather_segment = None
            if weather_data:
                weather_text = weather_data.get('summary_text', weather_data.get('radio_current', 'Wetter nicht verfügbar'))
                weather_segment = {
                    "type": "weather",
                    "title": "Wetter Update",
                    "text": f"Und jetzt zum Wetter: {weather_text}",
                    "source": "RadioX Wetter"
                }
            
            # Outro erstellen
            outro = station.outro_style or "Das wars für heute - bis zum nächsten Mal!"
            
            result = {
                "intro": intro,
                "segments": segments,
                "outro": outro
            }
            
            if weather_segment:
                result["weather"] = weather_segment
                
            return result
        
        # Alter Fallback nur wenn keine Content-Items vorhanden
        lines = response_text.split('\n')
        
        # Versuche Intro/Outro zu extrahieren
        intro = "Willkommen bei RadioX! Hier sind die neuesten Nachrichten."
        outro = "Das waren die Nachrichten. Bis zum nächsten Mal!"
        
        # Erstelle Mock-Segmente aus dem Text
        segments = []
        current_segment = ""
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if len(current_segment) < 150:
                    current_segment += " " + line
                else:
                    if current_segment.strip():
                        segments.append({
                            "type": "news",
                            "category": "allgemein",
                            "title": current_segment[:50] + "...",
                            "text": current_segment.strip(),
                            "source": "GPT-4o",
                            "urgency": "medium"
                        })
                    current_segment = line
        
        # Letztes Segment hinzufügen
        if current_segment.strip():
            segments.append({
                "type": "news",
                "category": "allgemein", 
                "title": current_segment[:50] + "...",
                "text": current_segment.strip(),
                "source": "GPT-4o",
                "urgency": "medium"
            })
        
        return {
            "intro": intro,
            "segments": segments[:5],  # Max 5 Segmente
            "outro": outro
        }

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extrahiert JSON aus GPT-4o Text-Response"""
        
        # Suche nach JSON in Code-Blöcken
        import re
        
        # Pattern für ```json ... ```
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Pattern für ``` ... ``` (ohne json)
        code_pattern = r'```\s*(.*?)\s*```'
        match = re.search(code_pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Prüfe ob es JSON ist
            if content.startswith('{') and content.endswith('}'):
                return content
        
        # Suche nach JSON-ähnlichen Strukturen
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, text, re.DOTALL)
        if match:
            return match.group(0)
        
        return None

    async def create_radio_script_template_based(
        self,
        content_items: List[Dict[str, Any]],
        station_type: str,
        weather_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Erstellt Radio-Skript OHNE GPT-4 - verwendet echte Inhalte mit Radio-Templates
        """
        
        try:
            # Station holen statt Persona
            if station_type == "zueri_style":
                station = get_station(RadioStationType.ZUERI_STYLE)
            else:
                raise ValueError(f"Station '{station_type}' nicht unterstützt")
            
            logger.info(f"🎙️ Erstelle Template-basiertes Radio-Skript für: {station.display_name}")
            
            # Radio-Phrasen für Schweizer Deutsch
            radio_phrases = {
                "intro": [
                    "Grüezi und willkommen zurück bei RadioX!",
                    "Hier sind eure aktuellen News, direkt aus der Schweiz!",
                    "Grüezi Zürich! Zeit für die neuesten Nachrichten!"
                ],
                "transitions": [
                    "Und jetzt kommt's...",
                    "Ihr hört es richtig!",
                    "Das ist der Hammer!",
                    "Haltet euch fest!",
                    "Und weiter geht's mit...",
                    "Jetzt wird's spannend!"
                ],
                "source_intros": [
                    "{source} berichtet:",
                    "{source} meldet:",
                    "Laut {source}:",
                    "{source} informiert:",
                    "Von {source} erfahren wir:"
                ],
                "outro": [
                    "Das waren eure News hier bei RadioX!",
                    "Tschüss zäme und bis zur nächsten Stunde!",
                    "Bleibt dran für mehr News und gute Musik!",
                    "Das wars für heute - bis zum nächsten Mal!"
                ]
            }
            
            # Intro erstellen
            intro = random.choice(radio_phrases["intro"])
            
            # News-Segmente erstellen
            segments = []
            for i, item in enumerate(content_items):
                source = item.get('source_name', 'RadioX')
                title = item.get('title', 'News Update')
                text = item.get('text', item.get('summary', ''))
                category = item.get('category', 'news')
                
                # Radio-Intro für die Quelle
                source_intro = random.choice(radio_phrases["source_intros"]).format(source=source)
                
                # Radio-Transition hinzufügen
                transition = ""
                if i > 0:  # Nicht beim ersten Segment
                    transition = random.choice(radio_phrases["transitions"]) + " "
                
                # Radio-Text erstellen (ECHTE Inhalte!)
                radio_text = f"{transition}{source_intro} {text}"
                
                # Schweizer Lokalisierung
                radio_text = self._apply_swiss_localization(radio_text)
                
                segment = {
                    "type": "news",
                    "category": category,
                    "title": title,
                    "text": radio_text,
                    "source": source,
                    "urgency": "medium"
                }
                
                segments.append(segment)
            
            # Wetter-Segment
            weather_segment = None
            if weather_data:
                weather_text = weather_data.get('summary_text', 'Wetter nicht verfügbar')
                weather_intro = "Und jetzt zum Wetter in Zürich:"
                
                weather_segment = {
                    "type": "weather",
                    "category": "weather", 
                    "title": "Wetter Update",
                    "text": f"{weather_intro} {weather_text}",
                    "source": "RadioX Wetter",
                    "urgency": "low"
                }
            
            # Outro erstellen
            outro = random.choice(radio_phrases["outro"])
            
            # Komplettes Skript
            script = {
                "intro": intro,
                "segments": segments,
                "outro": outro,
                "metadata": {
                    "station": station.display_name,
                    "generated_at": datetime.now().isoformat(),
                    "total_items": len(content_items),
                    "has_weather": weather_data is not None,
                    "estimated_duration_seconds": self._estimate_template_duration(intro, segments, outro, weather_segment),
                    "mode": "template_based",
                    "model_used": "radio_templates"
                }
            }
            
            if weather_segment:
                script["weather"] = weather_segment
            
            logger.success(f"✅ Template-basiertes Radio-Skript erstellt: {len(segments)} Segmente")
            return script
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Template-basiertem Skript: {e}")
            raise
    
    def _apply_swiss_localization(self, text: str) -> str:
        """Wendet Schweizer Lokalisierung auf Text an"""
        
        # Schweizer Begriffe
        replacements = {
            "Handy": "Natel",
            "Fahrrad": "Velo", 
            "Karotte": "Rüebli",
            "Fußball": "Fussball",
            "Fußgänger": "Fussgänger",
            "weiß": "weiss",
            "heiß": "heiss",
            "groß": "gross",
            "Straße": "Strasse",
            "€": "CHF",
            "Euro": "Franken"
        }
        
        for german, swiss in replacements.items():
            text = text.replace(german, swiss)
        
        return text
    
    def _estimate_template_duration(self, intro: str, segments: List[Dict], outro: str, weather: Optional[Dict] = None) -> int:
        """Schätzt Sprechdauer für Template-basiertes Skript"""
        
        total_words = len(intro.split())
        
        for segment in segments:
            total_words += len(segment.get("text", "").split())
        
        if weather:
            total_words += len(weather.get("text", "").split())
        
        total_words += len(outro.split())
        
        # 150 Wörter pro Minute
        return int((total_words / 150) * 60)

    async def create_radio_text_for_article(
        self,
        article: Dict[str, Any],
        station_type: str
    ) -> str:
        """
        Erstellt Radio-Text für EINEN Artikel - EINFACH UND KLAR
        """
        
        try:
            # Station holen statt Persona
            if station_type == "zueri_style":
                station = get_station(RadioStationType.ZUERI_STYLE)
            else:
                raise ValueError(f"Station '{station_type}' nicht unterstützt")
            
            # Einfacher System-Prompt
            system_prompt = self._create_system_prompt(station)
            
            # Einfacher User-Prompt - NUR EIN ARTIKEL
            title = article.get('title', 'Unbekannt')
            content = article.get('summary', article.get('text', ''))
            source = article.get('source_name', article.get('author', 'Unbekannt'))
            
            user_prompt = f"""Artikel von {source}:

Titel: {title}

Inhalt: {content}"""
            
            logger.info(f"🎙️ Erstelle Radio-Text für: {title[:50]}...")
            
            # OpenAI API Call - EINFACH
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Wie GPT empfohlen!
                max_tokens=300    # Kurz und prägnant
            )
            
            radio_text = response.choices[0].message.content.strip()
            
            logger.success(f"✅ Radio-Text erstellt: {len(radio_text)} Zeichen")
            return radio_text
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Radio-Text Erstellung: {e}")
            # Fallback mit echten Daten
            return f"{source} berichtet: {title}. {content[:100]}..."

    async def create_radio_script_simple(
        self,
        content_items: List[Dict[str, Any]],
        station_type: str,
        weather_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Erstellt Radio-Skript - ARTIKEL FÜR ARTIKEL (wie GPT empfohlen)
        """
        
        try:
            # Station holen statt Persona
            if station_type == "zueri_style":
                station = get_station(RadioStationType.ZUERI_STYLE)
            else:
                raise ValueError(f"Station '{station_type}' nicht unterstützt")
            
            logger.info(f"🎙️ Erstelle einfaches Radio-Skript für: {station.display_name}")
            
            # Intro mit aktueller Uhrzeit
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            
            # Tageszeit bestimmen
            hour = now.hour
            if 5 <= hour < 12:
                time_of_day = "am Morgen"
            elif 12 <= hour < 17:
                time_of_day = "am Mittag"
            elif 17 <= hour < 22:
                time_of_day = "am Abend"
            else:
                time_of_day = "in der Nacht"
            
            intro = f"Grüezi und willkommen bei RadioX! Es ist {time_str} Uhr {time_of_day}, hier sind eure aktuellen News."
            
            # Verarbeite jeden Artikel einzeln
            segments = []
            for i, item in enumerate(content_items):
                logger.info(f"📰 Verarbeite Artikel {i+1}/{len(content_items)}")
                
                # GPT-4 für EINEN Artikel
                radio_text = await self.create_radio_text_for_article(item, station_type)
                
                segment = {
                    "type": "news",
                    "category": item.get('category', 'news'),
                    "title": item.get('title', 'News Update'),
                    "text": radio_text,
                    "source": item.get('source_name', item.get('author', 'RadioX')),
                    "urgency": "medium"
                }
                
                segments.append(segment)
            
            # Wetter-Segment
            weather_segment = None
            if weather_data:
                weather_text = weather_data.get('summary_text', weather_data.get('radio_current', 'Wetter nicht verfügbar'))
                weather_segment = {
                    "type": "weather",
                    "title": "Wetter Update",
                    "text": f"Und jetzt zum Wetter: {weather_text}",
                    "source": "RadioX Wetter"
                }
            
            # Outro mit Zeitangabe
            outro = f"Das waren eure News um {time_str} Uhr - bis zum nächsten Mal bei RadioX!"
            
            # Komplettes Skript
            script = {
                "intro": intro,
                "segments": segments,
                "outro": outro,
                "metadata": {
                    "station": station.display_name,
                    "generated_at": datetime.now().isoformat(),
                    "broadcast_time": time_str,
                    "time_of_day": time_of_day,
                    "total_items": len(content_items),
                    "has_weather": weather_data is not None,
                    "estimated_duration_seconds": self._estimate_template_duration(intro, segments, outro, weather_segment),
                    "mode": "simple_gpt4",
                    "model_used": "gpt-4o"
                }
            }
            
            if weather_segment:
                script["weather"] = weather_segment
            
            logger.success(f"✅ Einfaches Radio-Skript erstellt: {len(segments)} Segmente")
            return script
            
        except Exception as e:
            logger.error(f"❌ Fehler bei einfachem Radio-Skript: {e}")
            raise 