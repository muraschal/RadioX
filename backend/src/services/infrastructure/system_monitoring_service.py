#!/usr/bin/env python3

"""
System Monitoring Service
=========================

Service für System-Überwachung und -Monitoring:
- Performance-Metriken
- Error-Tracking
- System-Health-Checks
- Datenbank-Cleanup
- Logging und Alerting
"""

import asyncio
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
from pathlib import Path

from .supabase_service import SupabaseService


class SystemMonitoringService:
    """
    Service für System-Monitoring und -Wartung
    
    Überwacht System-Performance, verwaltet Logs und
    führt Wartungsaufgaben durch.
    """
    
    def __init__(self):
        self.supabase = SupabaseService()
        
        # Monitoring-Konfiguration
        self.config = {
            "performance_check_interval": 300,  # 5 Minuten
            "log_retention_days": 30,
            "cleanup_interval_hours": 24,
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90,
                "error_rate": 10  # Fehler pro Stunde
            }
        }
        
        # Metriken-Cache
        self.metrics_cache = {
            "last_check": None,
            "system_stats": {},
            "error_counts": {},
            "performance_history": []
        }
    
    async def log_broadcast_creation(
        self, 
        broadcast_id: str, 
        metrics: Dict[str, Any]
    ) -> None:
        """Loggt die Erstellung eines Broadcasts"""
        
        try:
            log_data = {
                "session_id": broadcast_id,
                "event_type": "broadcast_created",
                "event_data": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.client.table('broadcast_logs').insert(log_data).execute()
            logger.info(f"📊 Broadcast-Erstellung geloggt: {broadcast_id}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Logging der Broadcast-Erstellung: {e}")
    
    async def log_error(self, error_type: str, error_message: str) -> None:
        """Loggt System-Fehler"""
        
        try:
            error_data = {
                "session_id": "system_monitoring",  # Fix: NOT NULL constraint
                "event_type": "system_error",
                "data": {
                    "error_type": error_type,
                    "error_message": error_message,
                    "system_stats": await self._get_current_system_stats()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.client.table('broadcast_logs').insert(error_data).execute()
            
            # Update Error-Counter
            current_hour = datetime.now().strftime("%Y-%m-%d-%H")
            if current_hour not in self.metrics_cache["error_counts"]:
                self.metrics_cache["error_counts"][current_hour] = 0
            self.metrics_cache["error_counts"][current_hour] += 1
            
            logger.error(f"🚨 System-Fehler geloggt: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Error-Logging: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Holt aktuellen System-Status"""
        
        logger.info("📊 Sammle System-Status")
        
        try:
            # System-Metriken
            system_stats = await self._get_current_system_stats()
            
            # Datenbank-Status
            db_status = await self._check_database_health()
            
            # Service-Status
            service_status = await self._check_service_health()
            
            # Performance-Metriken
            performance_metrics = await self._get_performance_metrics()
            
            # Error-Rate
            error_rate = self._calculate_error_rate()
            
            # Gesamt-Health-Score
            health_score = self._calculate_health_score(
                system_stats, db_status, service_status, error_rate
            )
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "health_score": health_score,
                "status": "healthy" if health_score > 0.8 else "warning" if health_score > 0.6 else "critical",
                "system_stats": system_stats,
                "database_status": db_status,
                "service_status": service_status,
                "performance_metrics": performance_metrics,
                "error_rate": error_rate,
                "alerts": self._generate_alerts(system_stats, error_rate)
            }
            
            # Cache aktualisieren
            self.metrics_cache["last_check"] = datetime.now()
            self.metrics_cache["system_stats"] = system_stats
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Sammeln des System-Status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "health_score": 0.0,
                "status": "error",
                "error": str(e)
            }
    
    async def cleanup_old_data(self, days_old: int = 7) -> Dict[str, Any]:
        """Räumt alte Daten auf"""
        
        logger.info(f"🧹 Starte Daten-Cleanup (älter als {days_old} Tage)")
        
        cleanup_results = {
            "broadcast_logs": 0,
            "old_logs": 0
        }
        
        try:
            # Cleanup alte broadcast_logs (älter als 30 Tage)
            cutoff_date = datetime.now() - timedelta(days=30)
            cutoff_iso = cutoff_date.isoformat()
            
            logs_response = self.supabase.client.table('broadcast_logs').delete().lt('timestamp', cutoff_iso).execute()
            cleanup_results["broadcast_logs"] = len(logs_response.data) if logs_response.data else 0
            
            logger.info(f"🧹 Cleanup abgeschlossen: {cleanup_results['broadcast_logs']} alte Logs gelöscht")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Cleanup: {e}")
            
        return cleanup_results
    
    async def test_monitoring(self) -> bool:
        """Testet das Monitoring-System"""
        
        try:
            # Test System-Status
            status = await self.get_system_status()
            
            # Test Error-Logging
            await self.log_error("test_error", "Test-Fehler für Monitoring-Test")
            
            # Test Event-Logging
            await self.log_system_event("test_event", {"test": True})
            
            return status.get("health_score", 0) > 0
            
        except Exception as e:
            logger.error(f"Monitoring Test Fehler: {e}")
            return False
    
    # Private Methods
    
    async def _get_current_system_stats(self) -> Dict[str, Any]:
        """Sammelt aktuelle System-Statistiken"""
        
        try:
            # CPU-Nutzung
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory-Nutzung
            memory = psutil.virtual_memory()
            
            # Disk-Nutzung
            disk = psutil.disk_usage('/')
            
            # Netzwerk-Statistiken
            network = psutil.net_io_counters()
            
            # Prozess-Informationen
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_memory_mb": round(process_memory.rss / (1024**2), 2),
                "process_cpu_percent": process.cpu_percent(),
                "uptime_seconds": int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds())
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim Sammeln der System-Stats: {e}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "error": str(e)
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Prüft Datenbank-Gesundheit"""
        
        try:
            # VEREINFACHTE DB-STRUKTUR PRÜFEN
            tables = ['rss_feed_preferences', 'voice_configurations', 'show_presets', 'broadcast_logs']
            
            health_data = {
                "database": {
                    "tables_accessible": 0,
                    "errors": []
                }
            }
            
            for table in tables:
                try:
                    response = self.supabase.client.table(table).select("*", count="exact").limit(1).execute()
                    table_count = response.count if hasattr(response, 'count') else len(response.data)
                    health_data["database"][f"{table}_count"] = table_count
                    
                    if table_count >= 0:
                        health_data["database"]["tables_accessible"] += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Tabelle {table} nicht erreichbar: {e}")
                    health_data["database"]["errors"].append(f"{table}: {str(e)}")
            
            # Gesamt-Gesundheit bewerten
            total_tables = len(tables)
            accessible_tables = health_data["database"]["tables_accessible"]
            
            if accessible_tables == total_tables:
                health_data["database"]["status"] = "healthy"
            elif accessible_tables > total_tables * 0.5:
                health_data["database"]["status"] = "degraded"
            else:
                health_data["database"]["status"] = "critical"
            
            return health_data
            
        except Exception as e:
            logger.error(f"❌ Datenbank-Health-Check Fehler: {e}")
            return {
                "connection_status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def _check_service_health(self) -> Dict[str, Any]:
        """Prüft Service-Gesundheit"""
        
        # Placeholder für Service-Health-Checks
        # In Produktion würden hier echte Service-Tests stattfinden
        
        return {
            "data_collection": "healthy",
            "content_processing": "healthy", 
            "broadcast_generation": "healthy",
            "audio_generation": "healthy",
            "last_check": datetime.now().isoformat()
        }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Sammelt Performance-Metriken"""
        
        try:
            # VEREINFACHT: Nur broadcast_logs verwenden (keine broadcast_scripts mehr)
            recent_broadcasts = self.supabase.client.table('broadcast_logs').select('*').eq('event_type', 'broadcast_generated').gte('timestamp', (datetime.now() - timedelta(hours=24)).isoformat()).execute()
            
            broadcasts_24h = len(recent_broadcasts.data) if recent_broadcasts.data else 0
            
            # Durchschnittliche Broadcast-Dauer aus broadcast_logs
            if recent_broadcasts.data:
                durations = []
                for b in recent_broadcasts.data:
                    data = b.get('data', {})
                    duration = data.get('estimated_duration_minutes', 0)
                    if duration > 0:
                        durations.append(duration)
                
                avg_duration = sum(durations) / len(durations) if durations else 0
            else:
                avg_duration = 0
            
            # Error-Logs der letzten 24h
            error_logs = self.supabase.client.table('broadcast_logs').select('*').eq('event_type', 'system_error').gte('timestamp', (datetime.now() - timedelta(hours=24)).isoformat()).execute()
            
            errors_24h = len(error_logs.data) if error_logs.data else 0
            
            return {
                "broadcasts_last_24h": broadcasts_24h,
                "average_broadcast_duration_min": round(avg_duration, 2),
                "errors_last_24h": errors_24h,
                "success_rate": round((broadcasts_24h / max(broadcasts_24h + errors_24h, 1)) * 100, 2)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim Sammeln der Performance-Metriken: {e}")
            return {
                "broadcasts_last_24h": 0,
                "average_broadcast_duration_min": 0,
                "errors_last_24h": 0,
                "success_rate": 0
            }
    
    def _calculate_error_rate(self) -> Dict[str, Any]:
        """Berechnet aktuelle Error-Rate"""
        
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        current_errors = self.metrics_cache["error_counts"].get(current_hour, 0)
        
        # Errors der letzten 24 Stunden
        last_24h_errors = 0
        now = datetime.now()
        
        for i in range(24):
            hour_key = (now - timedelta(hours=i)).strftime("%Y-%m-%d-%H")
            last_24h_errors += self.metrics_cache["error_counts"].get(hour_key, 0)
        
        return {
            "errors_current_hour": current_errors,
            "errors_last_24h": last_24h_errors,
            "error_rate_per_hour": round(last_24h_errors / 24, 2)
        }
    
    def _calculate_health_score(
        self, 
        system_stats: Dict[str, Any], 
        db_status: Dict[str, Any], 
        service_status: Dict[str, Any], 
        error_rate: Dict[str, Any]
    ) -> float:
        """Berechnet Gesamt-Health-Score (0-1)"""
        
        score = 1.0
        
        # System-Performance (40%)
        cpu_score = max(0, 1 - (system_stats.get("cpu_percent", 0) / 100))
        memory_score = max(0, 1 - (system_stats.get("memory_percent", 0) / 100))
        disk_score = max(0, 1 - (system_stats.get("disk_percent", 0) / 100))
        
        system_score = (cpu_score + memory_score + disk_score) / 3
        score *= (0.4 * system_score + 0.6)
        
        # Datenbank-Status (30%)
        db_score = 1.0 if db_status.get("connection_status") == "healthy" else 0.0
        score *= (0.3 * db_score + 0.7)
        
        # Error-Rate (30%)
        error_score = max(0, 1 - (error_rate.get("error_rate_per_hour", 0) / 10))
        score *= (0.3 * error_score + 0.7)
        
        return round(score, 3)
    
    def _generate_alerts(
        self, 
        system_stats: Dict[str, Any], 
        error_rate: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generiert System-Alerts"""
        
        alerts = []
        
        # CPU-Alert
        if system_stats.get("cpu_percent", 0) > self.config["alert_thresholds"]["cpu_usage"]:
            alerts.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": f"CPU-Nutzung bei {system_stats['cpu_percent']}%",
                "threshold": self.config["alert_thresholds"]["cpu_usage"]
            })
        
        # Memory-Alert
        if system_stats.get("memory_percent", 0) > self.config["alert_thresholds"]["memory_usage"]:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning",
                "message": f"Memory-Nutzung bei {system_stats['memory_percent']}%",
                "threshold": self.config["alert_thresholds"]["memory_usage"]
            })
        
        # Disk-Alert
        if system_stats.get("disk_percent", 0) > self.config["alert_thresholds"]["disk_usage"]:
            alerts.append({
                "type": "high_disk_usage",
                "severity": "critical",
                "message": f"Disk-Nutzung bei {system_stats['disk_percent']}%",
                "threshold": self.config["alert_thresholds"]["disk_usage"]
            })
        
        # Error-Rate-Alert
        if error_rate.get("error_rate_per_hour", 0) > self.config["alert_thresholds"]["error_rate"]:
            alerts.append({
                "type": "high_error_rate",
                "severity": "warning",
                "message": f"Error-Rate bei {error_rate['error_rate_per_hour']} Fehlern/Stunde",
                "threshold": self.config["alert_thresholds"]["error_rate"]
            })
        
        return alerts
    
    async def _get_table_sizes(self) -> Dict[str, Any]:
        """Holt Tabellen-Größen aus der Datenbank"""
        
        try:
            # VEREINFACHTE 4-TABELLEN-STRUKTUR
            tables = ['rss_feed_preferences', 'voice_configurations', 'show_presets', 'broadcast_logs']
            table_info = {}
            
            for table in tables:
                try:
                    response = self.supabase.client.table(table).select('*', count='exact').limit(1).execute()
                    table_info[table] = {
                        "row_count": response.count if hasattr(response, 'count') else 0
                    }
                except:
                    table_info[table] = {"row_count": 0, "error": "Zugriff fehlgeschlagen"}
            
            return table_info
            
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim Abrufen der Tabellen-Größen: {e}")
            return {}
    
    async def _cleanup_log_files(self, days_old: int) -> Dict[str, Any]:
        """Räumt alte Log-Dateien auf"""
        
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {"files_deleted": 0, "size_freed_mb": 0}
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            deleted_files = 0
            total_size_freed = 0
            
            for log_file in logs_dir.glob("*.log*"):
                if log_file.is_file():
                    file_time = log_file.stat().st_mtime
                    
                    if file_time < cutoff_time:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        deleted_files += 1
                        total_size_freed += file_size
            
            return {
                "files_deleted": deleted_files,
                "size_freed_mb": round(total_size_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim Log-Cleanup: {e}")
            return {"files_deleted": 0, "size_freed_mb": 0}
    
    async def log_system_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Loggt System-Events"""
        
        try:
            log_data = {
                "session_id": "system_monitoring",  # Fix: NOT NULL constraint
                "event_type": event_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.client.table('broadcast_logs').insert(log_data).execute()
            logger.info(f"📊 System-Event geloggt: {event_type}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim System-Event-Logging: {e}") 