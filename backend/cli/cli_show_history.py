#!/usr/bin/env python3
"""
🎙️ RadioX Show History CLI
Schneller Zugriff auf generierte Shows und Scripts
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import get_db

class ShowHistoryCLI:
    def __init__(self):
        self.db = get_db()
    
    async def get_latest_show(self) -> Optional[Dict[str, Any]]:
        """Hole die neueste Show"""
        try:
            result = self.db.client.table('broadcast_scripts').select('*').order('created_at', desc=True).limit(1).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Show: {e}")
            return None
    
    async def get_show_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Hole Show nach Session ID"""
        try:
            result = self.db.client.table('broadcast_scripts').select('*').eq('session_id', session_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Show {session_id}: {e}")
            return None
    
    async def list_recent_shows(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Liste der letzten Shows"""
        try:
            result = self.db.client.table('broadcast_scripts').select(
                'session_id, broadcast_style, estimated_duration_minutes, news_count, created_at'
            ).order('created_at', desc=True).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Show-Liste: {e}")
            return []
    
    def format_show_info(self, show: Dict[str, Any]) -> str:
        """Formatiere Show-Informationen"""
        created_at = datetime.fromisoformat(show['created_at'].replace('Z', '+00:00'))
        
        return f"""
📻 SESSION: {show['session_id']}
🕐 ZEIT: {created_at.strftime('%d.%m.%Y %H:%M')}
🎭 STIL: {show.get('broadcast_style', 'Unknown')}
⏱️ DAUER: {show.get('estimated_duration_minutes', 0)} Minuten
📰 NEWS: {show.get('news_count', 0)} Artikel
📝 SCRIPT: {len(show.get('script_content', ''))} Zeichen
"""
    
    def print_script_content(self, show: Dict[str, Any], max_lines: Optional[int] = None):
        """Drucke Script-Inhalt"""
        script = show.get('script_content', '')
        
        if not script:
            print("❌ Kein Script-Inhalt verfügbar")
            return
        
        lines = script.split('\n')
        
        if max_lines and len(lines) > max_lines:
            print(f"📜 SCRIPT (erste {max_lines} Zeilen):")
            print("=" * 60)
            for line in lines[:max_lines]:
                print(line)
            print("=" * 60)
            print(f"... ({len(lines) - max_lines} weitere Zeilen)")
        else:
            print("📜 KOMPLETTES SCRIPT:")
            print("=" * 60)
            print(script)
            print("=" * 60)

async def main():
    cli = ShowHistoryCLI()
    
    if len(sys.argv) < 2:
        print("""
🎙️ RADIOX SHOW HISTORY CLI
============================

BEFEHLE:
  latest              - Zeige letzte Show
  latest --script     - Zeige letzte Show mit Script
  list [anzahl]       - Liste letzte Shows (default: 10)
  show <session_id>   - Zeige spezifische Show
  script <session_id> - Zeige Script einer Show

BEISPIELE:
  python cli_show_history.py latest
  python cli_show_history.py latest --script
  python cli_show_history.py list 5
  python cli_show_history.py show ba890f69-ecc7-408a-908a-593c8471ca04
  python cli_show_history.py script ba890f69-ecc7-408a-908a-593c8471ca04
""")
        return
    
    command = sys.argv[1]
    
    if command == "latest":
        show = await cli.get_latest_show()
        if show:
            print("🎯 LETZTE SHOW:")
            print(cli.format_show_info(show))
            
            # Check if --script flag is provided
            if len(sys.argv) > 2 and sys.argv[2] == "--script":
                cli.print_script_content(show, max_lines=20)
        else:
            print("❌ Keine Shows gefunden")
    
    elif command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        shows = await cli.list_recent_shows(limit)
        
        if shows:
            print(f"📋 LETZTE {len(shows)} SHOWS:")
            print("=" * 80)
            for i, show in enumerate(shows, 1):
                created_at = datetime.fromisoformat(show['created_at'].replace('Z', '+00:00'))
                print(f"{i:2d}. {show['session_id'][:8]}... | {created_at.strftime('%d.%m %H:%M')} | {show.get('broadcast_style', 'Unknown')}")
        else:
            print("❌ Keine Shows gefunden")
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ Session ID erforderlich: python cli_show_history.py show <session_id>")
            return
        
        session_id = sys.argv[2]
        show = await cli.get_show_by_session(session_id)
        
        if show:
            print(f"🎯 SHOW {session_id}:")
            print(cli.format_show_info(show))
        else:
            print(f"❌ Show {session_id} nicht gefunden")
    
    elif command == "script":
        if len(sys.argv) < 3:
            print("❌ Session ID erforderlich: python cli_show_history.py script <session_id>")
            return
        
        session_id = sys.argv[2]
        show = await cli.get_show_by_session(session_id)
        
        if show:
            print(f"🎯 SCRIPT {session_id}:")
            cli.print_script_content(show)
        else:
            print(f"❌ Show {session_id} nicht gefunden")
    
    else:
        print(f"❌ Unbekannter Befehl: {command}")

if __name__ == "__main__":
    asyncio.run(main()) 