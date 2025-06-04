#!/usr/bin/env python3

"""
Supabase Tabellen Creator für RadioX
Erstellt alle benötigten Tabellen für News-Tracking und Script-Logging
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


async def create_supabase_tables():
    """Erstellt alle benötigten Supabase-Tabellen"""
    
    print("🏗️ SUPABASE TABELLEN CREATOR")
    print("=" * 50)
    
    try:
        service = SupabaseService()
        print("✅ Supabase-Verbindung erfolgreich")
        
        # 1. Broadcast Scripts Tabelle
        print("\n📊 ERSTELLE BROADCAST_SCRIPTS TABELLE:")
        print("-" * 40)
        
        broadcast_scripts_sql = """
        CREATE TABLE IF NOT EXISTS broadcast_scripts (
            id SERIAL PRIMARY KEY,
            session_id TEXT UNIQUE NOT NULL,
            script_content TEXT NOT NULL,
            script_preview TEXT,
            emotion_score FLOAT DEFAULT 0,
            urgency_level INTEGER DEFAULT 1,
            time_period TEXT,
            intro_style TEXT,
            script_data JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_broadcast_scripts_created_at 
        ON broadcast_scripts(created_at DESC);
        
        CREATE INDEX IF NOT EXISTS idx_broadcast_scripts_session_id 
        ON broadcast_scripts(session_id);
        """
        
        try:
            result = service.client.rpc('exec_sql', {'sql': broadcast_scripts_sql}).execute()
            print("✅ broadcast_scripts Tabelle erstellt")
        except Exception as e:
            print(f"⚠️ broadcast_scripts Tabelle: {e}")
        
        # 2. Used News Tabelle
        print("\n📰 ERSTELLE USED_NEWS TABELLE:")
        print("-" * 40)
        
        used_news_sql = """
        CREATE TABLE IF NOT EXISTS used_news (
            id SERIAL PRIMARY KEY,
            news_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            summary TEXT,
            used_at TIMESTAMPTZ DEFAULT NOW(),
            emotion_score FLOAT DEFAULT 0,
            urgency_level INTEGER DEFAULT 1
        );
        
        CREATE INDEX IF NOT EXISTS idx_used_news_news_id 
        ON used_news(news_id);
        
        CREATE INDEX IF NOT EXISTS idx_used_news_used_at 
        ON used_news(used_at DESC);
        
        CREATE INDEX IF NOT EXISTS idx_used_news_source 
        ON used_news(source);
        """
        
        try:
            result = service.client.rpc('exec_sql', {'sql': used_news_sql}).execute()
            print("✅ used_news Tabelle erstellt")
        except Exception as e:
            print(f"⚠️ used_news Tabelle: {e}")
        
        # 3. Broadcast Logs Tabelle
        print("\n📋 ERSTELLE BROADCAST_LOGS TABELLE:")
        print("-" * 40)
        
        broadcast_logs_sql = """
        CREATE TABLE IF NOT EXISTS broadcast_logs (
            id SERIAL PRIMARY KEY,
            event_type TEXT NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            data JSONB,
            session_id TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_broadcast_logs_timestamp 
        ON broadcast_logs(timestamp DESC);
        
        CREATE INDEX IF NOT EXISTS idx_broadcast_logs_event_type 
        ON broadcast_logs(event_type);
        
        CREATE INDEX IF NOT EXISTS idx_broadcast_logs_session_id 
        ON broadcast_logs(session_id);
        """
        
        try:
            result = service.client.rpc('exec_sql', {'sql': broadcast_logs_sql}).execute()
            print("✅ broadcast_logs Tabelle erstellt")
        except Exception as e:
            print(f"⚠️ broadcast_logs Tabelle: {e}")
        
        # 4. Cleanup Policy für alte Daten
        print("\n🧹 ERSTELLE CLEANUP POLICIES:")
        print("-" * 40)
        
        cleanup_sql = """
        -- Cleanup alte used_news (älter als 7 Tage)
        CREATE OR REPLACE FUNCTION cleanup_old_used_news()
        RETURNS void AS $$
        BEGIN
            DELETE FROM used_news 
            WHERE used_at < NOW() - INTERVAL '7 days';
        END;
        $$ LANGUAGE plpgsql;
        
        -- Cleanup alte broadcast_logs (älter als 30 Tage)
        CREATE OR REPLACE FUNCTION cleanup_old_broadcast_logs()
        RETURNS void AS $$
        BEGIN
            DELETE FROM broadcast_logs 
            WHERE timestamp < NOW() - INTERVAL '30 days';
        END;
        $$ LANGUAGE plpgsql;
        """
        
        try:
            result = service.client.rpc('exec_sql', {'sql': cleanup_sql}).execute()
            print("✅ Cleanup-Funktionen erstellt")
        except Exception as e:
            print(f"⚠️ Cleanup-Funktionen: {e}")
        
        # 5. Test-Insert
        print("\n🧪 TESTE TABELLEN:")
        print("-" * 40)
        
        try:
            # Test broadcast_logs
            test_log = {
                'event_type': 'table_creation_test',
                'data': {'message': 'Tabellen erfolgreich erstellt'},
                'session_id': 'setup_test'
            }
            
            result = service.client.table('broadcast_logs').insert(test_log).execute()
            if result.data:
                print("✅ broadcast_logs Test erfolgreich")
            
            # Test used_news
            test_news = {
                'news_id': 'test_news_123',
                'title': 'Test News für Tabellen-Setup',
                'source': 'test_source',
                'summary': 'Dies ist ein Test-Eintrag für die used_news Tabelle',
                'emotion_score': 0,
                'urgency_level': 1
            }
            
            result = service.client.table('used_news').insert(test_news).execute()
            if result.data:
                print("✅ used_news Test erfolgreich")
            
            # Test broadcast_scripts
            test_script = {
                'session_id': 'test_setup_script',
                'script_content': 'MARCEL: Test! JARVIS: Test erfolgreich!',
                'script_preview': 'MARCEL: Test! JARVIS: Test...',
                'emotion_score': 5.0,
                'urgency_level': 1,
                'time_period': 'setup',
                'intro_style': 'TEST',
                'script_data': {'test': True}
            }
            
            result = service.client.table('broadcast_scripts').insert(test_script).execute()
            if result.data:
                print("✅ broadcast_scripts Test erfolgreich")
                
        except Exception as e:
            print(f"⚠️ Test-Fehler: {e}")
        
        print("\n🎯 TABELLEN-SETUP ABGESCHLOSSEN!")
        print("=" * 50)
        print("📊 Verfügbare Tabellen:")
        print("  - broadcast_scripts (Script-Historie)")
        print("  - used_news (News-Tracking)")
        print("  - broadcast_logs (Event-Logging)")
        print("  - profiles (bereits vorhanden)")
        print("  - news_content (bereits vorhanden)")
        print()
        print("🚀 Das System ist bereit für intelligentes News-Tracking!")
        
    except Exception as e:
        print(f"💥 Hauptfehler: {e}")


if __name__ == "__main__":
    asyncio.run(create_supabase_tables()) 