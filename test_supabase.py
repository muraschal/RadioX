#!/usr/bin/env python3
"""
RadioX Supabase Connection Test
Testet die Verbindung zur Supabase-Datenbank
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.database.supabase_client import db
from backend.config.settings import get_settings

async def test_supabase_connection():
    """Testet die Supabase-Verbindung"""
    print("🔌 Teste Supabase-Verbindung...")
    
    try:
        # Test 1: Kategorien abrufen
        print("\n📊 Teste Content Categories...")
        result = db.client.table("content_categories").select("*").execute()
        categories = result.data
        
        print(f"✅ {len(categories)} Kategorien gefunden:")
        for cat in categories:
            print(f"   {cat['icon']} {cat['name']} ({cat['slug']})")
        
        # Test 2: Content Sources abrufen
        print("\n📡 Teste Content Sources...")
        result = db.client.table("content_sources").select("*").execute()
        sources = result.data
        
        print(f"✅ {len(sources)} Content Sources gefunden:")
        for source in sources[:5]:  # Nur erste 5 anzeigen
            print(f"   {source['source_type']}: {source['display_name']}")
        
        # Test 3: Test-Stream erstellen
        print("\n🎵 Teste Stream-Erstellung...")
        stream = await db.create_stream(
            title="Test Stream",
            description="Automatischer Test-Stream",
            persona="cyberpunk"
        )
        
        print(f"✅ Test-Stream erstellt: {stream['id']}")
        
        # Test 4: Stream wieder löschen
        print("\n🗑️ Lösche Test-Stream...")
        db.client.table("streams").delete().eq("id", stream['id']).execute()
        print("✅ Test-Stream gelöscht")
        
        print("\n🎉 Alle Tests erfolgreich! Supabase ist bereit.")
        return True
        
    except Exception as e:
        print(f"\n❌ Fehler bei Supabase-Test: {e}")
        print("\n🔧 Überprüfe:")
        print("   1. Ist das Schema in Supabase ausgeführt?")
        print("   2. Sind die API-Keys in .env korrekt?")
        print("   3. Ist die SUPABASE_URL richtig?")
        return False

async def show_config():
    """Zeigt die aktuelle Konfiguration"""
    settings = get_settings()
    
    print("⚙️ Aktuelle Konfiguration:")
    print(f"   Supabase URL: {settings.supabase_url}")
    print(f"   Audio Output: {settings.audio_output_dir}")
    print(f"   Temp Dir: {settings.temp_dir}")
    print(f"   Personas: {list(settings.personas.keys())}")
    print(f"   Stream Templates: {list(settings.stream_templates.keys())}")

if __name__ == "__main__":
    print("🚀 RadioX Supabase Test")
    print("=" * 50)
    
    asyncio.run(show_config())
    print()
    asyncio.run(test_supabase_connection()) 