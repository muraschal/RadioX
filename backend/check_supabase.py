#!/usr/bin/env python3

"""
Supabase Database Analyzer für RadioX
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.supabase_service import SupabaseService


async def analyze_supabase_db():
    """Analysiert die bestehende Supabase-Datenbank"""
    
    print("🔍 SUPABASE DATABASE ANALYSIS")
    print("=" * 50)
    
    try:
        service = SupabaseService()
        print("✅ Supabase-Verbindung erfolgreich")
        
        # 1. Radio Scripts Tabelle
        print("\n📊 RADIO_SCRIPTS TABELLE:")
        print("-" * 30)
        try:
            scripts = service.client.table('radio_scripts').select('*').limit(10).execute()
            print(f"📈 Anzahl Einträge: {len(scripts.data)}")
            
            if scripts.data:
                print("🔍 Beispiel-Einträge:")
                for i, script in enumerate(scripts.data[:3], 1):
                    print(f"  {i}. ID: {script.get('id', 'N/A')}")
                    print(f"     Station: {script.get('station_type', 'N/A')}")
                    print(f"     Status: {script.get('status', 'N/A')}")
                    print(f"     Erstellt: {script.get('created_at', 'N/A')}")
                    print()
        except Exception as e:
            print(f"❌ radio_scripts Fehler: {e}")
        
        # 2. Profiles Tabelle
        print("\n👤 PROFILES TABELLE:")
        print("-" * 30)
        try:
            profiles = service.client.table('profiles').select('*').limit(10).execute()
            print(f"📈 Anzahl Profile: {len(profiles.data)}")
            
            if profiles.data:
                print("🔍 Verfügbare Profile:")
                for i, profile in enumerate(profiles.data, 1):
                    name = profile.get('name', 'Unbekannt')
                    desc = profile.get('description', '')[:50]
                    print(f"  {i}. {name}: {desc}...")
        except Exception as e:
            print(f"❌ profiles Fehler: {e}")
        
        # 3. News Content Tabelle
        print("\n📰 NEWS_CONTENT TABELLE:")
        print("-" * 30)
        try:
            news = service.client.table('news_content').select('*').limit(5).execute()
            print(f"📈 Anzahl News: {len(news.data)}")
            
            if news.data:
                print("🔍 Letzte News:")
                for i, item in enumerate(news.data[:3], 1):
                    title = item.get('title', 'Kein Titel')[:40]
                    source = item.get('source', 'Unbekannt')
                    print(f"  {i}. {title}... ({source})")
        except Exception as e:
            print(f"❌ news_content Fehler: {e}")
        
        # 4. Weitere Tabellen erkunden
        print("\n🗂️ WEITERE TABELLEN:")
        print("-" * 30)
        
        table_names = [
            'broadcast_logs', 'persona_configs', 'voice_settings', 
            'content_templates', 'user_preferences'
        ]
        
        for table_name in table_names:
            try:
                result = service.client.table(table_name).select('*').limit(1).execute()
                print(f"✅ {table_name}: {len(result.data)} Einträge")
            except Exception as e:
                print(f"❌ {table_name}: Nicht verfügbar")
        
        print("\n🎯 ANALYSE ABGESCHLOSSEN")
        
    except Exception as e:
        print(f"💥 Hauptfehler: {e}")


if __name__ == "__main__":
    asyncio.run(analyze_supabase_db()) 