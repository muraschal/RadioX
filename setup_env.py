#!/usr/bin/env python3
"""
RadioX Environment Setup & Validation
=====================================

Automatisches Setup und Validierung der .env Datei:
- Prüft ob .env existiert
- Validiert erforderliche Variablen
- Überschreibt leere/unvollständige .env mit .env.example
- Gibt hilfreiche Setup-Anweisungen
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EnvVariable:
    """Definition einer Environment-Variable"""
    name: str
    required: bool
    description: str
    category: str


class EnvSetupManager:
    """Manager für .env Setup und Validierung"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.env_file = self.root_dir / ".env"
        self.env_example_file = self.root_dir / ".env.example"
        
        # Alle Environment-Variablen basierend auf Settings-Klasse
        self.env_variables = [
            # DATABASE (REQUIRED)
            EnvVariable("SUPABASE_URL", True, "Supabase Projekt URL", "database"),
            EnvVariable("SUPABASE_ANON_KEY", True, "Supabase Anonymous Key", "database"),
            EnvVariable("SUPABASE_SERVICE_ROLE_KEY", False, "Supabase Service Role Key", "database"),
            
            # AI SERVICES (REQUIRED)
            EnvVariable("OPENAI_API_KEY", True, "OpenAI API Key für GPT-4 & DALL-E", "ai"),
            EnvVariable("ELEVENLABS_API_KEY", True, "ElevenLabs API Key für Text-to-Speech", "ai"),
            
            # VOICE CONFIG (OPTIONAL)
            EnvVariable("ELEVENLABS_MARCEL_VOICE_ID", False, "Marcel Voice ID", "voice"),
            EnvVariable("ELEVENLABS_JARVIS_VOICE_ID", False, "Jarvis Voice ID", "voice"),
            
            # DATA SOURCES (REQUIRED)
            EnvVariable("COINMARKETCAP_API_KEY", True, "CoinMarketCap API Key für Crypto-Daten", "data"),
            EnvVariable("WEATHER_API_KEY", True, "Weather API Key", "data"),
            
            # SOCIAL MEDIA (OPTIONAL)
            EnvVariable("TWITTER_BEARER_TOKEN", False, "Twitter Bearer Token", "social"),
            EnvVariable("TWITTER_API_KEY", False, "Twitter API Key", "social"),
            EnvVariable("TWITTER_API_SECRET", False, "Twitter API Secret", "social"),
            EnvVariable("TWITTER_ACCESS_TOKEN", False, "Twitter Access Token", "social"),
            EnvVariable("TWITTER_ACCESS_TOKEN_SECRET", False, "Twitter Access Token Secret", "social"),
            
            # X API (OPTIONAL)
            EnvVariable("X_CLIENT_ID", False, "X API Client ID", "social"),
            EnvVariable("X_CLIENT_SECRET", False, "X API Client Secret", "social"),
            EnvVariable("X_BEARER_TOKEN", False, "X API Bearer Token", "social"),
            EnvVariable("X_ACCESS_TOKEN", False, "X API Access Token", "social"),
            EnvVariable("X_ACCESS_TOKEN_SECRET", False, "X API Access Token Secret", "social"),
            
            # ADDITIONAL WEATHER (OPTIONAL)
            EnvVariable("SRF_WEATHER_API_KEY", False, "SRF Weather API Key", "weather"),
            
            # SPOTIFY (OPTIONAL)
            EnvVariable("SPOTIFY_CLIENT_ID", False, "Spotify Client ID", "music"),
            EnvVariable("SPOTIFY_CLIENT_SECRET", False, "Spotify Client Secret", "music"),
            EnvVariable("SPOTIFY_REDIRECT_URI", False, "Spotify Redirect URI", "music"),
            
            # SYSTEM
            EnvVariable("ENVIRONMENT", False, "Environment (development/production)", "system"),
            EnvVariable("LOG_LEVEL", False, "Log Level (INFO/DEBUG/WARNING)", "system"),
            EnvVariable("DEBUG", False, "Debug Mode (true/false)", "system"),
        ]
    
    def setup_env(self) -> Dict[str, any]:
        """
        Hauptfunktion für .env Setup
        
        Returns:
            Dict mit Setup-Ergebnis
        """
        
        print("🔧 RadioX Environment Setup")
        print("=" * 50)
        
        # 1. Prüfe ob .env.example existiert
        if not self.env_example_file.exists():
            return {
                "success": False,
                "error": "❌ .env.example nicht gefunden! Template fehlt.",
                "action": "Erstelle zuerst .env.example"
            }
        
        # 2. Prüfe aktuelle .env Situation
        env_status = self._analyze_env_file()
        
        print(f"📍 Aktuelle .env Status: {env_status['status']}")
        
        # 3. Entscheide über Action
        if env_status["action"] == "create":
            return self._create_env_from_example()
        elif env_status["action"] == "validate":
            return self._validate_and_report()
        elif env_status["action"] == "repair":
            return self._repair_env_file()
        else:
            return env_status
    
    def _analyze_env_file(self) -> Dict[str, any]:
        """Analysiert den Zustand der .env Datei"""
        
        if not self.env_file.exists():
            return {
                "status": "❌ .env Datei existiert nicht",
                "action": "create",
                "missing_required": len([v for v in self.env_variables if v.required])
            }
        
        # Lade existierende .env
        env_content = self._load_env_file()
        
        if not env_content:
            return {
                "status": "⚠️ .env Datei ist leer",
                "action": "create",
                "missing_required": len([v for v in self.env_variables if v.required])
            }
        
        # Prüfe erforderliche Variablen
        missing_required = []
        missing_optional = []
        
        for var in self.env_variables:
            if var.name not in env_content or not env_content[var.name].strip():
                if var.required:
                    missing_required.append(var)
                else:
                    missing_optional.append(var)
        
        if missing_required:
            return {
                "status": f"⚠️ {len(missing_required)} erforderliche Variable(n) fehlen",
                "action": "repair",
                "missing_required": missing_required,
                "missing_optional": missing_optional,
                "env_content": env_content
            }
        
        return {
            "status": f"✅ .env vollständig ({len(missing_optional)} optionale fehlen)",
            "action": "validate",
            "missing_required": [],
            "missing_optional": missing_optional,
            "env_content": env_content
        }
    
    def _load_env_file(self) -> Dict[str, str]:
        """Lädt die .env Datei und parst Variablen"""
        
        env_vars = {}
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️ Fehler beim Lesen der .env: {e}")
        
        return env_vars
    
    def _create_env_from_example(self) -> Dict[str, any]:
        """Erstellt .env aus .env.example"""
        
        print("📋 Erstelle .env aus .env.example...")
        
        try:
            shutil.copy2(self.env_example_file, self.env_file)
            
            print("✅ .env erfolgreich erstellt!")
            print("\n📝 NÄCHSTE SCHRITTE:")
            print("1. Öffne .env und trage deine API Keys ein")
            print("2. Minimale Anforderungen:")
            
            required_vars = [v for v in self.env_variables if v.required]
            for var in required_vars:
                print(f"   • {var.name}: {var.description}")
            
            print(f"\n3. Teste mit: cd backend && python cli_master.py status")
            
            return {
                "success": True,
                "action": "created",
                "message": ".env aus Template erstellt",
                "next_steps": "API Keys eintragen"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"❌ Fehler beim Erstellen der .env: {e}"
            }
    
    def _repair_env_file(self) -> Dict[str, any]:
        """Repariert unvollständige .env Datei"""
        
        print("🔧 Repariere unvollständige .env Datei...")
        
        # Backup erstellen
        backup_file = self.env_file.with_suffix('.env.backup')
        try:
            shutil.copy2(self.env_file, backup_file)
            print(f"💾 Backup erstellt: {backup_file}")
        except Exception as e:
            print(f"⚠️ Backup-Fehler: {e}")
        
        # Überschreibe mit Example
        try:
            shutil.copy2(self.env_example_file, self.env_file)
            
            print("✅ .env repariert!")
            print(f"💾 Original gesichert als: {backup_file}")
            print("\n📝 NÄCHSTE SCHRITTE:")
            print("1. Trage deine API Keys in .env ein")
            print("2. Übertrage ggf. Werte aus dem Backup")
            
            return {
                "success": True,
                "action": "repaired",
                "message": ".env repariert und Backup erstellt",
                "backup_file": str(backup_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"❌ Fehler beim Reparieren: {e}"
            }
    
    def _validate_and_report(self) -> Dict[str, any]:
        """Validiert vollständige .env und gibt Report"""
        
        env_content = self._load_env_file()
        
        print("✅ .env Validierung:")
        print("\n🔑 ERFORDERLICHE API KEYS:")
        
        all_good = True
        for var in self.env_variables:
            if var.required:
                value = env_content.get(var.name, "")
                if value and not value.startswith("your_"):
                    status = "✅"
                else:
                    status = "❌"
                    all_good = False
                
                print(f"   {status} {var.name}: {var.description}")
        
        print(f"\n📊 OPTIONALE KEYS:")
        optional_count = 0
        for var in self.env_variables:
            if not var.required:
                value = env_content.get(var.name, "")
                if value and not value.startswith("your_"):
                    optional_count += 1
        
        print(f"   ✅ {optional_count}/{len([v for v in self.env_variables if not v.required])} optionale Keys konfiguriert")
        
        if all_good:
            print(f"\n🎉 SETUP VOLLSTÄNDIG! System ist einsatzbereit.")
            print(f"🧪 Teste mit: cd backend && python cli_master.py status")
        else:
            print(f"\n⚠️ Erforderliche API Keys fehlen noch!")
            print(f"📝 Editiere .env und trage die fehlenden Werte ein.")
        
        return {
            "success": True,
            "action": "validated",
            "all_required_present": all_good,
            "optional_configured": optional_count
        }


def main():
    """Hauptfunktion"""
    
    try:
        manager = EnvSetupManager()
        result = manager.setup_env()
        
        if not result.get("success", False):
            print(f"\n❌ SETUP FEHLER:")
            print(f"   {result.get('error', 'Unbekannter Fehler')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n💥 UNERWARTETER FEHLER: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 