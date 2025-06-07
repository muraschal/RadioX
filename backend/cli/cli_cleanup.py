#!/usr/bin/env python3
"""
RadioX Intelligent Cleanup
==========================

Intelligente Bereinigung die nur die wichtigsten Dateien behält:
- Letzte 2 Show-Logs (aktuell + vorherige)
- Alle anderen Logs/Dateien werden gelöscht
- Supabase DB bleibt unberührt (dort ist das Wissen gespeichert)

Usage:
    python cli/cli_cleanup.py --dry-run    # Zeigt was gelöscht würde
    python cli/cli_cleanup.py --execute    # Führt Cleanup aus
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import re

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))


class IntelligentCleanup:
    """Intelligente Cleanup-Logik für RadioX"""
    
    def __init__(self, backend_path: str = None):
        self.backend_path = Path(backend_path or Path(__file__).parent.parent)
        self.deleted_files = []
        self.kept_files = []
        self.total_size_deleted = 0
    
    def analyze_files(self):
        """Analysiert alle Dateien und kategorisiert sie"""
        
        print("🔍 ANALYSIERE DATEIEN...")
        print("=" * 50)
        
        # 1. LOG-DATEIEN
        log_files = self._find_log_files()
        print(f"📋 Log-Dateien gefunden: {len(log_files)}")
        
        # 2. TEST-DATEIEN  
        test_files = self._find_test_files()
        print(f"🧪 Test-Dateien gefunden: {len(test_files)}")
        
        # 3. AUDIO/COVER-DATEIEN
        media_files = self._find_media_files()
        print(f"🎵 Media-Dateien gefunden: {len(media_files)}")
        
        # 4. TEMP-DATEIEN
        temp_files = self._find_temp_files()
        print(f"🗑️ Temp-Dateien gefunden: {len(temp_files)}")
        
        return {
            'logs': log_files,
            'tests': test_files, 
            'media': media_files,
            'temp': temp_files
        }
    
    def _find_log_files(self):
        """Findet alle Log-Dateien"""
        patterns = [
            'logs/*.log',
            'radiox_master_*.log',
            '*.log',
            # ERWEITERTE PATTERNS FÜR ALLE LOG-DATEIEN
            'logs/radiox_master_*.log',  # Explizit logs-Ordner
            'logs/**/*.log',  # Alle Logs in Unterordnern
        ]
        
        log_files = []
        for pattern in patterns:
            files = glob.glob(str(self.backend_path / pattern), recursive=True)
            log_files.extend(files)
        
        return list(set(log_files))  # Duplikate entfernen
    
    def _find_test_files(self):
        """Findet alle Test-Dateien"""
        patterns = [
            'news_log_*.json',
            'script_test_*.txt', 
            'script_cli_*.txt',
            'content/news_log_*.json',
            'content/script_*.txt',
            # ERWEITERTE PATTERNS FÜR ALLE SICHTBAREN MÜLL-DATEIEN
            'content/news_log_cli_logging_test_*.json',
            'content/script_cli_logging_test_*.txt',
            'content/script_test_logging_*.txt',
            'logs/content/*',  # Alles im content-Unterordner von logs
            # ALLE GEFUNDENEN PATTERNS
            'logs/content/news_log_*.json',
            'logs/content/script_*.txt',
        ]
        
        test_files = []
        for pattern in patterns:
            files = glob.glob(str(self.backend_path / pattern), recursive=True)
            test_files.extend(files)
        
        return test_files
    
    def _find_media_files(self):
        """Findet alle Media-Dateien (Audio/Cover)"""
        patterns = [
            'output/audio/*.mp3',
            'output/audio/*.wav',
            'output/covers/*.png',
            'output/covers/*.jpg',
            'cover_*.png',
            'audio_*.mp3'
        ]
        
        media_files = []
        for pattern in patterns:
            files = glob.glob(str(self.backend_path / pattern))
            media_files.extend(files)
        
        return media_files
    
    def _find_temp_files(self):
        """Findet temporäre Dateien"""
        patterns = [
            '*.tmp',
            '*.temp',
            '__pycache__/*',
            '.pytest_cache/*',
            'test_*.py',
            'check_*.py',
            'debug_*.py'
        ]
        
        temp_files = []
        for pattern in patterns:
            files = glob.glob(str(self.backend_path / pattern), recursive=True)
            temp_files.extend(files)
        
        return temp_files
    
    def get_cleanup_plan(self, files_dict):
        """Erstellt intelligenten Cleanup-Plan"""
        
        print("\n🎯 CLEANUP-PLAN ERSTELLEN...")
        print("=" * 50)
        
        cleanup_plan = {
            'delete': [],
            'keep': []
        }
        
        # 1. LOG-DATEIEN: Nur letzte 2 RadioX Master Logs behalten
        log_files = files_dict['logs']
        radiox_logs = [f for f in log_files if 'radiox_master_' in f]
        
        if radiox_logs:
            # Sortiere nach Datum (neueste zuerst)
            radiox_logs.sort(key=lambda x: self._extract_date_from_filename(x), reverse=True)
            
            # Behalte nur die letzten 2
            keep_logs = radiox_logs[:2]
            delete_logs = radiox_logs[2:] + [f for f in log_files if f not in radiox_logs]
            
            cleanup_plan['keep'].extend(keep_logs)
            cleanup_plan['delete'].extend(delete_logs)
            
            print(f"📋 Logs behalten: {len(keep_logs)}")
            print(f"📋 Logs löschen: {len(delete_logs)}")
        
        # 2. TEST-DATEIEN: Alle löschen (sind nur temporär)
        test_files = files_dict['tests']
        cleanup_plan['delete'].extend(test_files)
        print(f"🧪 Test-Dateien löschen: {len(test_files)}")
        
        # 3. MEDIA-DATEIEN: Nur letzte 2 Shows behalten
        media_files = files_dict['media']
        if media_files:
            # Sortiere nach Änderungsdatum
            media_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Behalte nur die letzten 4 Dateien (2 Shows = je Audio + Cover)
            keep_media = media_files[:4]
            delete_media = media_files[4:]
            
            cleanup_plan['keep'].extend(keep_media)
            cleanup_plan['delete'].extend(delete_media)
            
            print(f"🎵 Media behalten: {len(keep_media)}")
            print(f"🎵 Media löschen: {len(delete_media)}")
        
        # 4. TEMP-DATEIEN: Alle löschen
        temp_files = files_dict['temp']
        cleanup_plan['delete'].extend(temp_files)
        print(f"🗑️ Temp-Dateien löschen: {len(temp_files)}")
        
        return cleanup_plan
    
    def _extract_date_from_filename(self, filename):
        """Extrahiert Datum aus Dateiname für Sortierung"""
        try:
            # Pattern: radiox_master_2025-06-07_09-23-46_910285.log
            match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', filename)
            if match:
                date_str = match.group(1)
                return datetime.strptime(date_str, '%Y-%m-%d_%H-%M-%S')
        except:
            pass
        
        # Fallback: Datei-Änderungsdatum
        return datetime.fromtimestamp(os.path.getmtime(filename))
    
    def execute_cleanup(self, cleanup_plan, dry_run=True):
        """Führt Cleanup aus"""
        
        if dry_run:
            print("\n🔍 DRY RUN - ZEIGE WAS GELÖSCHT WÜRDE:")
        else:
            print("\n🗑️ FÜHRE CLEANUP AUS:")
        
        print("=" * 50)
        
        total_size = 0
        delete_count = 0
        
        for file_path in cleanup_plan['delete']:
            try:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    delete_count += 1
                    
                    size_mb = file_size / (1024 * 1024)
                    rel_path = os.path.relpath(file_path, self.backend_path)
                    
                    if dry_run:
                        print(f"🗑️ WÜRDE LÖSCHEN: {rel_path} ({size_mb:.1f} MB)")
                    else:
                        os.remove(file_path)
                        print(f"✅ GELÖSCHT: {rel_path} ({size_mb:.1f} MB)")
                        self.deleted_files.append(file_path)
                        self.total_size_deleted += file_size
                        
            except Exception as e:
                print(f"❌ Fehler bei {file_path}: {e}")
        
        # BEHALTEN
        print(f"\n📁 DATEIEN BEHALTEN:")
        for file_path in cleanup_plan['keep']:
            if os.path.exists(file_path):
                rel_path = os.path.relpath(file_path, self.backend_path)
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                print(f"✅ BEHALTEN: {rel_path} ({file_size:.1f} MB)")
                self.kept_files.append(file_path)
        
        # ZUSAMMENFASSUNG
        total_mb = total_size / (1024 * 1024)
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   🗑️ Dateien gelöscht: {delete_count}")
        print(f"   📁 Dateien behalten: {len(cleanup_plan['keep'])}")
        print(f"   💾 Speicher freigegeben: {total_mb:.1f} MB")
        
        if dry_run:
            print(f"\n⚠️ DRY RUN - Keine Dateien wurden tatsächlich gelöscht!")
            print(f"   Führe mit --execute aus um Cleanup durchzuführen")
        
        return delete_count, total_mb


def main():
    """Hauptfunktion"""
    
    parser = argparse.ArgumentParser(
        description="RadioX Intelligent Cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python cli/cli_cleanup.py --dry-run     # Zeigt was gelöscht würde
  python cli/cli_cleanup.py --execute     # Führt Cleanup aus
  python cli/cli_cleanup.py --analyze     # Nur Analyse, kein Cleanup
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Zeigt nur was gelöscht würde (Standard)"
    )
    
    parser.add_argument(
        "--execute", 
        action="store_true",
        help="Führt Cleanup tatsächlich aus"
    )
    
    parser.add_argument(
        "--analyze",
        action="store_true", 
        help="Nur Analyse, kein Cleanup"
    )
    
    args = parser.parse_args()
    
    # Standard ist dry-run
    if not args.execute and not args.analyze:
        args.dry_run = True
    
    print("🧹 RADIOX INTELLIGENT CLEANUP")
    print("=" * 50)
    print("💡 Behält nur: Letzte 2 Shows + Supabase DB (unberührt)")
    print("🗑️ Löscht: Alle anderen Logs, Tests, Media, Temp-Dateien")
    print()
    
    cleanup = IntelligentCleanup()
    
    try:
        # 1. ANALYSE
        files_dict = cleanup.analyze_files()
        
        if args.analyze:
            print("\n✅ ANALYSE ABGESCHLOSSEN")
            return
        
        # 2. CLEANUP-PLAN
        cleanup_plan = cleanup.get_cleanup_plan(files_dict)
        
        # 3. AUSFÜHRUNG
        if args.execute:
            confirm = input(f"\n⚠️ WARNUNG: {len(cleanup_plan['delete'])} Dateien werden gelöscht! Fortfahren? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Cleanup abgebrochen")
                return
        
        delete_count, size_mb = cleanup.execute_cleanup(cleanup_plan, dry_run=not args.execute)
        
        if args.execute:
            print(f"\n🎉 CLEANUP ERFOLGREICH!")
            print(f"   📁 {delete_count} Dateien gelöscht")
            print(f"   💾 {size_mb:.1f} MB freigegeben")
            print(f"   🗄️ Supabase DB unberührt (Wissen erhalten)")
        
    except KeyboardInterrupt:
        print("\n❌ Cleanup abgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler beim Cleanup: {e}")


if __name__ == "__main__":
    main() 