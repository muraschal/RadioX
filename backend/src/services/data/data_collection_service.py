#!/usr/bin/env python3

"""
Data Collection Service - DUMM UND EINFACH
==========================================

Sammelt wertefrei ALLE verfügbaren Daten:
- RSS: ALLE aktiven Feeds
- Weather: Standard Location
- Bitcoin: Aktueller Preis

Keine Intelligenz, keine Presets, keine Filterung!
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
import os

from .rss_service import RSSService
from .weather_service import WeatherService
from .bitcoin_service import BitcoinService


class DataCollectionService:
    """
    DUMMER Data Collection Service
    
    Sammelt einfach ALLE verfügbaren Daten ohne Bewertung:
    - RSS: get_all_recent_news()
    - Weather: get_current_weather()
    - Bitcoin: get_bitcoin_price()
    """
    
    def __init__(self):
        self.rss_service = RSSService()
        self.weather_service = WeatherService()
        self.crypto_service = BitcoinService()
    
    async def collect_all_data(self, max_age_hours: int = 12) -> Dict[str, Any]:
        """
        Sammelt ALLE verfügbaren Daten von allen Services
        Generiert automatisch HTML-Dashboards
        """
        
        logger.info("🚀 Starte vollständige Datensammlung...")
        
        # SEQUENZIELLE Sammlung um Race Conditions zu vermeiden
        logger.info("📰 Sammle News...")
        news = await self._collect_all_news_safe(max_age_hours)
        
        # Parallele Sammlung für Weather + Crypto (diese haben keine Konflikte)
        logger.info("🌍 Sammle Kontext-Daten parallel...")
        weather_task = self._collect_weather_safe()
        crypto_task = self._collect_crypto_safe()
        
        weather, crypto = await asyncio.gather(
            weather_task, crypto_task,
            return_exceptions=True
        )
        
        # Ergebnisse zusammenfassen
        result = {
            "collection_timestamp": datetime.now().isoformat(),
            "max_age_hours": max_age_hours,
            "news": news if not isinstance(news, Exception) else [],
            "weather": weather if not isinstance(weather, Exception) else None,
            "crypto": crypto if not isinstance(crypto, Exception) else None,
            "success": True,
            "errors": []
        }
        
        # Fehler sammeln
        if isinstance(news, Exception):
            result["errors"].append(f"News: {str(news)}")
        if isinstance(weather, Exception):
            result["errors"].append(f"Weather: {str(weather)}")
        if isinstance(crypto, Exception):
            result["errors"].append(f"Crypto: {str(crypto)}")
        
        # Statistiken
        news_count = len(result["news"]) if result["news"] else 0
        logger.info(f"✅ Datensammlung abgeschlossen: {news_count} News, Wetter: {'✓' if result['weather'] else '✗'}, Bitcoin: {'✓' if result['crypto'] else '✗'}")
        
        # 🎨 HTML-Dashboards automatisch generieren
        try:
            await self.generate_html_dashboards(result)
            logger.info("🎨 HTML-Dashboards automatisch generiert!")
        except Exception as e:
            logger.error(f"⚠️ HTML-Dashboard-Generierung fehlgeschlagen: {e}")
            result["errors"].append(f"HTML-Dashboards: {str(e)}")
        
        return result
    
    async def collect_news_only(self, max_age_hours: int = 12) -> Dict[str, Any]:
        """
        Sammelt nur RSS News - ALLE verfügbaren
        """
        
        logger.info("📰 Sammle ALLE RSS News...")
        
        news = await self._collect_all_news_safe(max_age_hours)
        
        return {
            "news": news,
            "collection_timestamp": datetime.now().isoformat(),
            "max_age_hours": max_age_hours,
            "news_count": len(news) if news else 0
        }
    
    async def collect_context_data(self) -> Dict[str, Any]:
        """Sammelt nur Kontext-Daten (ALLE Weather + Crypto)"""
        
        logger.info("🌍 Sammle ALLE Kontext-Daten...")
        
        # Parallele Sammlung
        weather_task = self._collect_weather_safe()
        crypto_task = self._collect_crypto_safe()
        
        weather, crypto = await asyncio.gather(
            weather_task, crypto_task, return_exceptions=True
        )
        
        return {
            "weather": weather if not isinstance(weather, Exception) else None,
            "crypto": crypto if not isinstance(crypto, Exception) else None,
            "collection_timestamp": datetime.now().isoformat()
        }
    
    async def test_connections(self) -> Dict[str, bool]:
        """Testet alle Datenquellen-Verbindungen"""
        
        logger.info("🔧 Teste alle Datenquellen...")
        
        results = {}
        
        # Test RSS Feeds
        try:
            test_feeds = await self.rss_service.get_all_active_feeds()
            results["rss_service"] = len(test_feeds) > 0
        except Exception as e:
            logger.error(f"RSS Test Fehler: {e}")
            results["rss_service"] = False
        
        # Test Weather Service
        try:
            weather = await self.weather_service.get_current_weather("Zürich")
            results["weather_service"] = weather is not None
        except Exception as e:
            logger.error(f"Weather Test Fehler: {e}")
            results["weather_service"] = False
        
        # Test Crypto Service
        try:
            crypto = await self.crypto_service.get_bitcoin_price()
            results["crypto_service"] = crypto is not None
        except Exception as e:
            logger.error(f"Crypto Test Fehler: {e}")
            results["crypto_service"] = False
        
        logger.info(f"🔧 Verbindungstests abgeschlossen: {results}")
        return results
    
    async def generate_html_dashboards(self, data: Dict[str, Any]) -> bool:
        """
        Generiert automatisch beide HTML-Dashboards:
        1. RSS Dashboard (rss.html)
        2. Data Collection Dashboard (data_collection.html)
        """
        
        logger.info("🎨 Generiere HTML-Dashboards...")
        
        try:
            # Pfad zum outplay Ordner
            outplay_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "outplay")
            os.makedirs(outplay_dir, exist_ok=True)
            
            # 1. RSS Dashboard generieren
            await self._generate_rss_dashboard(data, outplay_dir)
            
            # 2. Data Collection Dashboard generieren  
            await self._generate_data_collection_dashboard(data, outplay_dir)
            
            # 3. JSON-Daten für JavaScript speichern
            await self._save_json_data(data, outplay_dir)
            
            logger.info("✅ HTML-Dashboards erfolgreich generiert")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler bei HTML-Dashboard-Generierung: {e}")
            return False
    
    async def _generate_rss_dashboard(self, data: Dict[str, Any], outplay_dir: str):
        """Generiert das RSS-spezifische Dashboard"""
        
        news = data.get('news', [])
        
        # RSS-spezifische Statistiken
        sources = {}
        categories = {}
        total_articles = len(news)
        
        for item in news:
            source = item.get('source', 'unknown')
            category = item.get('category', 'general')
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        # RSS HTML Template
        rss_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 RadioX RSS Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px; color: #2c3e50;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; background: rgba(255,255,255,0.95); border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center; }}
        .stat-card .icon {{ font-size: 3em; margin-bottom: 15px; }}
        .stat-card .number {{ font-size: 2.5em; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .stat-card .label {{ font-size: 1.1em; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }}
        .content {{ padding: 30px; }}
        .section {{ background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 30px; overflow: hidden; }}
        .section-header {{ background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px; font-size: 1.5em; font-weight: bold; }}
        .news-table {{ width: 100%; border-collapse: collapse; }}
        .news-table th {{ background: #34495e; color: white; padding: 15px; text-align: left; font-weight: 600; }}
        .news-table td {{ padding: 15px; border-bottom: 1px solid #ecf0f1; vertical-align: top; }}
        .news-table tr:hover {{ background: #f8f9fa; }}
        .source-badge {{ padding: 4px 12px; border-radius: 12px; font-weight: bold; text-transform: uppercase; font-size: 0.8em; color: white; }}
        .source-nzz {{ background: #e74c3c; }}
        .source-20min {{ background: #f39c12; }}
        .source-srf {{ background: #27ae60; }}
        .source-tagesanzeiger {{ background: #8e44ad; }}
        .source-cash {{ background: #2ecc71; }}
        .source-heise {{ background: #34495e; }}
        .source-cointelegraph {{ background: #f1c40f; color: black; }}
        .source-techcrunch {{ background: #1abc9c; }}
        .source-theverge {{ background: #9b59b6; }}
        .source-rt {{ background: #e67e22; }}
        .source-bbc {{ background: #c0392b; }}
        .news-link {{ color: #3498db; text-decoration: none; font-weight: bold; }}
        .news-link:hover {{ color: #2980b9; }}
        .timestamp {{ text-align: center; padding: 20px; background: #ecf0f1; color: #7f8c8d; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 RadioX RSS Dashboard</h1>
            <div style="font-size: 1.2em; opacity: 0.9;">Alle RSS-Feeds im Überblick</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📰</div>
                <div class="number">{total_articles}</div>
                <div class="label">Artikel Total</div>
            </div>
            <div class="stat-card">
                <div class="icon">📡</div>
                <div class="number">{len(sources)}</div>
                <div class="label">Aktive Quellen</div>
            </div>
            <div class="stat-card">
                <div class="icon">🏷️</div>
                <div class="number">{len(categories)}</div>
                <div class="label">Kategorien</div>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <div class="section-header">📊 Quellen-Verteilung</div>
                <div style="padding: 20px;">
                    {self._generate_source_stats_html(sources)}
                </div>
            </div>

            <div class="section">
                <div class="section-header">📰 Alle RSS-Artikel</div>
                <table class="news-table">
                    <thead>
                        <tr>
                            <th>Quelle</th>
                            <th>Kategorie</th>
                            <th>Titel</th>
                            <th>Zusammenfassung</th>
                            <th>Alter</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_news_table_html(news)}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="timestamp">
            RSS-Dashboard generiert am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
        
        # RSS HTML speichern
        rss_path = os.path.join(outplay_dir, "rss.html")
        with open(rss_path, 'w', encoding='utf-8') as f:
            f.write(rss_html)
        
        logger.info("✅ RSS Dashboard (rss.html) generiert")
    
    async def _generate_data_collection_dashboard(self, data: Dict[str, Any], outplay_dir: str):
        """Generiert das Data Collection Dashboard mit eingebetteten Daten"""
        
        import json
        
        # JSON-Daten direkt in JavaScript einbetten
        json_data = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        
        # Data Collection HTML Template mit eingebetteten Daten
        data_collection_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RadioX Data Collection Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); border-radius: 20px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); }}
        .header .subtitle {{ font-size: 1.2em; opacity: 0.9; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); text-align: center; transition: transform 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-card .icon {{ font-size: 3em; margin-bottom: 15px; }}
        .stat-card .number {{ font-size: 2.5em; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .stat-card .label {{ font-size: 1.1em; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }}
        .content-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 30px; padding: 30px; }}
        .news-section {{ background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .section-header {{ background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px; font-size: 1.5em; font-weight: bold; }}
        .news-filters {{ padding: 20px; background: #ecf0f1; border-bottom: 1px solid #bdc3c7; }}
        .filter-buttons {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .filter-btn {{ padding: 8px 16px; border: none; border-radius: 20px; background: #95a5a6; color: white; cursor: pointer; transition: all 0.3s ease; font-size: 0.9em; }}
        .filter-btn.active {{ background: #3498db; transform: scale(1.05); }}
        .filter-btn:hover {{ background: #2980b9; }}
        .news-list {{ max-height: 800px; overflow-y: auto; }}
        .news-item {{ padding: 20px; border-bottom: 1px solid #ecf0f1; transition: background-color 0.3s ease; }}
        .news-item:hover {{ background-color: #f8f9fa; }}
        .news-item:last-child {{ border-bottom: none; }}
        .news-meta {{ display: flex; align-items: center; gap: 15px; margin-bottom: 10px; font-size: 0.9em; }}
        .source-badge {{ padding: 4px 12px; border-radius: 12px; font-weight: bold; text-transform: uppercase; font-size: 0.8em; }}
        .source-nzz {{ background: #e74c3c; color: white; }}
        .source-20min {{ background: #f39c12; color: white; }}
        .source-srf {{ background: #27ae60; color: white; }}
        .source-tagesanzeiger {{ background: #8e44ad; color: white; }}
        .source-cash {{ background: #2ecc71; color: white; }}
        .source-heise {{ background: #34495e; color: white; }}
        .source-cointelegraph {{ background: #f1c40f; color: black; }}
        .source-techcrunch {{ background: #1abc9c; color: white; }}
        .source-theverge {{ background: #9b59b6; color: white; }}
        .source-rt {{ background: #e67e22; color: white; }}
        .source-bbc {{ background: #c0392b; color: white; }}
        .category-badge {{ padding: 4px 12px; border-radius: 12px; background: #ecf0f1; color: #2c3e50; font-size: 0.8em; }}
        .priority-badge {{ padding: 4px 8px; border-radius: 8px; font-weight: bold; font-size: 0.8em; }}
        .priority-10 {{ background: #e74c3c; color: white; }}
        .priority-9 {{ background: #f39c12; color: white; }}
        .priority-8 {{ background: #f1c40f; color: black; }}
        .priority-7 {{ background: #2ecc71; color: white; }}
        .priority-6 {{ background: #3498db; color: white; }}
        .priority-5 {{ background: #95a5a6; color: white; }}
        .age-badge {{ padding: 4px 8px; border-radius: 8px; background: #bdc3c7; color: #2c3e50; font-size: 0.8em; }}
        .news-title {{ font-size: 1.2em; font-weight: bold; color: #2c3e50; margin-bottom: 8px; line-height: 1.4; }}
        .news-summary {{ color: #7f8c8d; line-height: 1.5; margin-bottom: 10px; }}
        .news-link {{ display: inline-flex; align-items: center; gap: 8px; color: #3498db; text-decoration: none; font-weight: bold; transition: color 0.3s ease; }}
        .news-link:hover {{ color: #2980b9; }}
        .sidebar {{ display: flex; flex-direction: column; gap: 20px; }}
        .context-card {{ background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .weather-card .section-header {{ background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); }}
        .crypto-card .section-header {{ background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); color: #2c3e50; }}
        .card-content {{ padding: 25px; text-align: center; }}
        .weather-temp {{ font-size: 3em; font-weight: bold; color: #f39c12; margin-bottom: 10px; }}
        .weather-desc {{ font-size: 1.2em; color: #7f8c8d; margin-bottom: 15px; }}
        .weather-location {{ font-size: 1em; color: #95a5a6; }}
        .crypto-price {{ font-size: 2.5em; font-weight: bold; color: #f1c40f; margin-bottom: 10px; }}
        .crypto-change {{ font-size: 1.3em; font-weight: bold; margin-bottom: 15px; }}
        .crypto-change.positive {{ color: #27ae60; }}
        .crypto-change.negative {{ color: #e74c3c; }}
        .crypto-trend {{ font-size: 1em; color: #7f8c8d; background: #ecf0f1; padding: 10px; border-radius: 8px; }}
        .timestamp {{ text-align: center; padding: 20px; background: #ecf0f1; color: #7f8c8d; font-style: italic; }}
        @media (max-width: 768px) {{ .content-grid {{ grid-template-columns: 1fr; }} .stats-grid {{ grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }} .filter-buttons {{ justify-content: center; }} }}
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 RadioX Data Collection Dashboard</h1>
            <div class="subtitle">Alle gesammelten Daten vor GPT-Priorisierung</div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="icon">📰</div><div class="number" id="total-news">0</div><div class="label">News Artikel</div></div>
            <div class="stat-card"><div class="icon">🔗</div><div class="number" id="total-links">0</div><div class="label">Mit URLs</div></div>
            <div class="stat-card"><div class="icon">📡</div><div class="number" id="total-sources">0</div><div class="label">Quellen</div></div>
            <div class="stat-card"><div class="icon">🏷️</div><div class="number" id="total-categories">0</div><div class="label">Kategorien</div></div>
        </div>
        <div class="content-grid">
            <div class="news-section">
                <div class="section-header">📰 News Artikel (für GPT-Priorisierung)</div>
                <div class="news-filters">
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-filter="all">Alle</button>
                        <button class="filter-btn" data-filter="zurich">Zürich</button>
                        <button class="filter-btn" data-filter="news">News</button>
                        <button class="filter-btn" data-filter="wirtschaft">Wirtschaft</button>
                        <button class="filter-btn" data-filter="tech">Tech</button>
                        <button class="filter-btn" data-filter="bitcoin">Bitcoin</button>
                        <button class="filter-btn" data-filter="international">International</button>
                        <button class="filter-btn" data-filter="schweiz">Schweiz</button>
                    </div>
                </div>
                <div class="news-list" id="news-list"></div>
            </div>
            <div class="sidebar">
                <div class="context-card weather-card">
                    <div class="section-header">🌤️ Wetter Kontext</div>
                    <div class="card-content" id="weather-content"></div>
                </div>
                <div class="context-card crypto-card">
                    <div class="section-header">₿ Bitcoin Kontext</div>
                    <div class="card-content" id="crypto-content"></div>
                </div>
            </div>
        </div>
        <div class="timestamp" id="timestamp"></div>
    </div>
    <script>
        // Daten direkt eingebettet (kein fetch() nötig)
        const data = {json_data};
        
        function loadData() {{
            try {{
                displayStats(data); 
                displayNews(data.news || []); 
                displayWeather(data.weather); 
                displayCrypto(data.crypto); 
                displayTimestamp(data.collection_timestamp);
            }} catch (error) {{
                console.error('Error loading data:', error);
                document.getElementById('news-list').innerHTML = '<div style="padding: 20px; text-align: center; color: #e74c3c;">Fehler beim Laden der Daten</div>';
            }}
        }}
        
        function displayStats(data) {{
            const news = data.news || []; 
            const newsWithLinks = news.filter(item => item.has_link); 
            const sources = [...new Set(news.map(item => item.source))]; 
            const categories = [...new Set(news.map(item => item.category))];
            document.getElementById('total-news').textContent = news.length; 
            document.getElementById('total-links').textContent = newsWithLinks.length; 
            document.getElementById('total-sources').textContent = sources.length; 
            document.getElementById('total-categories').textContent = categories.length;
        }}
        
        function displayNews(news) {{
            const newsList = document.getElementById('news-list');
            if (!news || news.length === 0) {{ 
                newsList.innerHTML = '<div style="padding: 20px; text-align: center;">Keine News verfügbar</div>'; 
                return; 
            }}
            newsList.innerHTML = news.map(item => `<div class="news-item" data-category="${{item.category}}" data-source="${{item.source}}"><div class="news-meta"><span class="source-badge source-${{item.source}}">${{item.source}}</span><span class="category-badge">${{item.category}}</span><span class="priority-badge priority-${{item.priority}}">P${{item.priority}}</span><span class="age-badge">${{Math.round(item.age_hours)}}h alt</span></div><div class="news-title">${{item.title}}</div><div class="news-summary">${{item.summary}}</div>${{item.has_link ? `<a href="${{item.link}}" target="_blank" class="news-link">🔗 Vollständiger Artikel (für GPT)</a>` : ''}}</div>`).join('');
            setupFilters(news);
        }}
        
        function setupFilters(news) {{
            const filterButtons = document.querySelectorAll('.filter-btn'); 
            const newsItems = document.querySelectorAll('.news-item');
            filterButtons.forEach(button => {{ 
                button.addEventListener('click', () => {{ 
                    filterButtons.forEach(btn => btn.classList.remove('active')); 
                    button.classList.add('active'); 
                    const filter = button.dataset.filter; 
                    newsItems.forEach(item => {{ 
                        if (filter === 'all' || item.dataset.category === filter || item.dataset.source === filter) {{ 
                            item.classList.remove('hidden'); 
                        }} else {{ 
                            item.classList.add('hidden'); 
                        }} 
                    }}); 
                }}); 
            }});
        }}
        
        function displayWeather(weather) {{
            const weatherContent = document.getElementById('weather-content');
            if (!weather || !weather.current) {{ 
                weatherContent.innerHTML = '<div style="color: #e74c3c;">Keine Wetterdaten verfügbar</div>'; 
                return; 
            }}
            
            const current = weather.current;
            const forecast = weather.forecast || [];
            const outlook = weather.outlook || null;
            
            let weatherHtml = `
                <div class="weather-temp">${{current.temperature}}°C</div>
                <div class="weather-desc">${{current.description}}</div>
                <div class="weather-location">📍 ${{weather.location || 'Zürich'}}</div>
                <div style="margin-top: 15px; font-size: 0.9em; color: #7f8c8d;">
                    💨 ${{current.wind_speed}}km/h | 💧 ${{current.humidity}}%
                </div>
            `;
            
            // Outlook (Tomorrow) anzeigen
            if (outlook && outlook.tomorrow) {{
                const tom = outlook.tomorrow;
                weatherHtml += `
                    <div style="margin-top: 15px; padding: 10px; background: #ecf0f1; border-radius: 8px;">
                        <div style="font-weight: bold; margin-bottom: 5px;">🌅 Morgen</div>
                        <div>${{tom.temp_min}}°C - ${{tom.temp_max}}°C</div>
                        <div style="font-size: 0.9em; color: #7f8c8d;">${{tom.description}}</div>
                        ${{tom.precipitation > 0 ? `<div style="font-size: 0.9em;">🌧️ ${{tom.precipitation}}mm</div>` : ''}}
                    </div>
                `;
            }}
            
            // 5-Tage Forecast (kompakt)
            if (forecast.length > 0) {{
                weatherHtml += `
                    <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                        <div style="font-weight: bold; margin-bottom: 8px;">📅 5-Tage Forecast</div>
                        <div style="font-size: 0.8em;">
                `;
                
                forecast.slice(0, 3).forEach(day => {{
                    const date = new Date(day.date).toLocaleDateString('de-DE', {{weekday: 'short'}});
                    weatherHtml += `
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <span>${{date}}</span>
                            <span>${{Math.round(day.temp_min)}}°-${{Math.round(day.temp_max)}}°</span>
                        </div>
                    `;
                }});
                
                weatherHtml += `</div></div>`;
            }}
            
            weatherContent.innerHTML = weatherHtml;
        }}
        
        function displayCrypto(crypto) {{
            const cryptoContent = document.getElementById('crypto-content');
            if (!crypto || !crypto.bitcoin) {{ 
                cryptoContent.innerHTML = '<div style="color: #e74c3c;">Keine Bitcoin-Daten verfügbar</div>'; 
                return; 
            }}
            
            const bitcoin = crypto.bitcoin; 
            const trend = crypto.trend || null;
            const alerts = crypto.alerts || [];
            
            const change24h = bitcoin.change_24h || 0; 
            const changeClass = change24h >= 0 ? 'positive' : 'negative'; 
            const changeSymbol = change24h >= 0 ? '+' : '';
            
            let cryptoHtml = `
                <div class="crypto-price">$${{bitcoin.price_usd.toLocaleString()}}</div>
                <div class="crypto-change ${{changeClass}}">${{changeSymbol}}${{change24h.toFixed(1)}}% (24h)</div>
            `;
            
            // Trend-Analyse anzeigen
            if (trend && trend.message) {{
                cryptoHtml += `
                    <div style="margin: 15px 0; padding: 10px; background: #ecf0f1; border-radius: 8px; font-size: 0.9em;">
                        <div style="font-weight: bold; margin-bottom: 5px;">${{trend.emoji}} Trend</div>
                        <div>${{trend.message}}</div>
                    </div>
                `;
            }}
            
            // Alle Zeiträume anzeigen (wie im CLI)
            cryptoHtml += `
                <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                    <div style="font-weight: bold; margin-bottom: 8px;">📊 Alle Zeiträume</div>
                    <div style="font-size: 0.85em; line-height: 1.4;">
                        <div>1h: ${{bitcoin.change_1h ? (bitcoin.change_1h >= 0 ? '+' : '') + bitcoin.change_1h.toFixed(2) + '%' : 'N/A'}}</div>
                        <div>24h: ${{changeSymbol}}${{change24h.toFixed(2)}}%</div>
                        <div>7d: ${{bitcoin.change_7d ? (bitcoin.change_7d >= 0 ? '+' : '') + bitcoin.change_7d.toFixed(2) + '%' : 'N/A'}}</div>
                        <div>30d: ${{bitcoin.change_30d ? (bitcoin.change_30d >= 0 ? '+' : '') + bitcoin.change_30d.toFixed(2) + '%' : 'N/A'}}</div>
                        <div>60d: ${{bitcoin.change_60d ? (bitcoin.change_60d >= 0 ? '+' : '') + bitcoin.change_60d.toFixed(2) + '%' : 'N/A'}}</div>
                        <div>90d: ${{bitcoin.change_90d ? (bitcoin.change_90d >= 0 ? '+' : '') + bitcoin.change_90d.toFixed(2) + '%' : 'N/A'}}</div>
                    </div>
                </div>
            `;
            
            // Market Cap und Volume
            if (bitcoin.market_cap) {{
                cryptoHtml += `
                    <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 8px; font-size: 0.85em;">
                        <div>💰 Market Cap: $${{(bitcoin.market_cap / 1e12).toFixed(2)}}T</div>
                        ${{bitcoin.volume_24h ? `<div>📊 24h Volume: $${{(bitcoin.volume_24h / 1e9).toFixed(1)}}B</div>` : ''}}
                    </div>
                `;
            }}
            
            // Alerts anzeigen
            if (alerts && alerts.length > 0) {{
                cryptoHtml += `
                    <div style="margin-top: 15px; padding: 10px; background: #f8d7da; border-radius: 8px; font-size: 0.85em;">
                        <div style="font-weight: bold; color: #721c24;">🚨 Alerts</div>
                        ${{alerts.map(alert => `<div>${{alert.message}}</div>`).join('')}}
                    </div>
                `;
            }}
            
            cryptoContent.innerHTML = cryptoHtml;
        }}
        
        function displayTimestamp(timestamp) {{
            const timestampElement = document.getElementById('timestamp');
            if (timestamp) {{ 
                const date = new Date(timestamp); 
                timestampElement.textContent = `Daten gesammelt am: ${{date.toLocaleString('de-DE')}}`; 
            }} else {{ 
                timestampElement.textContent = 'Zeitstempel nicht verfügbar'; 
            }}
        }}
        
        // Daten beim Laden der Seite anzeigen
        document.addEventListener('DOMContentLoaded', loadData);
    </script>
</body>
</html>"""
        
        # Data Collection HTML speichern
        data_collection_path = os.path.join(outplay_dir, "data_collection.html")
        with open(data_collection_path, 'w', encoding='utf-8') as f:
            f.write(data_collection_html)
        
        logger.info("✅ Data Collection Dashboard (data_collection.html) generiert")
    
    async def _save_json_data(self, data: Dict[str, Any], outplay_dir: str):
        """Speichert die JSON-Daten für JavaScript"""
        
        import json
        
        # Saubere JSON-Daten speichern
        json_path = os.path.join(outplay_dir, "data_collection_clean.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("✅ JSON-Daten gespeichert (data_collection_clean.json)")
    
    def _generate_source_stats_html(self, sources: Dict[str, int]) -> str:
        """Generiert HTML für Quellen-Statistiken"""
        
        stats_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">'
        
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            stats_html += f'''
                <div style="background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center;">
                    <div class="source-badge source-{source}" style="display: inline-block; margin-bottom: 8px;">{source}</div>
                    <div style="font-size: 1.5em; font-weight: bold; color: #2c3e50;">{count}</div>
                    <div style="font-size: 0.9em; color: #7f8c8d;">Artikel</div>
                </div>
            '''
        
        stats_html += '</div>'
        return stats_html
    
    def _generate_news_table_html(self, news: List[Dict[str, Any]]) -> str:
        """Generiert HTML für News-Tabelle"""
        
        table_html = ""
        
        for item in news:
            age_hours = round(item.get('age_hours', 0))
            link_html = f'<a href="{item.get("link", "")}" target="_blank" class="news-link">🔗 Artikel</a>' if item.get('has_link') else 'Kein Link'
            
            table_html += f'''
                <tr>
                    <td><span class="source-badge source-{item.get('source', 'unknown')}">{item.get('source', 'Unknown')}</span></td>
                    <td>{item.get('category', 'general')}</td>
                    <td style="max-width: 400px;"><strong>{item.get('title', 'Kein Titel')}</strong></td>
                    <td style="max-width: 300px;">{item.get('summary', 'Keine Zusammenfassung')[:150]}...</td>
                    <td>{age_hours}h</td>
                    <td>{link_html}</td>
                </tr>
            '''
        
        return table_html
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _collect_all_news_safe(self, max_age_hours: int) -> List[Dict[str, Any]]:
        """
        Sammelt ALLE RSS News - konvertiert zu vollständigen JSON-Objekten
        Gibt ALLE verfügbaren Informationen zurück für GPT-Priorisierung
        """
        
        logger.info("📰 Sammle ALLE RSS News...")
        
        try:
            # DEBUG: Teste RSS Service direkt
            logger.info(f"🔧 DEBUG: Teste RSS Service mit max_age_hours={max_age_hours}")
            
            # Einfach die rohen RSS News Items holen
            news_items = await self.rss_service.get_all_recent_news(max_age_hours)
            
            logger.info(f"🔧 DEBUG: RSS Service returned {len(news_items) if news_items else 0} items")
            
            if not news_items:
                logger.warning("⚠️ Keine News gefunden")
                
                # ZUSÄTZLICHES DEBUGGING: Teste Feeds direkt
                logger.info("🔧 DEBUG: Teste aktive Feeds...")
                try:
                    feeds = await self.rss_service.get_all_active_feeds()
                    logger.info(f"🔧 DEBUG: {len(feeds)} aktive Feeds gefunden")
                    
                    if len(feeds) > 0:
                        logger.info(f"🔧 DEBUG: Erster Feed: {feeds[0].get('source_name', 'Unknown')}")
                        
                        # Teste ersten Feed direkt
                        try:
                            test_items = await self.rss_service.fetch_feed_items(feeds[0]['feed_url'])
                            logger.info(f"🔧 DEBUG: Erster Feed hat {len(test_items)} Items")
                        except Exception as feed_e:
                            logger.error(f"🔧 DEBUG: Feed-Test Fehler: {feed_e}")
                    
                except Exception as feeds_e:
                    logger.error(f"🔧 DEBUG: Feeds-Test Fehler: {feeds_e}")
                
                return []
            
            # Konvertiere RSSNewsItem Objekte zu vollständigen JSON-Dictionaries
            news_json = []
            for item in news_items:
                news_dict = {
                    "title": item.title,
                    "summary": item.summary,
                    "link": item.link,  # WICHTIG: URL für GPT
                    "published": item.published.isoformat(),
                    "source": item.source,
                    "category": item.category,
                    "priority": item.priority,
                    "weight": item.weight,
                    # Zusätzliche Metadaten für GPT
                    "published_timestamp": item.published.timestamp(),
                    "age_hours": (datetime.now() - item.published).total_seconds() / 3600,
                    "content_length": len(item.summary),
                    "has_link": bool(item.link),
                    "source_category": f"{item.source}_{item.category}"
                }
                news_json.append(news_dict)
            
            logger.info(f"✅ {len(news_json)} News als JSON gesammelt (mit URLs für GPT)")
            return news_json
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Sammeln der News: {e}")
            import traceback
            logger.error(f"🔧 DEBUG: Traceback: {traceback.format_exc()}")
            return []
    
    async def _collect_weather_safe(self) -> Dict[str, Any]:
        """Sammelt ALLE Wetter-Daten - Current Weather nur"""
        logger.info("🌤️ Hole ALLE Zürich Wetter-Daten...")
        
        try:
            # Sammle nur verfügbare Wetter-Informationen
            current = await self.weather_service.get_current_weather("zurich")
            
            # Zusammenfassen aller Wetter-Daten
            weather_data = {
                "current": current,
                "location": "Zürich",
                "timestamp": datetime.now().isoformat()
            }
            
            # Für Rückwärtskompatibilität - die wichtigsten Daten direkt verfügbar machen
            if weather_data["current"]:
                weather_data.update({
                    "temperature": weather_data["current"]["temperature"],
                    "description": weather_data["current"]["description"]
                })
            
            logger.info(f"✅ Zürich Wetter gesammelt (Current Weather)")
            return weather_data
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Wetter-Sammlung: {e}")
            return {}
    
    async def _collect_crypto_safe(self) -> Dict[str, Any]:
        """Sammelt ALLE Crypto-Daten - Bitcoin Price + Trend + Alerts"""
        logger.info("₿ Hole ALLE Crypto-Daten...")
        
        try:
            # Sammle ALLE verfügbaren Bitcoin-Informationen parallel
            price_task = self.crypto_service.get_bitcoin_price()
            trend_task = self.crypto_service.get_bitcoin_trend()
            alerts_task = self.crypto_service.get_bitcoin_alerts(price_threshold=100000)
            
            price_data, trend_data, alerts_data = await asyncio.gather(
                price_task, trend_task, alerts_task,
                return_exceptions=True
            )
            
            # Zusammenfassen aller Bitcoin-Daten
            crypto_data = {
                "bitcoin": price_data if not isinstance(price_data, Exception) else None,
                "trend": trend_data if not isinstance(trend_data, Exception) else None,
                "alerts": alerts_data if not isinstance(alerts_data, Exception) else [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Radio-formatierte Ausgaben für verschiedene Zeiträume
            if crypto_data["bitcoin"]:
                try:
                    radio_24h = self.crypto_service.format_for_radio(crypto_data["bitcoin"], "24h")
                    radio_7d = self.crypto_service.format_for_radio(crypto_data["bitcoin"], "7d")
                    
                    crypto_data["radio_formats"] = {
                        "24h": radio_24h,
                        "7d": radio_7d
                    }
                except Exception as e:
                    logger.warning(f"⚠️ Radio-Format-Generierung fehlgeschlagen: {e}")
            
            price = crypto_data["bitcoin"]["price_usd"] if crypto_data["bitcoin"] else "N/A"
            logger.info(f"✅ Bitcoin: ${price:,.0f} (mit Trend + Alerts)")
            return crypto_data
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Crypto-Sammlung: {e}")
            return {} 