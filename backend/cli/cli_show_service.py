#!/usr/bin/env python3
"""
RadioX Show Service CLI
=======================

CLI-Tool für Show Service Testing und Management:
- Zeigt alle verfügbaren Show-Presets
- Testet Sprecher-Konfigurationen
- Bereitet Show-Generierung vor
- Zeigt Show-Statistiken
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.services.processing.show_service import ShowService, get_show_for_generation


async def show_all_presets():
    """Zeigt alle verfügbaren Show-Presets"""
    
    print("🎭 ALLE SHOW-PRESETS")
    print("=" * 60)
    
    service = ShowService()
    shows = await service.get_all_show_presets()
    
    if not shows:
        print("❌ Keine Show-Presets gefunden")
        return
    
    print(f"📊 {len(shows)} aktive Show-Presets gefunden:\n")
    
    for i, show in enumerate(shows, 1):
        print(f"🎭 {i}. {show.preset_name.upper()}")
        print(f"   📺 Name: {show.display_name}")
        print(f"   📝 Beschreibung: {show.description}")
        print(f"   🏙️ Stadt-Fokus: {show.city_focus}")
        print(f"   🎤 Sprecher: {show.primary_speaker}")
        print(f"   📰 Kategorien: {', '.join(show.news_categories)}")
        print(f"   🚫 Ausgeschlossen: {', '.join(show.exclude_categories)}")
        print(f"   ⭐ Min. Priorität: {show.min_priority}")
        print()


async def show_speakers():
    """Zeigt alle verfügbaren Sprecher"""
    
    print("🎤 ALLE SPRECHER")
    print("=" * 60)
    
    service = ShowService()
    speakers = await service.get_all_speakers()
    
    if not speakers:
        print("❌ Keine Sprecher gefunden")
        return
    
    print(f"📊 {len(speakers)} Sprecher verfügbar:\n")
    
    for i, speaker in enumerate(speakers, 1):
        print(f"🎤 {i}. {speaker['speaker_name'].upper()}")
        print(f"   🗣️ Voice Name: {speaker['voice_name']}")
        print(f"   🌍 Sprache: {speaker['language']}")
        print(f"   📝 Beschreibung: {speaker['description']}")
        print(f"   ⭐ Primary: {'Ja' if speaker['is_primary'] else 'Nein'}")
        print()


async def show_preset_details(preset_name: str):
    """Zeigt Details eines spezifischen Show-Presets"""
    
    print(f"🎯 SHOW-PRESET DETAILS: {preset_name.upper()}")
    print("=" * 60)
    
    service = ShowService()
    show = await service.get_show_preset(preset_name)
    
    if not show:
        print(f"❌ Show-Preset '{preset_name}' nicht gefunden")
        return
    
    print(f"🎭 Show-Information:")
    print(f"   📺 Name: {show.display_name}")
    print(f"   📝 Beschreibung: {show.description}")
    print(f"   🏙️ Stadt-Fokus: {show.city_focus}")
    print(f"   🎤 Sprecher: {show.primary_speaker}")
    print(f"   ✅ Aktiv: {'Ja' if show.is_active else 'Nein'}")
    
    print(f"\n📰 Content-Konfiguration:")
    print(f"   📋 Kategorien: {', '.join(show.news_categories)}")
    print(f"   🚫 Ausgeschlossen: {', '.join(show.exclude_categories)}")
    print(f"   ⭐ Min. Priorität: {show.min_priority}")
    print(f"   📊 Max. Feeds pro Kategorie: {show.max_feeds_per_category}")
    
    print(f"\n🔧 RSS-Filter:")
    if show.rss_feed_filter:
        print(json.dumps(show.rss_feed_filter, indent=4, ensure_ascii=False))
    else:
        print("   Kein RSS-Filter konfiguriert")
    
    print(f"\n📅 Metadaten:")
    print(f"   🆔 ID: {show.preset_id}")
    print(f"   📅 Erstellt: {show.created_at}")
    print(f"   🔄 Aktualisiert: {show.updated_at}")


async def prepare_generation(preset_name: str):
    """Bereitet Show-Generierung vor"""
    
    print(f"🎬 SHOW-GENERIERUNG VORBEREITUNG: {preset_name.upper()}")
    print("=" * 60)
    
    generation_config = await get_show_for_generation(preset_name)
    
    if not generation_config:
        print(f"❌ Generierungs-Konfiguration für '{preset_name}' konnte nicht erstellt werden")
        return
    
    print("✅ Generierungs-Konfiguration erfolgreich erstellt!\n")
    
    # Show Information
    show_info = generation_config["show"]
    print(f"🎭 Show-Information:")
    print(f"   📺 Name: {show_info['display_name']}")
    print(f"   📝 Beschreibung: {show_info['description']}")
    print(f"   🏙️ Stadt-Fokus: {show_info['city_focus']}")
    
    # Speaker Configuration
    speaker_info = generation_config["speaker"]
    print(f"\n🎤 Sprecher-Konfiguration:")
    print(f"   🗣️ Name: {speaker_info['voice_name']} ({speaker_info['speaker_name']})")
    print(f"   🆔 Voice ID: {speaker_info['voice_id']}")
    print(f"   🌍 Sprache: {speaker_info['language']}")
    print(f"   🎛️ Model: {speaker_info['model']}")
    print(f"   ⚙️ Settings:")
    for key, value in speaker_info['settings'].items():
        print(f"      {key}: {value}")
    
    # Content Configuration
    content_info = generation_config["content"]
    print(f"\n📰 Content-Konfiguration:")
    print(f"   📋 Kategorien: {', '.join(content_info['categories'])}")
    print(f"   🚫 Ausgeschlossen: {', '.join(content_info['exclude_categories'])}")
    print(f"   ⭐ Min. Priorität: {content_info['min_priority']}")
    print(f"   📊 Max. Feeds: {content_info['max_feeds_per_category']}")
    
    # Generation Settings
    settings_info = generation_config["settings"]
    print(f"\n⚙️ Generierungs-Einstellungen:")
    print(f"   🌍 Sprache: {settings_info['language']}")
    print(f"   🎛️ Voice Model: {settings_info['voice_model']}")
    print(f"   🕐 Zeitstempel: {settings_info['generation_timestamp']}")
    
    print(f"\n💾 Vollständige Konfiguration (JSON):")
    print(json.dumps(generation_config, indent=2, ensure_ascii=False, default=str))


async def show_statistics():
    """Zeigt Show-Statistiken"""
    
    print("📊 SHOW-STATISTIKEN")
    print("=" * 60)
    
    service = ShowService()
    stats = await service.get_show_statistics()
    
    if not stats:
        print("❌ Keine Statistiken verfügbar")
        return
    
    print(f"📈 Übersicht:")
    print(f"   📊 Gesamt Shows: {stats['total_shows']}")
    print(f"   ✅ Aktive Shows: {stats['active_shows']}")
    print(f"   ❌ Inaktive Shows: {stats['inactive_shows']}")
    print(f"   🎤 Gesamt Sprecher: {stats['total_speakers']}")
    
    print(f"\n🏙️ Verteilung nach Städten:")
    for city, shows in stats['city_distribution'].items():
        print(f"   {city}: {', '.join(shows)}")
    
    print(f"\n🎤 Verteilung nach Sprechern:")
    for speaker, shows in stats['speaker_distribution'].items():
        print(f"   {speaker}: {', '.join(shows)}")
    
    print(f"\n🗣️ Verfügbare Sprecher:")
    print(f"   {', '.join(stats['available_speakers'])}")
    
    print(f"\n🕐 Letzte Aktualisierung: {stats['last_updated']}")


async def test_all():
    """Führt alle Tests durch"""
    
    print("🧪 VOLLSTÄNDIGER SHOW SERVICE TEST")
    print("=" * 60)
    
    service = ShowService()
    
    # Test 1: Alle Show-Presets
    print("\n1️⃣ TESTE: Alle Show-Presets laden")
    shows = await service.get_all_show_presets()
    print(f"✅ {len(shows)} Shows geladen")
    
    # Test 2: Alle Sprecher
    print("\n2️⃣ TESTE: Alle Sprecher laden")
    speakers = await service.get_all_speakers()
    print(f"✅ {len(speakers)} Sprecher geladen")
    
    # Test 3: Spezifisches Preset
    if shows:
        test_preset = shows[0].preset_name
        print(f"\n3️⃣ TESTE: Spezifisches Preset laden ({test_preset})")
        preset = await service.get_show_preset(test_preset)
        if preset:
            print(f"✅ Preset '{test_preset}' geladen: {preset.display_name}")
    
    # Test 4: Sprecher-Konfiguration
    if speakers:
        test_speaker = speakers[0]["speaker_name"]
        print(f"\n4️⃣ TESTE: Sprecher-Konfiguration laden ({test_speaker})")
        speaker_config = await service.get_speaker_configuration(test_speaker)
        if speaker_config:
            print(f"✅ Sprecher '{test_speaker}' geladen: {speaker_config['voice_name']}")
    
    # Test 5: Show-Generierung vorbereiten
    if shows:
        test_preset = shows[0].preset_name
        print(f"\n5️⃣ TESTE: Show-Generierung vorbereiten ({test_preset})")
        generation_config = await service.prepare_show_generation(test_preset)
        if generation_config:
            print(f"✅ Generierungs-Konfiguration für '{test_preset}' erstellt")
    
    # Test 6: Statistiken
    print(f"\n6️⃣ TESTE: Show-Statistiken")
    stats = await service.get_show_statistics()
    if stats:
        print(f"✅ Statistiken geladen: {stats['active_shows']} aktive Shows")
    
    print(f"\n🎉 ALLE TESTS ABGESCHLOSSEN!")


async def main():
    """Haupt-CLI-Funktion"""
    
    parser = argparse.ArgumentParser(
        description="RadioX Show Service CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python cli_show_service.py --list                    # Alle Show-Presets anzeigen
  python cli_show_service.py --speakers                # Alle Sprecher anzeigen
  python cli_show_service.py --preset zurich           # Zürich Show-Details
  python cli_show_service.py --generate crypto         # Crypto Show-Generierung vorbereiten
  python cli_show_service.py --stats                   # Show-Statistiken
  python cli_show_service.py --test                    # Alle Tests durchführen
        """
    )
    
    parser.add_argument("--list", action="store_true", help="Alle Show-Presets anzeigen")
    parser.add_argument("--speakers", action="store_true", help="Alle Sprecher anzeigen")
    parser.add_argument("--preset", type=str, help="Details eines spezifischen Show-Presets")
    parser.add_argument("--generate", type=str, help="Show-Generierung für Preset vorbereiten")
    parser.add_argument("--stats", action="store_true", help="Show-Statistiken anzeigen")
    parser.add_argument("--test", action="store_true", help="Alle Tests durchführen")
    
    args = parser.parse_args()
    
    # Wenn keine Argumente, zeige Hilfe
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        if args.list:
            await show_all_presets()
        
        elif args.speakers:
            await show_speakers()
        
        elif args.preset:
            await show_preset_details(args.preset)
        
        elif args.generate:
            await prepare_generation(args.generate)
        
        elif args.stats:
            await show_statistics()
        
        elif args.test:
            await test_all()
    
    except KeyboardInterrupt:
        print("\n❌ Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 