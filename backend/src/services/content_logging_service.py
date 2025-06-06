#!/usr/bin/env python3
"""
Content Logging Service
=======================

Vollständige Protokollierung aller News-Inhalte und Scripts:
- Sammelt ALLE News-Artikel die gesammelt wurden
- Protokolliert finale Audio-Scripts
- Erstellt detaillierte Content-Reports
- Archiviert für Analyse und Compliance
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger
import sqlite3
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class NewsEntry:
    """Einzelner News-Artikel"""
    session_id: str
    source: str
    title: str
    summary: str
    url: str
    category: str
    timestamp: str
    content_hash: str
    selected_for_broadcast: bool
    priority_score: float


@dataclass
class ScriptEntry:
    """Finales Audio-Script"""
    session_id: str
    target_time: str
    script_content: str
    script_hash: str
    word_count: int
    estimated_duration: int
    generation_timestamp: str
    voice_config: Dict[str, Any]
    context_data: Dict[str, Any]


class ContentLoggingService:
    """
    Service für vollständige Content-Protokollierung
    
    Protokolliert ALLE gesammelten News-Artikel und finale Scripts
    für Compliance, Analyse und Archivierung.
    """
    
    def __init__(self):
        # Logging-Verzeichnisse
        self.logs_dir = Path("logs/content")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.reports_dir = Path("logs/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite-Datenbank für strukturierte Logs
        self.db_path = self.logs_dir / "content_logs.db"
        
        # Konfiguration
        self.config = {
            "max_log_age_days": 30,
            "enable_content_hashing": True,
            "enable_duplicate_detection": True,
            "log_level": "detailed",
            "archive_threshold_days": 7
        }
        
        # Datenbank wird beim ersten Aufruf initialisiert
        self.db_initialized = False
    
    async def log_collected_news(
        self,
        session_id: str,
        collected_news: List[Dict[str, Any]],
        selected_news: List[Dict[str, Any]],
        collection_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Protokolliert ALLE gesammelten News-Artikel
        
        Args:
            session_id: Session-ID
            collected_news: ALLE gesammelten News
            selected_news: Für Broadcast ausgewählte News
            collection_metadata: Metadaten der Sammlung
            
        Returns:
            Logging-Ergebnis
        """
        
        logger.info(f"📋 Protokolliere {len(collected_news)} News-Artikel für Session {session_id}")
        
        # Datenbank initialisieren (falls noch nicht geschehen)
        if not self.db_initialized:
            await self._init_database()
            self.db_initialized = True
        
        try:
            # 1. News-Einträge erstellen
            news_entries = []
            selected_urls = {news.get("url", "") for news in selected_news}
            
            for news_item in collected_news:
                # Content-Hash für Duplikat-Erkennung
                content_hash = self._generate_content_hash(news_item) if self.config["enable_content_hashing"] else ""
                
                news_entry = NewsEntry(
                    session_id=session_id,
                    source=news_item.get("source", "unknown"),
                    title=news_item.get("title", ""),
                    summary=news_item.get("summary", ""),
                    url=news_item.get("url", ""),
                    category=news_item.get("primary_category", "general"),
                    timestamp=datetime.now().isoformat(),
                    content_hash=content_hash,
                    selected_for_broadcast=news_item.get("url", "") in selected_urls,
                    priority_score=news_item.get("priority_score", 0.0)
                )
                
                news_entries.append(news_entry)
            
            # 2. In Datenbank speichern
            await self._save_news_entries(news_entries)
            
            # 3. JSON-Log erstellen
            json_log_path = await self._create_news_json_log(
                session_id, 
                news_entries, 
                collection_metadata
            )
            
            # 4. Duplikat-Analyse (falls aktiviert)
            duplicate_analysis = {}
            if self.config["enable_duplicate_detection"]:
                duplicate_analysis = await self._analyze_duplicates(news_entries)
            
            result = {
                "success": True,
                "session_id": session_id,
                "total_news_logged": len(news_entries),
                "selected_for_broadcast": len([n for n in news_entries if n.selected_for_broadcast]),
                "json_log_path": str(json_log_path),
                "duplicate_analysis": duplicate_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.success(f"✅ News-Protokollierung abgeschlossen: {len(news_entries)} Artikel")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei News-Protokollierung: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def log_final_script(
        self,
        session_id: str,
        script_content: str,
        script_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Protokolliert finales Audio-Script
        
        Args:
            session_id: Session-ID
            script_content: Finaler Script-Text
            script_metadata: Script-Metadaten
            
        Returns:
            Logging-Ergebnis
        """
        
        logger.info(f"📝 Protokolliere finales Script für Session {session_id}")
        
        # Datenbank initialisieren (falls noch nicht geschehen)
        if not self.db_initialized:
            await self._init_database()
            self.db_initialized = True
        
        try:
            # Script-Hash für Integrität
            script_hash = hashlib.sha256(script_content.encode()).hexdigest()[:16]
            
            # Word Count und Duration schätzen
            word_count = len(script_content.split())
            estimated_duration = int(word_count / 2.5 * 60)  # ~2.5 Wörter/Sekunde
            
            # Script-Entry erstellen
            script_entry = ScriptEntry(
                session_id=session_id,
                target_time=script_metadata.get("target_time", ""),
                script_content=script_content,
                script_hash=script_hash,
                word_count=word_count,
                estimated_duration=estimated_duration,
                generation_timestamp=datetime.now().isoformat(),
                voice_config=script_metadata.get("voice_config", {}),
                context_data=script_metadata.get("context_data", {})
            )
            
            # 1. In Datenbank speichern
            await self._save_script_entry(script_entry)
            
            # 2. Script-Datei speichern
            script_file_path = await self._save_script_file(script_entry)
            
            result = {
                "success": True,
                "session_id": session_id,
                "script_hash": script_hash,
                "word_count": word_count,
                "estimated_duration_seconds": estimated_duration,
                "script_file_path": str(script_file_path),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.success(f"✅ Script-Protokollierung abgeschlossen: {word_count} Wörter")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Script-Protokollierung: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_content_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        report_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Generiert Content-Report
        
        Args:
            start_date: Start-Datum (ISO format)
            end_date: End-Datum (ISO format)
            report_type: "summary", "detailed", "analytics"
            
        Returns:
            Content-Report
        """
        
        logger.info(f"📊 Generiere Content-Report ({report_type})")
        
        # Datenbank initialisieren (falls noch nicht geschehen)
        if not self.db_initialized:
            await self._init_database()
            self.db_initialized = True
        
        try:
            # Zeitraum bestimmen
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()
            
            # Daten aus Datenbank holen
            news_data = await self._get_news_data(start_date, end_date)
            script_data = await self._get_script_data(start_date, end_date)
            
            # Report generieren
            if report_type == "summary":
                report = await self._generate_summary_report(news_data, script_data, start_date, end_date)
            elif report_type == "detailed":
                report = await self._generate_detailed_report(news_data, script_data, start_date, end_date)
            elif report_type == "analytics":
                report = await self._generate_analytics_report(news_data, script_data, start_date, end_date)
            else:
                report = await self._generate_summary_report(news_data, script_data, start_date, end_date)
            
            # Report speichern
            report_file_path = await self._save_report(report, report_type)
            
            result = {
                "success": True,
                "report_type": report_type,
                "period": {"start": start_date, "end": end_date},
                "report_file_path": str(report_file_path),
                "report_data": report,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.success(f"✅ Content-Report generiert: {report_type}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Report-Generierung: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_content_logging(self) -> bool:
        """Testet das Content Logging"""
        
        # Mock News-Daten
        mock_collected_news = [
            {
                "source": "RSS Feed 1",
                "title": "Test News 1",
                "summary": "Test summary 1",
                "url": "https://test1.com",
                "primary_category": "tech",
                "priority_score": 0.8
            },
            {
                "source": "RSS Feed 2", 
                "title": "Test News 2",
                "summary": "Test summary 2",
                "url": "https://test2.com",
                "primary_category": "bitcoin_crypto",
                "priority_score": 0.9
            }
        ]
        
        mock_selected_news = [mock_collected_news[1]]  # Nur News 2 ausgewählt
        
        mock_script = """
        MARCEL: Guten Tag und willkommen zu RadioX News!
        JARVIS: Heute haben wir spannende Neuigkeiten aus der Tech-Welt.
        MARCEL: Bitcoin erreicht neue Höchststände...
        """
        
        try:
            # Test News Logging
            news_result = await self.log_collected_news(
                "test_logging",
                mock_collected_news,
                mock_selected_news,
                {"test": True}
            )
            
            # Test Script Logging
            script_result = await self.log_final_script(
                "test_logging",
                mock_script,
                {"target_time": "12:00", "test": True}
            )
            
            logger.info(f"Content Logging Test - News: {news_result['success']}, Script: {script_result['success']}")
            return news_result["success"] and script_result["success"]
            
        except Exception as e:
            logger.error(f"Content Logging Test Fehler: {e}")
            return False
    
    # Private Methods
    
    async def _init_database(self):
        """Initialisiert SQLite-Datenbank"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # News-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    source TEXT,
                    title TEXT,
                    summary TEXT,
                    url TEXT,
                    category TEXT,
                    timestamp TEXT,
                    content_hash TEXT,
                    selected_for_broadcast BOOLEAN,
                    priority_score REAL
                )
            ''')
            
            # Scripts-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS script_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    target_time TEXT,
                    script_content TEXT,
                    script_hash TEXT,
                    word_count INTEGER,
                    estimated_duration INTEGER,
                    generation_timestamp TEXT,
                    voice_config TEXT,
                    context_data TEXT
                )
            ''')
            
            # Indizes für Performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_session ON news_entries(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news_entries(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_script_session ON script_entries(session_id)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Content Logging Datenbank initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Datenbank-Initialisierung Fehler: {e}")
    
    def _generate_content_hash(self, content: Dict[str, Any]) -> str:
        """Generiert Content-Hash für Duplikat-Erkennung"""
        
        # Relevante Felder für Hash
        hash_content = f"{content.get('title', '')}{content.get('summary', '')}{content.get('url', '')}"
        return hashlib.sha256(hash_content.encode()).hexdigest()[:16]
    
    async def _save_news_entries(self, news_entries: List[NewsEntry]):
        """Speichert News-Einträge in Datenbank"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for entry in news_entries:
            cursor.execute('''
                INSERT INTO news_entries 
                (session_id, source, title, summary, url, category, timestamp, 
                 content_hash, selected_for_broadcast, priority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.session_id, entry.source, entry.title, entry.summary,
                entry.url, entry.category, entry.timestamp, entry.content_hash,
                entry.selected_for_broadcast, entry.priority_score
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_script_entry(self, script_entry: ScriptEntry):
        """Speichert Script-Entry in Datenbank"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO script_entries 
            (session_id, target_time, script_content, script_hash, word_count,
             estimated_duration, generation_timestamp, voice_config, context_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            script_entry.session_id, script_entry.target_time, script_entry.script_content,
            script_entry.script_hash, script_entry.word_count, script_entry.estimated_duration,
            script_entry.generation_timestamp, json.dumps(script_entry.voice_config),
            json.dumps(script_entry.context_data)
        ))
        
        conn.commit()
        conn.close()
    
    async def _create_news_json_log(
        self, 
        session_id: str, 
        news_entries: List[NewsEntry], 
        metadata: Dict[str, Any]
    ) -> Path:
        """Erstellt JSON-Log für News"""
        
        log_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "total_news": len(news_entries),
            "selected_news": len([n for n in news_entries if n.selected_for_broadcast]),
            "news_entries": [asdict(entry) for entry in news_entries]
        }
        
        log_filename = f"news_log_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path = self.logs_dir / log_filename
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return log_path
    
    async def _save_script_file(self, script_entry: ScriptEntry) -> Path:
        """Speichert Script als Textdatei"""
        
        script_filename = f"script_{script_entry.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        script_path = self.logs_dir / script_filename
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f"# RadioX Script - Session {script_entry.session_id}\n")
            f.write(f"# Generated: {script_entry.generation_timestamp}\n")
            f.write(f"# Target Time: {script_entry.target_time}\n")
            f.write(f"# Word Count: {script_entry.word_count}\n")
            f.write(f"# Estimated Duration: {script_entry.estimated_duration}s\n")
            f.write(f"# Hash: {script_entry.script_hash}\n\n")
            f.write(script_entry.script_content)
        
        return script_path
    
    async def _analyze_duplicates(self, news_entries: List[NewsEntry]) -> Dict[str, Any]:
        """Analysiert Duplikate"""
        
        hash_counts = {}
        for entry in news_entries:
            if entry.content_hash:
                hash_counts[entry.content_hash] = hash_counts.get(entry.content_hash, 0) + 1
        
        duplicates = {h: count for h, count in hash_counts.items() if count > 1}
        
        return {
            "total_unique_hashes": len(hash_counts),
            "duplicate_hashes": len(duplicates),
            "duplicate_details": duplicates
        }
    
    async def _get_news_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Holt News-Daten aus Datenbank"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM news_entries 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_date, end_date))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    async def _get_script_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Holt Script-Daten aus Datenbank"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM script_entries 
            WHERE generation_timestamp BETWEEN ? AND ?
            ORDER BY generation_timestamp DESC
        ''', (start_date, end_date))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    async def _generate_summary_report(
        self, 
        news_data: List[Dict[str, Any]], 
        script_data: List[Dict[str, Any]], 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """Generiert Summary-Report"""
        
        # News-Statistiken
        total_news = len(news_data)
        selected_news = len([n for n in news_data if n.get('selected_for_broadcast')])
        
        # Kategorien-Verteilung
        categories = {}
        for news in news_data:
            cat = news.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Script-Statistiken
        total_scripts = len(script_data)
        total_words = sum(s.get('word_count', 0) for s in script_data)
        
        return {
            "report_type": "summary",
            "period": {"start": start_date, "end": end_date},
            "news_stats": {
                "total_collected": total_news,
                "selected_for_broadcast": selected_news,
                "selection_rate": round(selected_news / total_news * 100, 1) if total_news > 0 else 0,
                "categories": categories
            },
            "script_stats": {
                "total_scripts": total_scripts,
                "total_words": total_words,
                "avg_words_per_script": round(total_words / total_scripts, 1) if total_scripts > 0 else 0
            },
            "generation_timestamp": datetime.now().isoformat()
        }
    
    async def _generate_detailed_report(
        self, 
        news_data: List[Dict[str, Any]], 
        script_data: List[Dict[str, Any]], 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """Generiert Detailed-Report"""
        
        summary = await self._generate_summary_report(news_data, script_data, start_date, end_date)
        
        # Detaillierte News-Liste (Top 20)
        detailed_news = news_data[:20]
        
        # Detaillierte Script-Liste
        detailed_scripts = [
            {
                "session_id": s.get("session_id"),
                "target_time": s.get("target_time"),
                "word_count": s.get("word_count"),
                "estimated_duration": s.get("estimated_duration"),
                "generation_timestamp": s.get("generation_timestamp")
            }
            for s in script_data
        ]
        
        summary.update({
            "report_type": "detailed",
            "detailed_news": detailed_news,
            "detailed_scripts": detailed_scripts
        })
        
        return summary
    
    async def _generate_analytics_report(
        self, 
        news_data: List[Dict[str, Any]], 
        script_data: List[Dict[str, Any]], 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """Generiert Analytics-Report"""
        
        summary = await self._generate_summary_report(news_data, script_data, start_date, end_date)
        
        # Erweiterte Analytics
        # Source-Analyse
        sources = {}
        for news in news_data:
            source = news.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        # Priority-Score Analyse
        priority_scores = [n.get('priority_score', 0) for n in news_data if n.get('priority_score')]
        avg_priority = sum(priority_scores) / len(priority_scores) if priority_scores else 0
        
        # Zeitliche Verteilung (nach Stunden)
        hourly_distribution = {}
        for script in script_data:
            target_time = script.get('target_time', '')
            if ':' in target_time:
                hour = target_time.split(':')[0]
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        summary.update({
            "report_type": "analytics",
            "analytics": {
                "source_distribution": sources,
                "avg_priority_score": round(avg_priority, 2),
                "hourly_distribution": hourly_distribution,
                "top_categories": dict(sorted(summary["news_stats"]["categories"].items(), key=lambda x: x[1], reverse=True)[:5])
            }
        })
        
        return summary
    
    async def _save_report(self, report: Dict[str, Any], report_type: str) -> Path:
        """Speichert Report als JSON"""
        
        report_filename = f"content_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.reports_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path 