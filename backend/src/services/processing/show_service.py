#!/usr/bin/env python3
"""
RadioX Show Service
===================

Service für RadioShow-Konfiguration und -Management:
- Lädt Show-Presets aus Supabase
- Verwaltet Sprecher-Konfigurationen (Marcel, Jarvis)
- Bereitet Show-Parameter für Generierung auf
- Unterstützt verschiedene Show-Typen (Zürich, Crypto, Tech, etc.)
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from loguru import logger
from dataclasses import dataclass

# Import database connection
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database.supabase_client import get_db


@dataclass
class ShowConfiguration:
    """Repräsentiert eine vollständige Show-Konfiguration"""
    
    # Basic Show Info
    preset_name: str
    display_name: str
    description: str
    city_focus: str
    
    # Speaker Configuration
    primary_speaker: str
    secondary_speaker: Optional[str] = None
    
    # Content Configuration
    rss_feed_filter: Dict[str, Any] = None
    news_categories: List[str] = None
    exclude_categories: List[str] = None
    min_priority: int = 5
    max_feeds_per_category: int = 10
    
    # Show Settings
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    show_behavior: Dict[str, Any] = None
    
    # Metadata
    preset_id: Optional[str] = None


class ShowService:
    """
    Service für RadioShow-Konfiguration und -Management
    
    Verwaltet Show-Presets, Sprecher-Konfigurationen und
    bereitet alle Parameter für die Show-Generierung auf.
    """
    
    def __init__(self):
        # Lazy loading - only initialize when needed
        self._db = None
        
        # Cache für Show-Konfigurationen
        self._show_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 Minuten Cache
        
        logger.info("🎭 Show Service initialisiert")
    
    @property
    def db(self):
        """Lazy loading of database connection"""
        if self._db is None:
            self._db = get_db()
        return self._db
    
    # ==================== SHOW PRESETS ====================
    
    async def get_all_show_presets(self, active_only: bool = True) -> List[ShowConfiguration]:
        """
        Lädt alle Show-Presets aus Supabase
        
        Args:
            active_only: Nur aktive Shows laden
            
        Returns:
            Liste aller Show-Konfigurationen
        """
        logger.info(f"🎭 Lade alle Show-Presets (active_only={active_only})...")
        
        try:
            # Query für Show-Presets
            query = self.db.client.table("show_presets").select("*")
            
            if active_only:
                query = query.eq("is_active", True)
            
            response = query.order("display_name").execute()
            
            if not response.data:
                logger.warning("⚠️ Keine Show-Presets gefunden")
                return []
            
            # Konvertiere zu ShowConfiguration Objekten
            show_configs = []
            for preset_data in response.data:
                config = self._convert_to_show_config(preset_data)
                show_configs.append(config)
            
            logger.info(f"✅ {len(show_configs)} Show-Presets geladen")
            return show_configs
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Show-Presets: {e}")
            return []
    
    async def get_show_preset(self, preset_name: str) -> Optional[ShowConfiguration]:
        """
        Lädt ein spezifisches Show-Preset
        
        Args:
            preset_name: Name des Presets (z.B. "zurich", "crypto")
            
        Returns:
            Show-Konfiguration oder None
        """
        logger.info(f"🎭 Lade Show-Preset: {preset_name}")
        
        try:
            response = self.db.client.table("show_presets").select("*").eq("preset_name", preset_name).execute()
            
            if not response.data:
                logger.warning(f"⚠️ Show-Preset '{preset_name}' nicht gefunden")
                return None
            
            preset_data = response.data[0]
            config = self._convert_to_show_config(preset_data)
            
            logger.info(f"✅ Show-Preset '{preset_name}' geladen: {config.display_name}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden des Show-Presets '{preset_name}': {e}")
            return None
    
    async def get_available_show_types(self) -> List[Dict[str, str]]:
        """
        Gibt verfügbare Show-Typen zurück
        
        Returns:
            Liste mit Show-Typen und Beschreibungen
        """
        logger.info("🎭 Lade verfügbare Show-Typen...")
        
        try:
            response = self.db.client.table("show_presets").select("preset_name, display_name, description, city_focus, primary_speaker").eq("is_active", True).order("display_name").execute()
            
            show_types = []
            for preset in response.data:
                show_types.append({
                    "preset_name": preset["preset_name"],
                    "display_name": preset["display_name"],
                    "description": preset["description"],
                    "city_focus": preset["city_focus"],
                    "primary_speaker": preset["primary_speaker"]
                })
            
            logger.info(f"✅ {len(show_types)} Show-Typen verfügbar")
            return show_types
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Show-Typen: {e}")
            return []
    
    # ==================== SPRECHER-KONFIGURATION ====================
    
    async def get_speaker_configuration(self, speaker_name: str) -> Optional[Dict[str, Any]]:
        """
        Lädt Sprecher-Konfiguration aus voice_configurations
        
        Args:
            speaker_name: Name des Sprechers (marcel, jarvis)
            
        Returns:
            Voice-Konfiguration oder None
        """
        logger.info(f"🎤 Lade Sprecher-Konfiguration: {speaker_name}")
        
        try:
            response = self.db.client.table("voice_configurations").select("*").eq("speaker_name", speaker_name).eq("is_active", True).execute()
            
            if not response.data:
                logger.warning(f"⚠️ Sprecher '{speaker_name}' nicht gefunden")
                return None
            
            voice_config = response.data[0]
            
            # Bereite Konfiguration für ElevenLabs auf
            speaker_config = {
                "speaker_name": voice_config["speaker_name"],
                "voice_id": voice_config["voice_id"],
                "voice_name": voice_config["voice_name"],
                "language": voice_config["language"],
                "settings": {
                    "stability": float(voice_config["stability"]),
                    "similarity_boost": float(voice_config["similarity_boost"]),
                    "style": float(voice_config["style"]),
                    "use_speaker_boost": voice_config["use_speaker_boost"]
                },
                "model": voice_config["model"],
                "description": voice_config.get("description", ""),
                "is_primary": voice_config.get("is_primary", False)
            }
            
            logger.info(f"✅ Sprecher-Konfiguration geladen: {speaker_config['voice_name']}")
            return speaker_config
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Sprecher-Konfiguration '{speaker_name}': {e}")
            return None
    
    async def get_all_speakers(self) -> List[Dict[str, Any]]:
        """
        Lädt alle verfügbaren Sprecher
        
        Returns:
            Liste aller Sprecher-Konfigurationen
        """
        logger.info("🎤 Lade alle Sprecher...")
        
        try:
            response = self.db.client.table("voice_configurations").select("*").eq("is_active", True).order("speaker_name").execute()
            
            speakers = []
            for voice_data in response.data:
                speaker_config = {
                    "speaker_name": voice_data["speaker_name"],
                    "voice_name": voice_data["voice_name"],
                    "language": voice_data["language"],
                    "description": voice_data.get("description", ""),
                    "is_primary": voice_data.get("is_primary", False)
                }
                speakers.append(speaker_config)
            
            logger.info(f"✅ {len(speakers)} Sprecher geladen")
            return speakers
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Sprecher: {e}")
            return []
    
    # ==================== SHOW-GENERIERUNG VORBEREITUNG ====================
    
    async def prepare_show_generation(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Bereitet alle Parameter für Show-Generierung vor
        
        Args:
            preset_name: Name des Show-Presets
            
        Returns:
            Vollständige Show-Konfiguration für Generierung
        """
        logger.info(f"🎬 Bereite Show-Generierung vor: {preset_name}")
        
        try:
            # 1. Lade Show-Preset
            show_config = await self.get_show_preset(preset_name)
            if not show_config:
                logger.error(f"❌ Show-Preset '{preset_name}' nicht gefunden")
                return None
            
            # 2. Lade Sprecher-Konfiguration
            speaker_config = await self.get_speaker_configuration(show_config.primary_speaker)
            if not speaker_config:
                logger.error(f"❌ Sprecher '{show_config.primary_speaker}' nicht gefunden")
                return None
            
            # 3. Bereite RSS-Filter vor
            rss_filter = show_config.rss_feed_filter or {}
            
            # 4. Erstelle vollständige Generierungs-Konfiguration
            generation_config = {
                # Show Information
                "show": {
                    "preset_name": show_config.preset_name,
                    "display_name": show_config.display_name,
                    "description": show_config.description,
                    "city_focus": show_config.city_focus,
                    "show_behavior": getattr(show_config, 'show_behavior', {})
                },
                
                # Speaker Configuration
                "speaker": speaker_config,
                
                # Content Configuration
                "content": {
                    "rss_filter": rss_filter,
                    "categories": rss_filter.get("categories", []),
                    "exclude_categories": rss_filter.get("exclude_categories", []),
                    "min_priority": rss_filter.get("min_priority", 5),
                    "max_feeds_per_category": rss_filter.get("max_feeds_per_category", 10)
                },
                
                # Generation Settings
                "settings": {
                    "language": speaker_config["language"],
                    "voice_model": speaker_config["model"],
                    "generation_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            logger.info(f"✅ Show-Generierung vorbereitet für '{show_config.display_name}'")
            logger.info(f"   🎤 Sprecher: {speaker_config['voice_name']} ({speaker_config['language']})")
            logger.info(f"   🏙️ Stadt-Fokus: {show_config.city_focus}")
            logger.info(f"   📰 Kategorien: {', '.join(rss_filter.get('categories', []))}")
            
            return generation_config
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Show-Generierung Vorbereitung: {e}")
            return None
    
    # ==================== HILFSMETHODEN ====================
    
    def _convert_to_show_config(self, preset_data: Dict[str, Any]) -> ShowConfiguration:
        """Konvertiert Supabase-Daten zu ShowConfiguration"""
        
        rss_filter = preset_data.get("rss_feed_filter", {})
        
        return ShowConfiguration(
            preset_id=preset_data.get("id"),
            preset_name=preset_data["preset_name"],
            display_name=preset_data["display_name"],
            description=preset_data.get("description", ""),
            city_focus=preset_data.get("city_focus", "Global"),
            primary_speaker=preset_data["primary_speaker"],
            secondary_speaker=preset_data.get("secondary_speaker"),
            rss_feed_filter=rss_filter,
            news_categories=rss_filter.get("categories", []),
            exclude_categories=rss_filter.get("exclude_categories", []),
            min_priority=rss_filter.get("min_priority", 5),
            max_feeds_per_category=rss_filter.get("max_feeds_per_category", 10),
            is_active=preset_data.get("is_active", True),
            created_at=preset_data.get("created_at"),
            updated_at=preset_data.get("updated_at"),
            show_behavior=preset_data.get("show_behavior", {})
        )
    
    # ==================== SHOW-STATISTIKEN ====================
    
    async def get_show_statistics(self) -> Dict[str, Any]:
        """
        Gibt Show-Statistiken zurück
        
        Returns:
            Statistiken über verfügbare Shows
        """
        logger.info("📊 Lade Show-Statistiken...")
        
        try:
            # Lade alle Show-Presets
            all_shows = await self.get_all_show_presets(active_only=False)
            active_shows = [s for s in all_shows if s.is_active]
            
            # Lade alle Sprecher
            all_speakers = await self.get_all_speakers()
            
            # Gruppiere Shows nach Stadt-Fokus
            city_groups = {}
            speaker_groups = {}
            
            for show in active_shows:
                # Nach Stadt gruppieren
                city = show.city_focus
                if city not in city_groups:
                    city_groups[city] = []
                city_groups[city].append(show.preset_name)
                
                # Nach Sprecher gruppieren
                speaker = show.primary_speaker
                if speaker not in speaker_groups:
                    speaker_groups[speaker] = []
                speaker_groups[speaker].append(show.preset_name)
            
            statistics = {
                "total_shows": len(all_shows),
                "active_shows": len(active_shows),
                "inactive_shows": len(all_shows) - len(active_shows),
                "total_speakers": len(all_speakers),
                "city_distribution": city_groups,
                "speaker_distribution": speaker_groups,
                "available_speakers": [s["speaker_name"] for s in all_speakers],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Show-Statistiken geladen: {statistics['active_shows']} aktive Shows")
            return statistics
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Show-Statistiken: {e}")
            return {}


# ==================== CONVENIENCE FUNCTIONS ====================

async def get_show_service() -> ShowService:
    """Factory function für Show Service"""
    return ShowService()


async def get_show_for_generation(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function für Show-Generierung
    
    Args:
        preset_name: Name des Show-Presets
        
    Returns:
        Vollständige Show-Konfiguration
    """
    service = await get_show_service()
    return await service.prepare_show_generation(preset_name)


# ==================== TESTING ====================

async def test_show_service():
    """Test-Funktion für Show Service"""
    
    print("🧪 TESTE SHOW SERVICE")
    print("=" * 50)
    
    service = ShowService()
    
    # Test 1: Alle Show-Presets laden
    print("\n📋 TESTE: Alle Show-Presets laden")
    shows = await service.get_all_show_presets()
    print(f"✅ {len(shows)} Shows geladen")
    
    for show in shows:
        print(f"   🎭 {show.preset_name}: {show.display_name} ({show.primary_speaker})")
    
    # Test 2: Spezifisches Preset laden
    print("\n🎯 TESTE: Zürich Show-Preset laden")
    zurich_show = await service.get_show_preset("zurich")
    if zurich_show:
        print(f"✅ Zürich Show geladen: {zurich_show.display_name}")
        print(f"   🎤 Sprecher: {zurich_show.primary_speaker}")
        print(f"   🏙️ Stadt: {zurich_show.city_focus}")
        print(f"   📰 Kategorien: {', '.join(zurich_show.news_categories)}")
    
    # Test 3: Sprecher-Konfiguration laden
    print("\n🎤 TESTE: Sprecher-Konfiguration laden")
    marcel_config = await service.get_speaker_configuration("marcel")
    if marcel_config:
        print(f"✅ Marcel Konfiguration geladen: {marcel_config['voice_name']}")
        print(f"   🗣️ Voice ID: {marcel_config['voice_id']}")
        print(f"   🌍 Sprache: {marcel_config['language']}")
    
    # Test 4: Show-Generierung vorbereiten
    print("\n🎬 TESTE: Show-Generierung vorbereiten")
    generation_config = await service.prepare_show_generation("zurich")
    if generation_config:
        print(f"✅ Generierungs-Konfiguration erstellt")
        print(f"   🎭 Show: {generation_config['show']['display_name']}")
        print(f"   🎤 Sprecher: {generation_config['speaker']['voice_name']}")
        print(f"   📰 RSS-Filter: {len(generation_config['content']['categories'])} Kategorien")
    
    # Test 5: Show-Statistiken
    print("\n📊 TESTE: Show-Statistiken")
    stats = await service.get_show_statistics()
    if stats:
        print(f"✅ Statistiken geladen:")
        print(f"   📊 Aktive Shows: {stats['active_shows']}")
        print(f"   🎤 Sprecher: {stats['total_speakers']}")
        print(f"   🏙️ Städte: {', '.join(stats['city_distribution'].keys())}")
    
    print("\n🎉 SHOW SERVICE TESTS ABGESCHLOSSEN!")


if __name__ == "__main__":
    asyncio.run(test_show_service()) 