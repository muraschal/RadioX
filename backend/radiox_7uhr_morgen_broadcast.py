#!/usr/bin/env python3

"""
RadioX 7:00 Morgen-Broadcast - Frische Start in den Tag
Marcel & Jarvis präsentieren die Morgen-News mit News-Deduplication
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import requests
import os
import json
import tempfile
import shutil
import base64
import glob
import hashlib
import re
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, COMM

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.rss_parser import RSSParser
from src.services.weather_service import WeatherService
from src.services.coinmarketcap_service import CoinMarketCapService
from src.services.news_summarizer import NewsSummarizer


class NewsDeduplicationSystem:
    """System zur Vermeidung von doppelten News"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.used_news_cache = set()
        self.load_used_news()
    
    def load_used_news(self):
        """Lädt alle bereits verwendeten News aus Info-Dateien"""
        print("📚 LADE BEREITS VERWENDETE NEWS")
        print("-" * 40)
        
        info_files = glob.glob(str(self.output_dir / "RadioX_Final_Info_*.txt"))
        
        for info_file in info_files:
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extrahiere News-Topics
                if "NEWS TOPICS:" in content:
                    topics_section = content.split("NEWS TOPICS:")[1].split("SCRIPT:")[0]
                    for line in topics_section.strip().split('\n'):
                        if line.strip() and line.startswith('- '):
                            news_item = line.strip()[2:]  # Entferne "- "
                            news_hash = self.hash_news(news_item)
                            self.used_news_cache.add(news_hash)
                            print(f"   📰 Bereits verwendet: {news_item[:50]}...")
                            
            except Exception as e:
                print(f"   ❌ Fehler beim Lesen von {info_file}: {e}")
        
        print(f"   ✅ {len(self.used_news_cache)} bereits verwendete News geladen")
    
    def hash_news(self, news_text):
        """Erstellt Hash für News-Text"""
        # Normalisiere Text für bessere Deduplication
        normalized = re.sub(r'\s+', ' ', news_text.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Entferne Satzzeichen
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def filter_new_news(self, news_items):
        """Filtert nur neue, noch nicht verwendete News"""
        print("🔍 FILTERE NEUE NEWS")
        print("-" * 40)
        
        new_news = []
        for news in news_items:
            news_hash = self.hash_news(news['title'] + ' ' + news.get('description', ''))
            
            if news_hash not in self.used_news_cache:
                new_news.append(news)
                self.used_news_cache.add(news_hash)  # Markiere als verwendet
                print(f"   ✅ NEU: {news['title'][:50]}...")
            else:
                print(f"   ❌ BEREITS VERWENDET: {news['title'][:50]}...")
        
        print(f"   📊 {len(new_news)} neue News von {len(news_items)} gefunden")
        return new_news


class RadioX7UhrMorgenBroadcast:
    """7:00 Morgen-Broadcast mit Marcel & Jarvis"""
    
    def __init__(self):
        # ElevenLabs API
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY nicht gefunden!")
        
        # OpenAI API
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY nicht gefunden!")
        
        # Voice IDs
        self.marcel_voice_id = "owi9KfbgBi6A987h5eJH"  # Deine deutsche Stimme
        self.jarvis_voice_id = "dmLlPcdDHenQXbfM5tee"  # AI-Style deutsch
        
        # Output Directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Services
        self.rss_parser = RSSParser()
        self.weather_service = WeatherService()
        self.crypto_service = CoinMarketCapService()  # Bitcoin-only Service
        self.news_summarizer = NewsSummarizer()
        
        # News Deduplication System
        self.news_dedup = NewsDeduplicationSystem(self.output_dir)
        
        # Broadcast Structure Variations
        self.broadcast_structures = self.define_broadcast_structures()
        
        print("🌅 RadioX 7:00 Morgen-Broadcast initialisiert")
    
    def define_broadcast_structures(self):
        """Definiert verschiedene Broadcast-Strukturen für Abwechslung"""
        
        structures = {
            "classic_morning": {
                "name": "Klassischer Morgen",
                "description": "Kompakter traditioneller Aufbau",
                "structure": [
                    "MARCEL: Kurze Begrüßung 'Guten Morgen Zürich, 7 Uhr'",
                    "JARVIS: Knapper Gruß, direkt zu Bitcoin-Fakten",
                    "MARCEL: Wetter kompakt in einem Satz",
                    "NEWS-BLOCK: Marcel startet mit wichtigster News",
                    "NEWS-BLOCK: Jarvis übernimmt zweite News sachlich",
                    "NEWS-BLOCK: Marcel führt durch restliche News",
                    "MARCEL: Kurze Verabschiedung"
                ]
            },
            
            "news_first": {
                "name": "News First",
                "description": "Direkt mit Top-News, kein Smalltalk",
                "structure": [
                    "MARCEL: Sofort wichtigste News + kurze Begrüßung",
                    "JARVIS: Sachlicher Kommentar zur Top-News",
                    "MARCEL: Weitere News ohne Umschweife",
                    "JARVIS: Bitcoin-Fakten eingeworfen",
                    "MARCEL: Wetter in einem Satz",
                    "NEWS-BLOCK: Jarvis führt durch restliche News",
                    "MARCEL: Direkte Verabschiedung"
                ]
            },
            
            "bitcoin_focus": {
                "name": "Bitcoin-Fokus",
                "description": "Bitcoin sachlich, dann News",
                "structure": [
                    "JARVIS: Bitcoin-Preis und Trend sachlich",
                    "MARCEL: Kurze Begrüßung, direkt zu News",
                    "MARCEL: Wetter kompakt",
                    "NEWS-BLOCK: Jarvis startet mit Tech-News",
                    "NEWS-BLOCK: Marcel übernimmt lokale News",
                    "JARVIS: Kurzer Bitcoin-Ausblick ohne Hype",
                    "MARCEL: Kompakte Verabschiedung"
                ]
            },
            
            "rapid_info": {
                "name": "Rapid Info",
                "description": "Maximale Informationsdichte",
                "structure": [
                    "MARCEL: Blitz-Begrüßung",
                    "JARVIS: Bitcoin-Preis in einem Satz",
                    "MARCEL: Wetter, sofort zu News",
                    "NEWS-BLOCK: Rapid-Fire News ohne Umschweife",
                    "JARVIS: Kurzer Fakten-Kommentar",
                    "MARCEL: News-Fortsetzung",
                    "MARCEL: Schnelle Verabschiedung"
                ]
            },
            
            "fact_focus": {
                "name": "Fakten-Fokus",
                "description": "Reine Information, minimaler Smalltalk",
                "structure": [
                    "MARCEL: Begrüßung + sofort erste News",
                    "JARVIS: Sachliche Einordnung",
                    "MARCEL: Wetter-Fakten",
                    "JARVIS: Bitcoin-Daten ohne Emotion",
                    "NEWS-BLOCK: Abwechselnde sachliche News-Moderation",
                    "MARCEL: Fakten-basierte Verabschiedung"
                ]
            }
        }
        
        return structures
    
    def select_broadcast_structure(self):
        """Wählt eine Broadcast-Struktur basierend auf vorherigen Sendungen"""
        
        print("🎭 WÄHLE BROADCAST-STRUKTUR")
        print("-" * 40)
        
        # Lade vorherige Strukturen aus Info-Dateien
        used_structures = set()
        info_files = glob.glob(str(self.output_dir / "RadioX_Final_Info_*.txt"))
        
        for info_file in info_files[-5:]:  # Nur letzte 5 Sendungen prüfen
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "STRUKTUR:" in content:
                        structure_line = content.split("STRUKTUR:")[1].split("\n")[0]
                        if structure_line.strip():
                            used_structures.add(structure_line.strip())
            except:
                pass
        
        # Wähle eine Struktur, die in den letzten 5 Sendungen nicht verwendet wurde
        available_structures = []
        for key, structure in self.broadcast_structures.items():
            if structure["name"] not in used_structures:
                available_structures.append((key, structure))
        
        # Falls alle verwendet wurden, nimm eine zufällige
        if not available_structures:
            available_structures = list(self.broadcast_structures.items())
        
        # Zufällige Auswahl
        selected_key, selected_structure = random.choice(available_structures)
        
        print(f"   🎯 Gewählte Struktur: {selected_structure['name']}")
        print(f"   📝 Beschreibung: {selected_structure['description']}")
        print(f"   🚫 Vermiedene Strukturen: {', '.join(used_structures) if used_structures else 'Keine'}")
        
        return selected_key, selected_structure
    
    def load_last_script(self):
        """Lädt das letzte Script als Referenz für Variation"""
        
        print("📜 LADE LETZTES SCRIPT ALS REFERENZ")
        print("-" * 40)
        
        info_files = glob.glob(str(self.output_dir / "RadioX_Final_Info_*.txt"))
        
        if not info_files:
            print("   ℹ️ Kein vorheriges Script gefunden")
            return None
        
        # Sortiere nach Datum (neueste zuerst)
        info_files.sort(reverse=True)
        last_info_file = info_files[0]
        
        try:
            with open(last_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extrahiere Script-Teil
            if "SCRIPT:" in content:
                script_section = content.split("SCRIPT:")[1]
                if "SEGMENTE:" in script_section:
                    script_section = script_section.split("SEGMENTE:")[0]
                
                script = script_section.strip()
                
                # Extrahiere auch verwendete Struktur
                used_structure = "Unbekannt"
                if "STRUKTUR:" in content:
                    structure_line = content.split("STRUKTUR:")[1].split("\n")[0].strip()
                    used_structure = structure_line
                
                print(f"   ✅ Letztes Script geladen ({len(script)} Zeichen)")
                print(f"   🎭 Letzte Struktur: {used_structure}")
                
                return {
                    'script': script,
                    'structure': used_structure,
                    'file': last_info_file
                }
            else:
                print("   ❌ Kein Script-Bereich gefunden")
                return None
                
        except Exception as e:
            print(f"   ❌ Fehler beim Laden: {e}")
            return None
    
    async def collect_fresh_content(self):
        """Sammelt komplett frische Inhalte mit erweiterten Quellen"""
        
        print("📰 SAMMLE FRISCHE MORGEN-INHALTE (ERWEITERT)")
        print("-" * 40)
        
        # RSS News sammeln mit erweiterten Quellen
        try:
            # LOKALE SCHWEIZER NEWS
            local_news = await self.rss_parser.get_latest_news(
                sources=["20min", "nzz", "tagesanzeiger", "zueritoday", "telezueri"],
                categories=["schweiz", "wirtschaft", "zurich", "lokale_news_schweiz"],
                max_items=50
            )
            print(f"   🏔️ {len(local_news)} lokale Schweizer News geladen")
            
            # INTERNATIONALE BREAKING NEWS
            international_news = await self.rss_parser.get_latest_news(
                sources=["reuters", "bbc", "dw"],
                categories=["breaking", "world", "business", "top"],
                max_items=30
            )
            print(f"   🌍 {len(international_news)} internationale Breaking News geladen")
            
            # TOP TECH NEWS
            tech_news = await self.rss_parser.get_latest_news(
                sources=["techcrunch", "theverge", "arstechnica", "heise"],
                categories=["latest", "tech", "ai", "startups", "news"],
                max_items=20
            )
            print(f"   💻 {len(tech_news)} Tech News geladen")
            
            # BITCOIN NEWS
            bitcoin_news = await self.rss_parser.get_latest_news(
                sources=["cointelegraph", "coindesk"],
                categories=["bitcoin", "latest", "markets"],
                max_items=15
            )
            print(f"   ₿ {len(bitcoin_news)} Bitcoin News geladen")
            
            # Alle News kombinieren
            all_news = local_news + international_news + tech_news + bitcoin_news
            print(f"   📡 {len(all_news)} News TOTAL von erweiterten Quellen geladen")
            
        except Exception as e:
            print(f"   ❌ RSS Fehler: {e}")
            all_news = []
        
        # Konvertiere RSSNewsItem zu dict für Kompatibilität
        news_dicts = []
        for news_item in all_news:
            news_dicts.append({
                'title': news_item.title,
                'description': news_item.summary,
                'link': news_item.link,
                'published': news_item.published,
                'source': news_item.source,
                'category': news_item.category,
                'priority': news_item.priority,
                'tags': news_item.tags
            })
        
        # Nur neue, noch nicht verwendete News
        fresh_news = self.news_dedup.filter_new_news(news_dicts)
        print(f"   🔄 {len(fresh_news)} neue News nach Deduplication")
        
        # Intelligente News-Priorisierung für Morgen-Show
        prioritized_news = self.prioritize_morning_news_enhanced(fresh_news)
        
        # Top 6-8 priorisierte News für bessere Auswahl
        selected_news = prioritized_news[:8] if len(prioritized_news) >= 8 else prioritized_news
        
        # Wetter mit korrekter Methode
        try:
            weather_data = await self.weather_service.get_current_weather("zurich")
            if weather_data:
                weather_info = {
                    'temperature': weather_data.temperature,
                    'description': self.weather_service.get_weather_description(weather_data.weather_code),
                    'humidity': weather_data.humidity,
                    'wind_speed': weather_data.wind_speed
                }
            else:
                weather_info = {'temperature': 'N/A', 'description': 'Nicht verfügbar'}
        except Exception as e:
            print(f"   ❌ Wetter Fehler: {e}")
            weather_info = {'temperature': 'N/A', 'description': 'Nicht verfügbar'}
        
        # Bitcoin
        try:
            bitcoin_data = await self.crypto_service.get_bitcoin_price()
            if bitcoin_data:
                bitcoin_info = {
                    'price': bitcoin_data.price_usd,
                    'change_24h': bitcoin_data.change_24h,
                    'price_chf': bitcoin_data.price_chf
                }
            else:
                bitcoin_info = {'price': 'N/A', 'change_24h': 'N/A'}
        except Exception as e:
            print(f"   ❌ Bitcoin Fehler: {e}")
            bitcoin_info = {'price': 'N/A', 'change_24h': 'N/A'}
        
        print(f"   ✅ {len(selected_news)} priorisierte News ausgewählt")
        print(f"   🌤️ Wetter: {weather_info.get('temperature', 'N/A')}°C")
        print(f"   ₿ Bitcoin: ${bitcoin_info.get('price', 'N/A')}")
        
        return {
            'news': selected_news,
            'weather': weather_info,
            'bitcoin': bitcoin_info
        }
    
    def prioritize_morning_news_enhanced(self, news_list):
        """Erweiterte News-Priorisierung mit internationalen Breaking News und Tech-News"""
        
        print("🌅 ERWEITERTE NEWS-PRIORISIERUNG FÜR MORGEN-SHOW")
        print("-" * 40)
        
        from datetime import datetime, timedelta
        import pytz
        
        # Schweizer Zeitzone
        swiss_tz = pytz.timezone('Europe/Zurich')
        now = datetime.now(swiss_tz)
        
        # Erweiterte Kategorisierung
        night_breaking = []      # Sehr neue News (letzte 6 Stunden)
        international_breaking = []  # Internationale Breaking News
        tech_highlights = []     # Top Tech News
        bitcoin_updates = []     # Bitcoin News
        zurich_local = []       # Zürich/lokale News
        recent_national = []    # Nationale News
        other_news = []         # Andere News
        
        for news in news_list:
            try:
                # Parse Publish-Datum
                pub_date = None
                hours_ago = 999  # Fallback
                
                if news.get('published'):
                    # Verschiedene Datumsformate versuchen
                    for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S']:
                        try:
                            if '+' in str(news['published']) or 'GMT' in str(news['published']):
                                pub_date = datetime.strptime(str(news['published']), '%a, %d %b %Y %H:%M:%S %z')
                            else:
                                pub_date = datetime.strptime(str(news['published']), fmt)
                                pub_date = swiss_tz.localize(pub_date)
                            break
                        except:
                            continue
                    
                    if pub_date:
                        hours_ago = (now - pub_date).total_seconds() / 3600
                
                # Analysiere News-Eigenschaften
                title_lower = news['title'].lower()
                source = news.get('source', '').lower()
                category = news.get('category', '').lower()
                priority = news.get('priority', 5)
                tags = news.get('tags', [])
                
                # KATEGORISIERUNG NACH INHALT UND AKTUALITÄT
                
                # 1. NACHT-BREAKING NEWS (letzte 6 Stunden, hohe Priorität)
                if hours_ago <= 6 and priority >= 7:
                    night_breaking.append((news, hours_ago, priority))
                    print(f"   🚨 NACHT-BREAKING ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                
                # 2. INTERNATIONALE BREAKING NEWS
                elif source in ['reuters', 'bbc', 'dw'] and hours_ago <= 12:
                    international_breaking.append((news, hours_ago, priority))
                    print(f"   🌍 INTERNATIONAL ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                
                # 3. TOP TECH NEWS
                elif (source in ['techcrunch', 'theverge', 'arstechnica', 'heise'] or 
                      category == 'technologie' or 
                      any(tag in ['tech', 'ai', 'startup'] for tag in tags)) and hours_ago <= 24:
                    tech_highlights.append((news, hours_ago, priority))
                    print(f"   💻 TECH ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                
                # 4. BITCOIN NEWS
                elif (source in ['cointelegraph', 'coindesk'] or 
                      category == 'bitcoin' or 
                      'bitcoin' in title_lower or 
                      any(tag in ['bitcoin', 'btc'] for tag in tags)) and hours_ago <= 24:
                    bitcoin_updates.append((news, hours_ago, priority))
                    print(f"   ₿ BITCOIN ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                
                # 5. ZÜRICH/LOKALE NEWS
                elif ('zürich' in title_lower or 'zurich' in title_lower or 
                      'zürcher' in title_lower or source in ['zueritoday', 'telezueri'] or
                      category in ['zurich', 'lokale_news_schweiz']) and hours_ago <= 48:
                    zurich_local.append((news, hours_ago, priority))
                    print(f"   🏙️ ZÜRICH-LOKAL ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                
                # 6. NATIONALE SCHWEIZER NEWS
                elif source in ['20min', 'nzz', 'srf', 'tagesanzeiger'] and hours_ago <= 24:
                    recent_national.append((news, hours_ago, priority))
                    print(f"   🇨🇭 NATIONAL ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                
                # 7. ANDERE NEWS
                else:
                    other_news.append((news, hours_ago, priority))
                    print(f"   📰 ANDERE ({hours_ago:.1f}h, P{priority}): {news['title'][:50]}...")
                    
            except Exception as e:
                print(f"   ❌ Fehler bei News-Analyse: {e}")
                other_news.append((news, 999, 1))
        
        # Sortiere jede Kategorie nach Priorität und Aktualität
        def sort_key(item):
            news, hours, priority = item
            return (-priority, hours)  # Hohe Priorität zuerst, dann neueste
        
        night_breaking.sort(key=sort_key)
        international_breaking.sort(key=sort_key)
        tech_highlights.sort(key=sort_key)
        bitcoin_updates.sort(key=sort_key)
        zurich_local.sort(key=sort_key)
        recent_national.sort(key=sort_key)
        other_news.sort(key=sort_key)
        
        # INTELLIGENTE MISCHUNG FÜR MORGEN-SHOW
        prioritized = []
        
        # 1. Top Nacht-Breaking News (max 2)
        for news, hours, priority in night_breaking[:2]:
            prioritized.append(news)
        
        # 2. Top internationale Breaking News (max 1)
        for news, hours, priority in international_breaking[:1]:
            prioritized.append(news)
        
        # 3. Top Tech News (max 1)
        for news, hours, priority in tech_highlights[:1]:
            prioritized.append(news)
        
        # 4. Bitcoin Update (max 1)
        for news, hours, priority in bitcoin_updates[:1]:
            prioritized.append(news)
        
        # 5. Zürich/lokale News (max 2)
        for news, hours, priority in zurich_local[:2]:
            prioritized.append(news)
        
        # 6. Nationale News auffüllen
        for news, hours, priority in recent_national:
            if len(prioritized) >= 10:
                break
            prioritized.append(news)
        
        # 7. Falls noch Platz: andere News
        for news, hours, priority in other_news:
            if len(prioritized) >= 12:
                break
            prioritized.append(news)
        
        print(f"   📊 KATEGORIEN: {len(night_breaking)} Nacht-Breaking, {len(international_breaking)} International, {len(tech_highlights)} Tech, {len(bitcoin_updates)} Bitcoin, {len(zurich_local)} Zürich-Lokal, {len(recent_national)} National")
        print(f"   ✅ {len(prioritized)} News priorisiert für erweiterte Morgen-Show")
        
        return prioritized
    
    def create_morning_script(self, content):
        """Erstellt Morgen-spezifisches Script"""
        
        print("✍️ ERSTELLE MORGEN-SCRIPT")
        print("-" * 40)
        
        # Wähle Broadcast-Struktur
        structure_key, selected_structure = self.select_broadcast_structure()
        
        # Lade letztes Script als Referenz
        last_script_data = self.load_last_script()
        
        # News für Prompt formatieren mit Priorisierung
        news_text = ""
        night_breaking_count = 0
        zurich_local_count = 0
        
        for i, news in enumerate(content['news'], 1):
            # Analysiere News-Typ für bessere Anweisungen
            title_lower = news['title'].lower()
            source = news.get('source', '').lower()
            
            news_type = "📰 STANDARD"
            if ('zürich' in title_lower or 'zurich' in title_lower or 
                source == 'zueritoday'):
                news_type = "🏙️ ZÜRICH-LOKAL"
                zurich_local_count += 1
            elif i <= 2:  # Erste 2 News sind meist die neuesten
                news_type = "🚨 AKTUELL"
                night_breaking_count += 1
            
            news_text += f"{i}. {news_type}: {news['title']}\n"
            if news.get('description'):
                news_text += f"   {news['description'][:200]}...\n"
        
        # Morgen-Show spezifische Anweisungen
        morning_context = f"""
MORGEN-SHOW KONTEXT (7:00 Uhr):
- {night_breaking_count} aktuelle/Nacht-News für "Was ist über Nacht passiert?"
- {zurich_local_count} Zürich-lokale News (meist vom Vortag)
- Perfekt für Morgen-Recap und lokale Verbindung
- Hörer wollen wissen: Was ist neu? Was betrifft Zürich?
"""
        
        weather_info = f"Temperatur: {content['weather'].get('temperature', 'N/A')}°C, {content['weather'].get('description', 'N/A')}"
        bitcoin_info = f"Bitcoin: ${content['bitcoin'].get('price', 'N/A')} ({content['bitcoin'].get('change_24h', 'N/A')}%)"
        
        # Struktur-spezifische Anweisungen
        structure_instructions = "\n".join([f"   {step}" for step in selected_structure['structure']])
        
        # Referenz-Script für Variation
        reference_section = ""
        if last_script_data:
            reference_section = f"""
LETZTES SCRIPT ALS REFERENZ (NICHT KOPIEREN!):
{'-' * 50}
Letzte Struktur: {last_script_data['structure']}

{last_script_data['script'][:800]}...
{'-' * 50}

WICHTIG: Das obige Script ist NUR als Referenz gedacht!
- Erstelle eine GRUNDLEGEND ANDERE Show
- Verwende ANDERE Gesprächsverläufe und Übergänge
- NEUE Formulierungen und Ansätze
- Vermeide ähnliche Phrasen oder Strukturen
- Sei kreativ und variiere den Stil komplett!
"""
        else:
            reference_section = "\nKEIN VORHERIGES SCRIPT VORHANDEN - Erstelle eine frische Show!\n"
        
        gpt_prompt = f"""Du bist ein professioneller Radio-Script-Writer für RadioX Zürich.

SPRECHER-CHARAKTERE:
- MARCEL: Haupt-Moderator, warm, energisch, Zürcher, führt durch die Sendung
- JARVIS: AI-Co-Host, entspannt-cool, tech-fokussiert, ergänzt Marcel

DIALOG-REGELN FÜR NATÜRLICHEN FLOW:
1. MARCEL spricht NICHT bei jedem Beitrag Jarvis direkt an
2. Natürliche Gesprächsübergänge ohne ständige Namensnennung
3. Jarvis meldet sich selbstständig zu Wort (besonders bei Tech/Bitcoin)
4. Organische Unterhaltung wie echte Radio-Partner
5. Marcel moderiert, Jarvis ergänzt und kommentiert
6. BITCOIN-ONLY: Niemals andere Kryptowährungen erwähnen!

TEMPO & INHALT-FOKUS:
- SCHNELL ZUM PUNKT: Keine langen Einleitungen oder Smalltalk
- INHALT ÜBER HYPE: Sachliche Information statt übertriebene Begeisterung
- BITCOIN SACHLICH: Nicht "in den Himmel loben" - einfach Fakten und Preis
- KOMPAKT: Jeder Sprecher max. 2-3 Sätze pro Beitrag
- DIREKT: Sofort zu den wichtigen Informationen

BITCOIN-BEHANDLUNG:
- Sachlich und faktisch: "Bitcoin steht bei X Dollar"
- NICHT: "Bitcoin explodiert!", "Wahnsinn!", "Unglaublich!"
- Kurz und knapp: Preis, Trend, fertig
- Keine übertriebenen Emotionen oder Hype-Sprache

GEWÄHLTE STRUKTUR: "{selected_structure['name']}"
BESCHREIBUNG: {selected_structure['description']}

STRUKTUR-VORGABE:
{structure_instructions}
{reference_section}
{morning_context}

ANTI-HALLUZINATIONS-REGELN:
- Verwende NUR die bereitgestellten echten News-Titel und Beschreibungen
- Erfinde KEINE zusätzlichen Details oder Fakten
- Bleibe bei den gegebenen Wetter- und Bitcoin-Daten
- KEINE erfundenen Zahlen, Namen oder Ereignisse
- Nur authentische, bereitgestellte Informationen verwenden

WICHTIG: 
- BEIDE SPRECHER VERWENDEN NUR HOCHDEUTSCH!
- MARCEL spricht "Jarvis" auf ENGLISCH aus (phonetisch: "Dscharvis")
- MORGEN-STIMMUNG: Energisch, motivierend, frischer Start in den Tag
- FOLGE EXAKT der gewählten Struktur für Abwechslung!
- BITCOIN-ONLY: Spreche NIEMALS über andere Kryptowährungen! Nur Bitcoin!
- Verwende NIEMALS Begriffe wie "Krypto", "Kryptowährungen", "Altcoins"
- Sage immer nur "Bitcoin" - nie "Krypto-Markt" sondern "Bitcoin-Markt"
- TEMPO: Schnell, kompakt, auf den Punkt!

CONTENT (NUR DIESE ECHTEN DATEN VERWENDEN):
{news_text}

WETTER: {weather_info}
BITCOIN: {bitcoin_info}

AUFGABE: Erstelle ein energisches Morgen-Radio-Script (7:00 Uhr) das EXAKT der gewählten Struktur "{selected_structure['name']}" folgt:

DIALOG-STIL:
- KOMPAKT: Kurze, prägnante Aussagen
- SACHLICH: Besonders bei Bitcoin - Fakten statt Hype
- SCHNELL: Direkt zu den wichtigen Infos
- Natürliche Gesprächsübergänge ohne ständige Ansprache
- Marcel führt, Jarvis ergänzt organisch
- Authentische Radio-Partner-Dynamik
- Weniger "Jarvis, was denkst du..." - mehr natürlicher Flow
- Jarvis meldet sich selbst zu relevanten Themen
- STRUKTUR-VARIATION: Jede Sendung soll anders aufgebaut sein!
- BITCOIN-FOKUS: Nur Bitcoin erwähnen, niemals andere Kryptowährungen erwähnen!
- KEINE HALLUZINATIONEN: Nur echte, bereitgestellte Daten verwenden!
- INHALT-FOKUS: Weniger Gerede, mehr Information!

BEISPIEL KOMPAKTER STIL:
MARCEL: Guten Morgen Zürich! 7 Uhr, hier die News.
JARVIS: Bitcoin bei 43.000 Dollar, leicht im Plus.
MARCEL: Wetter heute 15 Grad, sonnig. Zur ersten News...

FORMAT: Nur Sprecher-Namen und Text, keine Regieanweisungen.

Erstelle das komplette Script mit der Struktur "{selected_structure['name']}" - KOMPAKT, SACHLICH, SCHNELL ZUM PUNKT:"""

        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {'role': 'user', 'content': gpt_prompt}
                ],
                'max_tokens': 1500,
                'temperature': 0.7
            }
            
            print("🤖 Sende Request an GPT-4...")
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content']
                print("   ✅ Script erfolgreich generiert")
                print(f"   📝 Script-Länge: {len(script)} Zeichen")
                
                # Speichere gewählte Struktur für nächste Auswahl
                self.current_structure = selected_structure
                
                return script
            else:
                print(f"   ❌ GPT-4 Fehler: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Script-Generierung Fehler: {str(e)}")
            return None
    
    def parse_script_to_segments(self, script):
        """Parst Script in Sprecher-Segmente"""
        
        print("📝 PARSE SCRIPT IN SEGMENTE")
        print("-" * 40)
        
        segments = []
        lines = script.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Entferne Markdown-Formatierung (**TEXT:**) und normale Formatierung (TEXT:)
            if line.startswith('**JARVIS:**') or line.startswith('JARVIS:'):
                text = line.replace('**JARVIS:**', '').replace('JARVIS:', '').strip()
                if text:
                    segments.append({
                        'speaker': 'JARVIS',
                        'voice_id': self.jarvis_voice_id,
                        'text': text
                    })
                    print(f"   🤖 JARVIS: {text[:50]}...")
                    
            elif line.startswith('**MARCEL:**') or line.startswith('MARCEL:'):
                text = line.replace('**MARCEL:**', '').replace('MARCEL:', '').strip()
                if text:
                    segments.append({
                        'speaker': 'MARCEL',
                        'voice_id': self.marcel_voice_id,
                        'text': text
                    })
                    print(f"   🎙️ MARCEL: {text[:50]}...")
        
        print(f"   ✅ {len(segments)} Segmente erstellt")
        return segments
    
    def generate_audio_segment(self, segment):
        """Generiert Audio für ein Segment"""
        
        try:
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.elevenlabs_api_key
            }
            
            data = {
                'text': segment['text'],
                'model_id': 'eleven_multilingual_v2',
                'voice_settings': {
                    'stability': 0.85,
                    'similarity_boost': 0.95,
                    'style': 0.1,
                    'use_speaker_boost': True
                }
            }
            
            response = requests.post(
                f'https://api.elevenlabs.io/v1/text-to-speech/{segment["voice_id"]}',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # Temporäre Datei erstellen
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(response.content)
                temp_file.close()
                
                print(f"   ✅ {segment['speaker']}: Audio generiert ({len(response.content)} bytes)")
                return temp_file.name
            else:
                print(f"   ❌ {segment['speaker']}: ElevenLabs Fehler {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ {segment['speaker']}: Audio-Generierung Fehler: {str(e)}")
            return None
    
    def create_concatenated_audio(self, audio_segments):
        """Fügt Audio-Segmente zusammen"""
        
        print("🎵 FÜGE AUDIO-SEGMENTE ZUSAMMEN")
        print("-" * 40)
        
        # Timestamp für Dateiname
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        final_file = self.output_dir / f"RadioX_Final_{timestamp}.mp3"
        
        try:
            # Einfache binäre Concatenation für MP3
            with open(final_file, 'wb') as outfile:
                total_size = 0
                segments_added = 0
                
                for i, audio_file in enumerate(audio_segments):
                    if audio_file and os.path.exists(audio_file):
                        print(f"   📎 Füge Segment {i+1} hinzu...")
                        with open(audio_file, 'rb') as infile:
                            data = infile.read()
                            outfile.write(data)
                            total_size += len(data)
                            segments_added += 1
            
            # Cleanup temporäre Dateien
            for audio_file in audio_segments:
                if audio_file and os.path.exists(audio_file):
                    os.unlink(audio_file)
            
            print(f"   ✅ Finale MP3 erstellt: {final_file}")
            print(f"   📊 Dateigröße: {total_size / 1024 / 1024:.1f} MB")
            print(f"   🎵 {segments_added} Segmente zusammengefügt")
            
            return str(final_file)
            
        except Exception as e:
            print(f"   ❌ Audio-Concatenation Fehler: {str(e)}")
            return None
    
    def generate_morning_cover(self, timestamp):
        """Generiert Morgen-spezifisches Cover mit DALL-E 3"""
        
        print("🎨 GENERIERE MORGEN-COVER")
        print("-" * 40)
        
        image_prompt = f"""Create a professional podcast cover art for "RadioX 7:00 Morning Edition":

DESIGN ELEMENTS:
- Fresh morning theme with bright, energizing colors (sunrise orange, sky blue)
- Swiss design principles: clean, minimal, functional
- Professional broadcasting aesthetic with modern elements
- 1024x1024 pixel format

TEXT ELEMENTS:
- "RADIOX" as main title (bold, modern font)
- "7:00 MORGEN-EDITION" as subtitle
- "Marcel & Jarvis" as hosts

STYLE:
- Modern, energetic morning radio aesthetic
- Sunrise/dawn atmosphere with fresh, bright colors
- Swiss broadcasting quality
- Motivating and positive energy
- Professional podcast/radio design

MOOD: Fresh start, energy, motivation, Swiss morning radio"""

        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'dall-e-3',
                'prompt': image_prompt,
                'n': 1,
                'size': '1024x1024',
                'quality': 'standard',
                'response_format': 'b64_json'
            }
            
            print("🎨 Sende Request an DALL-E 3...")
            response = requests.post(
                'https://api.openai.com/v1/images/generations',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result['data'][0]['b64_json'])
                
                # Cover-Datei speichern
                cover_file = self.output_dir / f"RadioX_Cover_{timestamp}.png"
                with open(cover_file, 'wb') as f:
                    f.write(image_data)
                
                print(f"   ✅ Cover erstellt: {cover_file}")
                print(f"   📊 Dateigröße: {len(image_data) / 1024 / 1024:.1f} MB")
                
                return str(cover_file)
            else:
                print(f"   ❌ DALL-E 3 Fehler: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Cover-Generierung Fehler: {str(e)}")
            return None
    
    def add_cover_to_mp3(self, mp3_file, cover_file):
        """Fügt Cover zu MP3 hinzu"""
        
        try:
            print("🎵 Füge Cover zu MP3 hinzu...")
            
            # Prüfe ob Cover-Datei existiert
            if not cover_file or not os.path.exists(cover_file):
                print(f"   ❌ Cover-Datei nicht gefunden: {cover_file}")
                return
            
            # Prüfe ob MP3-Datei existiert
            if not os.path.exists(mp3_file):
                print(f"   ❌ MP3-Datei nicht gefunden: {mp3_file}")
                return
            
            # Lade MP3 mit mutagen
            try:
                audio = MP3(mp3_file, ID3=ID3)
            except Exception as e:
                print(f"   ❌ Fehler beim Laden der MP3: {e}")
                return
            
            # Entferne alle existierenden Tags
            try:
                if audio.tags is not None:
                    audio.delete()
                audio.save()
                print("   🗑️ Alte Tags entfernt")
            except Exception as e:
                print(f"   ⚠️ Warnung beim Entfernen alter Tags: {e}")
            
            # Lade MP3 neu und füge neue Tags hinzu
            try:
                audio = MP3(mp3_file, ID3=ID3)
                
                # Stelle sicher, dass Tags existieren
                if audio.tags is None:
                    audio.add_tags()
                    print("   ➕ Neue ID3-Tags hinzugefügt")
                
                # Basis-Tags setzen
                audio.tags.add(TIT2(encoding=3, text="RadioX 7:00 Morgen-Edition"))
                audio.tags.add(TPE1(encoding=3, text="Marcel & Jarvis"))
                audio.tags.add(TALB(encoding=3, text="RadioX AI Broadcasts"))
                
                # Timestamp als Kommentar
                timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
                audio.tags.add(COMM(encoding=3, lang='deu', desc='Broadcast Info', 
                                  text=f'RadioX 7:00 Morgen-Edition vom {timestamp}'))
                
                print("   📝 Basis-Tags gesetzt")
                
                # Cover-Bild hinzufügen
                with open(cover_file, 'rb') as img_file:
                    img_data = img_file.read()
                
                # Bestimme MIME-Type basierend auf Dateiendung
                mime_type = 'image/png' if cover_file.lower().endswith('.png') else 'image/jpeg'
                
                # APIC (Attached Picture) Tag hinzufügen
                audio.tags.add(APIC(
                    encoding=3,          # UTF-8
                    mime=mime_type,      # MIME type
                    type=3,              # Cover (front)
                    desc='Cover Art',    # Beschreibung
                    data=img_data        # Bilddaten
                ))
                
                print(f"   🖼️ Cover hinzugefügt ({len(img_data)} bytes, {mime_type})")
                
                # Tags speichern
                audio.save()
                print("   ✅ Cover erfolgreich zu MP3 hinzugefügt")
                
                # Verifikation
                verification = MP3(mp3_file, ID3=ID3)
                if verification.tags and verification.tags.getall('APIC'):
                    print("   ✅ Cover-Integration verifiziert")
                else:
                    print("   ⚠️ Cover-Verifikation fehlgeschlagen")
                
            except Exception as e:
                print(f"   ❌ Fehler beim Hinzufügen der Tags: {e}")
                
        except Exception as e:
            print(f"   ❌ Cover-Integration Fehler: {str(e)}")
            import traceback
            print(f"   🔍 Traceback: {traceback.format_exc()}")
    
    def verify_mp3_cover(self, mp3_file):
        """Verifiziert ob das Cover korrekt in der MP3 eingebettet ist"""
        
        try:
            print("🔍 VERIFIZIERE MP3-COVER")
            print("-" * 40)
            
            audio = MP3(mp3_file, ID3=ID3)
            
            if not audio.tags:
                print("   ❌ Keine ID3-Tags gefunden")
                return False
            
            # Prüfe alle Tags
            print("   📋 Gefundene Tags:")
            for tag_name in audio.tags.keys():
                tag_value = audio.tags[tag_name]
                if tag_name == 'APIC:Cover Art':
                    print(f"   🖼️ {tag_name}: {len(tag_value.data)} bytes Cover-Daten")
                else:
                    print(f"   📝 {tag_name}: {str(tag_value)[:50]}...")
            
            # Prüfe speziell nach Cover
            covers = audio.tags.getall('APIC')
            if covers:
                cover = covers[0]
                print(f"   ✅ Cover gefunden: {cover.mime}, {len(cover.data)} bytes")
                return True
            else:
                print("   ❌ Kein Cover gefunden")
                return False
                
        except Exception as e:
            print(f"   ❌ Verifikation fehlgeschlagen: {e}")
            return False
    
    def add_cover_alternative(self, mp3_file, cover_file):
        """Alternative Cover-Integration-Methode"""
        
        try:
            print("🔄 ALTERNATIVE COVER-INTEGRATION")
            print("-" * 40)
            
            # Verwende eyed3 als Alternative falls verfügbar
            try:
                import eyed3
                
                audiofile = eyed3.load(mp3_file)
                if audiofile.tag is None:
                    audiofile.initTag()
                
                # Cover hinzufügen
                with open(cover_file, 'rb') as img_file:
                    img_data = img_file.read()
                
                audiofile.tag.images.set(3, img_data, 'image/png')  # Type 3 = Front Cover
                audiofile.tag.save()
                
                print("   ✅ Alternative Cover-Integration mit eyed3 erfolgreich")
                return True
                
            except ImportError:
                print("   ℹ️ eyed3 nicht verfügbar")
            
            # Fallback: Manuelle ID3v2.3 Cover-Integration
            print("   🔧 Versuche manuelle ID3v2.3 Integration...")
            
            audio = MP3(mp3_file)
            
            # Forciere ID3v2.3 Format
            if audio.tags is None:
                audio.add_tags(ID3=ID3)
            
            # Entferne alle APIC Tags
            audio.tags.delall('APIC')
            
            # Cover mit spezifischen Parametern hinzufügen
            with open(cover_file, 'rb') as img_file:
                img_data = img_file.read()
            
            # ID3v2.3 kompatibles APIC
            audio.tags.add(APIC(
                encoding=0,              # ISO-8859-1 für bessere Kompatibilität
                mime='image/png',
                type=3,                  # Front cover
                desc='',                 # Leere Beschreibung für Kompatibilität
                data=img_data
            ))
            
            # Forciere ID3v2.3 beim Speichern
            audio.save(v2_version=3)
            
            print("   ✅ Manuelle ID3v2.3 Cover-Integration abgeschlossen")
            
            # Finale Verifikation
            return self.verify_mp3_cover(mp3_file)
            
        except Exception as e:
            print(f"   ❌ Alternative Cover-Integration fehlgeschlagen: {e}")
            return False
    
    def save_broadcast_info(self, timestamp, segments, content, script):
        """Speichert Broadcast-Informationen"""
        
        info_file = self.output_dir / f"RadioX_Final_Info_{timestamp}.txt"
        
        info_content = f"""RadioX 7:00 Morgen-Edition - Broadcast Info
==================================================

Timestamp: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Duration: {len(segments) * 10} Sekunden (geschätzt)
Segments: {len(segments)}
Audio Files: {len(segments)}

STRUKTUR: {getattr(self, 'current_structure', {}).get('name', 'Standard')}
BESCHREIBUNG: {getattr(self, 'current_structure', {}).get('description', 'Standard-Struktur')}

SPRECHER:
- MARCEL: {self.marcel_voice_id} (Deine deutsche Stimme)
- JARVIS: {self.jarvis_voice_id} (AI-Style deutsch)

CONTENT:
- News Items: {len(content['news'])}
- Weather: ✅
- Bitcoin: ✅

NEWS TOPICS:
"""
        
        # News Topics hinzufügen
        for news in content['news']:
            info_content += f"- {news['title']}\n"
        
        info_content += f"\nSCRIPT:\n{'=' * 30}\n{script}\n\n"
        info_content += f"SEGMENTE:\n{'=' * 30}\n"
        
        for i, segment in enumerate(segments, 1):
            text_preview = segment['text'][:80] + "..." if len(segment['text']) > 80 else segment['text']
            info_content += f"{i:2d}. {segment['speaker']}: {text_preview}\n"
        
        # Struktur-Details hinzufügen
        if hasattr(self, 'current_structure'):
            info_content += f"\nSTRUKTUR-DETAILS:\n{'=' * 30}\n"
            for i, step in enumerate(self.current_structure['structure'], 1):
                info_content += f"{i:2d}. {step}\n"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_content)
        
        print(f"📄 Broadcast-Info gespeichert: {info_file}")
        print(f"🎭 Verwendete Struktur: {getattr(self, 'current_structure', {}).get('name', 'Standard')}")
    
    async def create_morning_broadcast(self):
        """Erstellt kompletten 7:00 Morgen-Broadcast"""
        
        print("🌅 STARTE 7:00 MORGEN-BROADCAST GENERIERUNG")
        print("=" * 50)
        
        # 1. Sammle frische Inhalte
        content = await self.collect_fresh_content()
        
        if not content['news']:
            print("❌ Keine neuen News gefunden! Broadcast abgebrochen.")
            return None
        
        # 2. Erstelle Script
        script = self.create_morning_script(content)
        if not script:
            print("❌ Script-Generierung fehlgeschlagen!")
            return None
        
        # 3. Parse Script in Segmente
        segments = self.parse_script_to_segments(script)
        if not segments:
            print("❌ Keine Segmente erstellt!")
            return None
        
        # 4. Generiere Audio für alle Segmente
        print("🎙️ GENERIERE AUDIO-SEGMENTE")
        print("-" * 40)
        
        audio_files = []
        for i, segment in enumerate(segments, 1):
            print(f"   🎵 Segment {i}/{len(segments)}: {segment['speaker']}")
            audio_file = self.generate_audio_segment(segment)
            audio_files.append(audio_file)
        
        # 5. Füge Audio zusammen
        final_mp3 = self.create_concatenated_audio(audio_files)
        if not final_mp3:
            print("❌ Audio-Concatenation fehlgeschlagen!")
            return None
        
        # 6. Generiere Cover
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        cover_file = self.generate_morning_cover(timestamp)
        
        # 7. Füge Cover zu MP3 hinzu
        if cover_file:
            self.add_cover_to_mp3(final_mp3, cover_file)
            
            # Verifiziere Cover-Integration
            cover_success = self.verify_mp3_cover(final_mp3)
            if not cover_success:
                print("⚠️ Cover-Integration fehlgeschlagen - versuche alternative Methode...")
                # Alternative Cover-Integration versuchen
                self.add_cover_alternative(final_mp3, cover_file)
        
        # 8. Speichere Broadcast-Info
        self.save_broadcast_info(timestamp, segments, content, script)
        
        print("🎉 7:00 MORGEN-BROADCAST ERFOLGREICH ERSTELLT!")
        print("=" * 50)
        print(f"📁 MP3: {final_mp3}")
        print(f"🎨 Cover: {cover_file}")
        print(f"📄 Info: RadioX_Final_Info_{timestamp}.txt")
        
        return {
            'mp3_file': final_mp3,
            'cover_file': cover_file,
            'timestamp': timestamp,
            'segments': len(segments)
        }


async def main():
    """Hauptfunktion"""
    try:
        broadcast = RadioX7UhrMorgenBroadcast()
        result = await broadcast.create_morning_broadcast()
        
        if result:
            print(f"\n✅ 7:00 Morgen-Broadcast erfolgreich erstellt!")
            print(f"🎵 {result['segments']} Segmente generiert")
            print(f"📁 Dateien im output/ Ordner verfügbar")
        else:
            print("\n❌ Broadcast-Generierung fehlgeschlagen!")
            
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 