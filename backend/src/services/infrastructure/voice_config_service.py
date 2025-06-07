#!/usr/bin/env python3
"""
Voice Configuration Service
===========================

Lädt Voice-Konfigurationen aus Supabase statt hardcoded Definitionen.
Ersetzt die hardcoded voice_config im AudioGenerationService.
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import sys
from pathlib import Path

# Add database path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.supabase_client import get_db


class VoiceConfigService:
    """Service für Voice-Konfigurationen aus Supabase"""
    
    def __init__(self):
        db_wrapper = get_db()
        self.db = db_wrapper.client  # Direkter Zugriff auf den Supabase Client
        self._voice_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self._cache_timestamp: Optional[float] = None
        self.cache_duration = 300  # 5 Minuten Cache
    
    async def get_voice_config(self, speaker_name: str) -> Optional[Dict[str, Any]]:
        """
        Holt Voice-Konfiguration für einen Speaker
        
        Args:
            speaker_name: Name des Speakers (marcel, jarvis, etc.)
            
        Returns:
            Voice-Konfiguration oder None wenn nicht gefunden
        """
        
        try:
            # Lade alle Voices (mit Cache)
            all_voices = await self.get_all_voice_configs()
            
            # Suche spezifischen Speaker
            voice_config = all_voices.get(speaker_name)
            
            if not voice_config:
                logger.warning(f"⚠️ Voice-Konfiguration für '{speaker_name}' nicht gefunden")
                return None
            
            return voice_config
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Voice-Konfiguration für '{speaker_name}': {e}")
            return None
    
    async def get_all_voice_configs(self, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Holt alle aktiven Voice-Konfigurationen aus Supabase
        
        Args:
            force_refresh: Cache ignorieren und neu laden
            
        Returns:
            Dictionary mit speaker_name als Key und Voice-Config als Value
        """
        
        import time
        
        # Cache prüfen
        if not force_refresh and self._voice_cache and self._cache_timestamp:
            if time.time() - self._cache_timestamp < self.cache_duration:
                return self._voice_cache
        
        try:
            logger.info("🎤 Lade Voice-Konfigurationen...")
            
            # Hole alle aktiven Voices
            result = self.db.table("voice_configurations").select("*").eq("is_active", True).execute()
            
            if not result.data:
                logger.warning("⚠️ Keine aktiven Voice-Konfigurationen gefunden")
                return {}
            
            # Konvertiere zu Dictionary
            voice_configs = {}
            for voice in result.data:
                voice_configs[voice["speaker_name"]] = {
                    "voice_id": voice["voice_id"],
                    "voice_name": voice["voice_name"],
                    "language": voice["language"],
                    "stability": float(voice["stability"]),
                    "similarity_boost": float(voice["similarity_boost"]),
                    "style": float(voice["style"]),
                    "use_speaker_boost": voice["use_speaker_boost"],
                    "model": voice["model"],
                    "description": voice["description"],
                    "is_primary": voice["is_primary"]
                }
            
            # Cache aktualisieren
            self._voice_cache = voice_configs
            self._cache_timestamp = time.time()
            
            logger.info(f"✅ {len(voice_configs)} Voice-Konfigurationen geladen")
            return voice_configs
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Voice-Konfigurationen: {e}")
            
            # Fallback: Leere Konfiguration
            return {}
    
    async def get_primary_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        Holt nur die Primary Voice-Konfigurationen
        
        Returns:
            Dictionary mit Primary Voices
        """
        
        try:
            all_voices = await self.get_all_voice_configs()
            
            # Filtere nur Primary Voices
            primary_voices = {
                speaker: config for speaker, config in all_voices.items()
                if config.get("is_primary", False)
            }
            
            logger.info(f"✅ {len(primary_voices)} Primary Voice-Konfigurationen gefunden")
            return primary_voices
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Primary Voices: {e}")
            return {}
    
    async def get_voices_by_language(self, language: str = "en") -> Dict[str, Dict[str, Any]]:
        """
        Holt Voice-Konfigurationen für eine bestimmte Sprache
        
        Args:
            language: Sprach-Code (en, de, etc.)
            
        Returns:
            Dictionary mit Voices für die Sprache
        """
        
        try:
            all_voices = await self.get_all_voice_configs()
            
            # Filtere nach Sprache
            language_voices = {
                speaker: config for speaker, config in all_voices.items()
                if config.get("language", "en") == language
            }
            
            logger.info(f"✅ {len(language_voices)} Voice-Konfigurationen für Sprache '{language}' gefunden")
            return language_voices
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Voices für Sprache '{language}': {e}")
            return {}
    
    async def add_voice_config(self, voice_config: Dict[str, Any]) -> bool:
        """
        Fügt eine neue Voice-Konfiguration hinzu
        
        Args:
            voice_config: Voice-Konfiguration mit allen erforderlichen Feldern
            
        Returns:
            True wenn erfolgreich hinzugefügt
        """
        
        try:
            logger.info(f"🎤 Füge Voice-Konfiguration hinzu: {voice_config.get('speaker_name')}")
            
            # Validiere erforderliche Felder
            required_fields = ["speaker_name", "voice_id", "voice_name"]
            for field in required_fields:
                if field not in voice_config:
                    raise ValueError(f"Erforderliches Feld '{field}' fehlt")
            
            # Füge Voice hinzu
            result = self.db.table("voice_configurations").insert(voice_config).execute()
            
            if result.data:
                logger.info(f"✅ Voice-Konfiguration '{voice_config['speaker_name']}' hinzugefügt")
                
                # Cache invalidieren
                self._voice_cache = None
                self._cache_timestamp = None
                
                return True
            else:
                logger.error("❌ Fehler beim Hinzufügen der Voice-Konfiguration")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Hinzufügen der Voice-Konfiguration: {e}")
            return False
    
    async def update_voice_config(self, speaker_name: str, updates: Dict[str, Any]) -> bool:
        """
        Aktualisiert eine Voice-Konfiguration
        
        Args:
            speaker_name: Name des Speakers
            updates: Dictionary mit zu aktualisierenden Feldern
            
        Returns:
            True wenn erfolgreich aktualisiert
        """
        
        try:
            logger.info(f"🔧 Aktualisiere Voice-Konfiguration: {speaker_name}")
            
            # Füge updated_at hinzu
            updates["updated_at"] = "NOW()"
            
            # Aktualisiere Voice
            result = self.db.table("voice_configurations").update(updates).eq("speaker_name", speaker_name).execute()
            
            if result.data:
                logger.info(f"✅ Voice-Konfiguration '{speaker_name}' aktualisiert")
                
                # Cache invalidieren
                self._voice_cache = None
                self._cache_timestamp = None
                
                return True
            else:
                logger.error(f"❌ Voice-Konfiguration '{speaker_name}' nicht gefunden")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Aktualisieren der Voice-Konfiguration '{speaker_name}': {e}")
            return False
    
    async def deactivate_voice(self, speaker_name: str) -> bool:
        """
        Deaktiviert eine Voice-Konfiguration
        
        Args:
            speaker_name: Name des Speakers
            
        Returns:
            True wenn erfolgreich deaktiviert
        """
        
        return await self.update_voice_config(speaker_name, {"is_active": False})
    
    async def activate_voice(self, speaker_name: str) -> bool:
        """
        Aktiviert eine Voice-Konfiguration
        
        Args:
            speaker_name: Name des Speakers
            
        Returns:
            True wenn erfolgreich aktiviert
        """
        
        return await self.update_voice_config(speaker_name, {"is_active": True})
    
    async def get_voice_stats(self) -> Dict[str, Any]:
        """
        Holt Statistiken über Voice-Konfigurationen
        
        Returns:
            Dictionary mit Statistiken
        """
        
        try:
            # Hole alle Voices (auch inaktive)
            result = self.db.table("voice_configurations").select("*").execute()
            
            if not result.data:
                return {"total": 0, "active": 0, "primary": 0, "languages": []}
            
            voices = result.data
            
            # Berechne Statistiken
            total = len(voices)
            active = len([v for v in voices if v["is_active"]])
            primary = len([v for v in voices if v["is_primary"]])
            languages = list(set([v["language"] for v in voices]))
            
            # Gruppiere nach Sprache
            by_language = {}
            for voice in voices:
                lang = voice["language"]
                if lang not in by_language:
                    by_language[lang] = {"total": 0, "active": 0, "primary": 0}
                
                by_language[lang]["total"] += 1
                if voice["is_active"]:
                    by_language[lang]["active"] += 1
                if voice["is_primary"]:
                    by_language[lang]["primary"] += 1
            
            stats = {
                "total": total,
                "active": active,
                "primary": primary,
                "languages": languages,
                "by_language": by_language,
                "cache_status": "cached" if self._voice_cache else "not_cached"
            }
            
            logger.info(f"📊 Voice-Statistiken: {total} total, {active} aktiv, {primary} primary")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Voice-Statistiken: {e}")
            return {"error": str(e)}
    
    async def test_voice_service(self) -> bool:
        """
        Testet den Voice Configuration Service
        
        Returns:
            True wenn alle Tests erfolgreich
        """
        
        try:
            logger.info("🧪 Teste Voice Configuration Service...")
            
            # Test 1: Alle Voices laden
            all_voices = await self.get_all_voice_configs()
            if not all_voices:
                logger.error("❌ Test 1 fehlgeschlagen: Keine Voices geladen")
                return False
            logger.info(f"✅ Test 1: {len(all_voices)} Voices geladen")
            
            # Test 2: Primary Voices laden
            primary_voices = await self.get_primary_voices()
            if not primary_voices:
                logger.error("❌ Test 2 fehlgeschlagen: Keine Primary Voices gefunden")
                return False
            logger.info(f"✅ Test 2: {len(primary_voices)} Primary Voices gefunden")
            
            # Test 3: Spezifische Voice laden
            marcel_voice = await self.get_voice_config("marcel")
            if not marcel_voice:
                logger.error("❌ Test 3 fehlgeschlagen: Marcel Voice nicht gefunden")
                return False
            logger.info(f"✅ Test 3: Marcel Voice geladen: {marcel_voice['voice_name']}")
            
            # Test 4: Statistiken
            stats = await self.get_voice_stats()
            if "error" in stats:
                logger.error("❌ Test 4 fehlgeschlagen: Statistiken-Fehler")
                return False
            logger.info(f"✅ Test 4: Statistiken geladen: {stats['total']} Voices")
            
            logger.info("🎉 Alle Voice Configuration Service Tests erfolgreich!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Voice Configuration Service Test fehlgeschlagen: {e}")
            return False


# Singleton Instance für einfache Verwendung
_voice_config_service = None

def get_voice_config_service() -> VoiceConfigService:
    """Holt die Singleton-Instanz des Voice Configuration Service"""
    global _voice_config_service
    if _voice_config_service is None:
        _voice_config_service = VoiceConfigService()
    return _voice_config_service


async def main():
    """Test-Funktion"""
    
    print("🎤 VOICE CONFIGURATION SERVICE TEST")
    print("=" * 50)
    
    service = get_voice_config_service()
    success = await service.test_voice_service()
    
    if success:
        print("\n🎉 Voice Configuration Service funktioniert perfekt!")
        
        # Zeige Statistiken
        stats = await service.get_voice_stats()
        print(f"\n📊 STATISTIKEN:")
        print(f"   Total Voices: {stats['total']}")
        print(f"   Aktive Voices: {stats['active']}")
        print(f"   Primary Voices: {stats['primary']}")
        print(f"   Sprachen: {', '.join(stats['languages'])}")
    else:
        print("❌ Voice Configuration Service Test fehlgeschlagen!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 