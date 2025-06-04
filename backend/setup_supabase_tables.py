#!/usr/bin/env python3

"""
RadioX Supabase Tables Setup
Erstellt die notwendigen Tabellen in Supabase für RadioX
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from src.services.supabase_service import SupabaseService

async def create_radio_scripts_table():
    """Erstellt die radio_scripts Tabelle"""
    print("\n📋 ERSTELLE RADIO_SCRIPTS TABELLE")
    print("=" * 50)
    
    sql = """
    CREATE TABLE IF NOT EXISTS radio_scripts (
        id TEXT PRIMARY KEY,
        station_type TEXT NOT NULL,
        target_hour TIMESTAMPTZ NOT NULL,
        total_duration_seconds INTEGER NOT NULL DEFAULT 0,
        segment_count INTEGER NOT NULL DEFAULT 0,
        news_count INTEGER NOT NULL DEFAULT 0,
        tweet_count INTEGER NOT NULL DEFAULT 0,
        weather_city TEXT,
        script_data JSONB NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{}',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        status TEXT NOT NULL DEFAULT 'generated',
        
        -- Constraints
        CONSTRAINT valid_status CHECK (status IN ('generated', 'gpt_enhanced', 'audio_ready', 'published')),
        CONSTRAINT valid_station_type CHECK (station_type IN ('breaking_news', 'zueri_style', 'bitcoin_og', 'tradfi_news', 'tech_insider', 'swiss_local'))
    );
    
    -- Indexes für bessere Performance
    CREATE INDEX IF NOT EXISTS idx_radio_scripts_station_type ON radio_scripts(station_type);
    CREATE INDEX IF NOT EXISTS idx_radio_scripts_target_hour ON radio_scripts(target_hour);
    CREATE INDEX IF NOT EXISTS idx_radio_scripts_created_at ON radio_scripts(created_at);
    CREATE INDEX IF NOT EXISTS idx_radio_scripts_status ON radio_scripts(status);
    """
    
    try:
        service = SupabaseService()
        result = service.client.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ radio_scripts Tabelle erfolgreich erstellt")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der radio_scripts Tabelle: {e}")
        
        # Alternative: Direkte SQL Ausführung
        try:
            print("🔄 Versuche alternative Methode...")
            # Tabelle direkt erstellen
            result = service.client.table('radio_scripts').select('id').limit(1).execute()
            print("✅ radio_scripts Tabelle existiert bereits oder wurde erstellt")
            return True
        except Exception as e2:
            print(f"❌ Auch alternative Methode fehlgeschlagen: {e2}")
            print("💡 Erstelle die Tabelle manuell in der Supabase Console:")
            print("   1. Gehe zu https://supabase.com/dashboard")
            print("   2. Öffne dein Projekt")
            print("   3. Gehe zu 'SQL Editor'")
            print("   4. Führe das SQL aus backend/database/radio_scripts_schema.sql aus")
            return False

async def create_news_content_table():
    """Erstellt die news_content Tabelle (falls sie nicht existiert)"""
    print("\n📰 PRÜFE NEWS_CONTENT TABELLE")
    print("=" * 40)
    
    try:
        service = SupabaseService()
        # Teste ob Tabelle existiert
        result = service.client.table('news_content').select('id').limit(1).execute()
        print("✅ news_content Tabelle existiert bereits")
        return True
    except Exception as e:
        print(f"⚠️ news_content Tabelle nicht gefunden: {e}")
        print("💡 Diese Tabelle sollte bereits aus der ursprünglichen Migration existieren")
        print("   Falls nicht, führe die ursprünglichen Migrations-Skripte aus")
        return False

async def test_tables():
    """Testet die erstellten Tabellen"""
    print("\n🧪 TESTE TABELLEN")
    print("=" * 30)
    
    try:
        service = SupabaseService()
        
        # Test radio_scripts
        scripts = await service.list_radio_scripts(limit=1)
        print(f"✅ radio_scripts: {len(scripts)} Einträge gefunden")
        
        # Test news_content (falls verfügbar)
        try:
            news = await service.get_recent_content(limit=1)
            print(f"✅ news_content: {len(news)} Einträge gefunden")
        except:
            print("⚠️ news_content: Tabelle nicht verfügbar (aber nicht kritisch)")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Tabellen: {e}")
        return False

async def main():
    """Hauptfunktion"""
    print("🎙️ RADIOX SUPABASE TABLES SETUP")
    print("=" * 60)
    print("Erstellt die notwendigen Tabellen für RadioX in Supabase")
    print("=" * 60)
    
    try:
        # 1. Supabase-Verbindung testen
        print("\n🔗 TESTE SUPABASE VERBINDUNG")
        service = SupabaseService()
        print("✅ Supabase-Verbindung erfolgreich")
        
        # 2. radio_scripts Tabelle erstellen
        radio_scripts_ok = await create_radio_scripts_table()
        
        # 3. news_content Tabelle prüfen
        news_content_ok = await create_news_content_table()
        
        # 4. Tabellen testen
        if radio_scripts_ok:
            test_ok = await test_tables()
            
            if test_ok:
                print(f"\n🎉 SETUP ERFOLGREICH ABGESCHLOSSEN!")
                print("=" * 50)
                print("✅ Alle notwendigen Tabellen sind verfügbar")
                print("✅ RadioX kann jetzt Skripte in Supabase speichern")
                print("\n🚀 Führe jetzt 'python demo_supabase_integration.py' aus!")
            else:
                print(f"\n⚠️ SETUP TEILWEISE ERFOLGREICH")
                print("Tabellen wurden erstellt, aber Tests schlugen fehl")
        else:
            print(f"\n❌ SETUP FEHLGESCHLAGEN")
            print("Kritische Tabellen konnten nicht erstellt werden")
        
    except Exception as e:
        print(f"\n💥 KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 