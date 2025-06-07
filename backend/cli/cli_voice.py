#!/usr/bin/env python3
"""
🎤 RadioX Voice Configuration CLI
Voice-Management über Supabase statt hardcoded Definitionen
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.voice_config_service import get_voice_config_service


async def list_voices():
    """Zeigt alle Voice-Konfigurationen"""
    
    print("🎤 VOICE-KONFIGURATIONEN")
    print("=" * 60)
    
    service = get_voice_config_service()
    
    try:
        # Hole alle Voices
        all_voices = await service.get_all_voice_configs()
        
        if not all_voices:
            print("❌ Keine Voice-Konfigurationen gefunden")
            return
        
        # Gruppiere nach Sprache
        by_language = {}
        for speaker, config in all_voices.items():
            lang = config["language"]
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append((speaker, config))
        
        # Zeige Voices gruppiert nach Sprache
        for language, voices in by_language.items():
            print(f"\n🌍 SPRACHE: {language.upper()}")
            print("-" * 40)
            
            for speaker, config in voices:
                primary = "⭐ PRIMARY" if config["is_primary"] else ""
                active = "✅" if config["is_active"] else "❌"
                
                print(f"  {active} {speaker}")
                print(f"     Voice: {config['voice_name']} ({config['voice_id']})")
                print(f"     Model: {config['model']}")
                print(f"     Settings: Stability={config['stability']}, Style={config['style']}")
                print(f"     Description: {config['description']} {primary}")
                print()
        
        print(f"📊 TOTAL: {len(all_voices)} Voice-Konfigurationen")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Voices: {e}")


async def show_voice_stats():
    """Zeigt Voice-Statistiken"""
    
    print("📊 VOICE-STATISTIKEN")
    print("=" * 40)
    
    service = get_voice_config_service()
    
    try:
        stats = await service.get_voice_stats()
        
        if "error" in stats:
            print(f"❌ Fehler: {stats['error']}")
            return
        
        print(f"📈 ÜBERSICHT:")
        print(f"   Total Voices: {stats['total']}")
        print(f"   Aktive Voices: {stats['active']}")
        print(f"   Primary Voices: {stats['primary']}")
        print(f"   Sprachen: {', '.join(stats['languages'])}")
        print(f"   Cache Status: {stats['cache_status']}")
        
        print(f"\n🌍 NACH SPRACHE:")
        for lang, lang_stats in stats['by_language'].items():
            print(f"   {lang.upper()}: {lang_stats['active']}/{lang_stats['total']} aktiv, {lang_stats['primary']} primary")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Statistiken: {e}")


async def test_voice(speaker_name: str):
    """Testet eine spezifische Voice-Konfiguration"""
    
    print(f"🧪 TESTE VOICE: {speaker_name}")
    print("=" * 40)
    
    service = get_voice_config_service()
    
    try:
        # Lade Voice-Konfiguration
        voice_config = await service.get_voice_config(speaker_name)
        
        if not voice_config:
            print(f"❌ Voice '{speaker_name}' nicht gefunden")
            return
        
        print(f"✅ Voice-Konfiguration gefunden:")
        print(f"   Voice Name: {voice_config['voice_name']}")
        print(f"   Voice ID: {voice_config['voice_id']}")
        print(f"   Sprache: {voice_config['language']}")
        print(f"   Model: {voice_config['model']}")
        print(f"   Primary: {'Ja' if voice_config['is_primary'] else 'Nein'}")
        print(f"   Aktiv: {'Ja' if voice_config.get('is_active', True) else 'Nein'}")
        
        print(f"\n🎛️ PARAMETER:")
        print(f"   Stability: {voice_config['stability']}")
        print(f"   Similarity Boost: {voice_config['similarity_boost']}")
        print(f"   Style: {voice_config['style']}")
        print(f"   Speaker Boost: {'Ja' if voice_config['use_speaker_boost'] else 'Nein'}")
        
        print(f"\n📝 BESCHREIBUNG:")
        print(f"   {voice_config['description']}")
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Voice: {e}")


async def show_primary_voices():
    """Zeigt nur Primary Voice-Konfigurationen"""
    
    print("⭐ PRIMARY VOICE-KONFIGURATIONEN")
    print("=" * 50)
    
    service = get_voice_config_service()
    
    try:
        primary_voices = await service.get_primary_voices()
        
        if not primary_voices:
            print("❌ Keine Primary Voice-Konfigurationen gefunden")
            return
        
        for speaker, config in primary_voices.items():
            print(f"🎤 {speaker.upper()}")
            print(f"   Voice: {config['voice_name']} ({config['language']})")
            print(f"   ID: {config['voice_id']}")
            print(f"   Model: {config['model']}")
            print(f"   Description: {config['description']}")
            print()
        
        print(f"📊 TOTAL: {len(primary_voices)} Primary Voices")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Primary Voices: {e}")


async def show_voices_by_language(language: str):
    """Zeigt Voices für eine bestimmte Sprache"""
    
    print(f"🌍 VOICES FÜR SPRACHE: {language.upper()}")
    print("=" * 50)
    
    service = get_voice_config_service()
    
    try:
        language_voices = await service.get_voices_by_language(language)
        
        if not language_voices:
            print(f"❌ Keine Voice-Konfigurationen für Sprache '{language}' gefunden")
            return
        
        for speaker, config in language_voices.items():
            primary = "⭐ PRIMARY" if config["is_primary"] else ""
            active = "✅" if config.get("is_active", True) else "❌"
            
            print(f"{active} {speaker} - {config['voice_name']} {primary}")
            print(f"   ID: {config['voice_id']}")
            print(f"   Model: {config['model']}")
            print(f"   Description: {config['description']}")
            print()
        
        print(f"📊 TOTAL: {len(language_voices)} Voices für Sprache '{language}'")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Voices für Sprache '{language}': {e}")


async def test_voice_service():
    """Testet den kompletten Voice Configuration Service"""
    
    print("🧪 VOICE CONFIGURATION SERVICE TEST")
    print("=" * 60)
    
    service = get_voice_config_service()
    
    try:
        success = await service.test_voice_service()
        
        if success:
            print("\n🎉 ALLE TESTS ERFOLGREICH!")
            
            # Zeige zusätzliche Informationen
            stats = await service.get_voice_stats()
            print(f"\n📊 SERVICE-STATISTIKEN:")
            print(f"   {stats['total']} Voice-Konfigurationen verfügbar")
            print(f"   {stats['active']} aktive Voices")
            print(f"   {stats['primary']} Primary Voices")
            print(f"   Sprachen: {', '.join(stats['languages'])}")
            
        else:
            print("❌ VOICE SERVICE TEST FEHLGESCHLAGEN!")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen des Voice Service: {e}")


async def activate_voice(speaker_name: str):
    """Aktiviert eine Voice-Konfiguration"""
    
    print(f"✅ AKTIVIERE VOICE: {speaker_name}")
    print("=" * 40)
    
    service = get_voice_config_service()
    
    try:
        success = await service.activate_voice(speaker_name)
        
        if success:
            print(f"✅ Voice '{speaker_name}' erfolgreich aktiviert")
        else:
            print(f"❌ Fehler beim Aktivieren der Voice '{speaker_name}'")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")


async def deactivate_voice(speaker_name: str):
    """Deaktiviert eine Voice-Konfiguration"""
    
    print(f"❌ DEAKTIVIERE VOICE: {speaker_name}")
    print("=" * 40)
    
    service = get_voice_config_service()
    
    try:
        success = await service.deactivate_voice(speaker_name)
        
        if success:
            print(f"❌ Voice '{speaker_name}' erfolgreich deaktiviert")
        else:
            print(f"❌ Fehler beim Deaktivieren der Voice '{speaker_name}'")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")


async def main():
    """Hauptfunktion"""
    
    parser = argparse.ArgumentParser(description="🎤 RadioX Voice Configuration CLI")
    
    subparsers = parser.add_subparsers(dest="action", help="Verfügbare Aktionen")
    
    # List command
    subparsers.add_parser("list", help="Zeige alle Voice-Konfigurationen")
    
    # Stats command
    subparsers.add_parser("stats", help="Zeige Voice-Statistiken")
    
    # Primary command
    subparsers.add_parser("primary", help="Zeige Primary Voice-Konfigurationen")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Teste Voice-Konfiguration")
    test_parser.add_argument("speaker", nargs="?", help="Speaker-Name (optional)")
    
    # Language command
    lang_parser = subparsers.add_parser("language", help="Zeige Voices für Sprache")
    lang_parser.add_argument("lang", help="Sprach-Code (en, de, etc.)")
    
    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Aktiviere Voice")
    activate_parser.add_argument("speaker", help="Speaker-Name")
    
    # Deactivate command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deaktiviere Voice")
    deactivate_parser.add_argument("speaker", help="Speaker-Name")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        return
    
    print("🎤 RADIOX VOICE CONFIGURATION CLI")
    print("=" * 60)
    
    try:
        if args.action == "list":
            await list_voices()
        elif args.action == "stats":
            await show_voice_stats()
        elif args.action == "primary":
            await show_primary_voices()
        elif args.action == "test":
            if args.speaker:
                await test_voice(args.speaker)
            else:
                await test_voice_service()
        elif args.action == "language":
            await show_voices_by_language(args.lang)
        elif args.action == "activate":
            await activate_voice(args.speaker)
        elif args.action == "deactivate":
            await deactivate_voice(args.speaker)
        else:
            print(f"❌ Unbekannte Aktion: {args.action}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️ Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 