#!/usr/bin/env python3

"""
RadioX X API Setup Guide
Schritt-für-Schritt Anleitung zur Einrichtung der X (Twitter) API
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

def print_header(title: str):
    """Druckt einen formatierten Header"""
    print("\n" + "=" * 80)
    print(f"🐦 {title}")
    print("=" * 80)

def print_step(step: int, title: str):
    """Druckt einen Schritt"""
    print(f"\n📋 SCHRITT {step}: {title}")
    print("-" * 60)

def print_success(message: str):
    """Druckt eine Erfolgsmeldung"""
    print(f"✅ {message}")

def print_error(message: str):
    """Druckt eine Fehlermeldung"""
    print(f"❌ {message}")

def print_info(message: str):
    """Druckt eine Info"""
    print(f"ℹ️  {message}")

def setup_x_api_guide():
    """Zeigt die Anleitung zur X API Einrichtung"""
    
    print_header("X (TWITTER) API EINRICHTUNG")
    
    print_step(1, "X Developer Account erstellen")
    print("1. Gehe zu: https://developer.twitter.com/")
    print("2. Klicke auf 'Apply for a developer account'")
    print("3. Logge dich mit deinem Twitter Account ein")
    print("4. Wähle 'Hobbyist' oder 'Professional' je nach Verwendung")
    print("5. Beschreibe dein Projekt (RadioX - AI Radio System)")
    print("6. Bestätige deine E-Mail Adresse")
    
    print_step(2, "Neues Projekt erstellen")
    print("1. Gehe zu: https://developer.twitter.com/en/portal/dashboard")
    print("2. Klicke auf '+ Create Project'")
    print("3. Projektname: 'RadioX'")
    print("4. Use case: 'Making a bot' oder 'Exploring the API'")
    print("5. Beschreibung: 'AI-powered radio system with news aggregation'")
    
    print_step(3, "App erstellen und Keys generieren")
    print("1. Erstelle eine neue App in deinem Projekt")
    print("2. App Name: 'RadioX-Backend'")
    print("3. Gehe zu 'Keys and tokens'")
    print("4. Generiere einen 'Bearer Token'")
    print("5. WICHTIG: Kopiere den Bearer Token sofort!")
    
    print_step(4, "API Permissions konfigurieren")
    print("1. Gehe zu 'App settings' > 'User authentication settings'")
    print("2. App permissions: 'Read' (wir lesen nur Tweets)")
    print("3. Type of App: 'Web App'")
    print("4. Callback URLs: http://localhost:8000/callback")
    print("5. Website URL: http://localhost:8000")
    
    print_step(5, "Bearer Token in .env konfigurieren")
    print("1. Kopiere env_example.txt zu .env")
    print("2. Füge deinen Bearer Token ein:")
    print("   X_BEARER_TOKEN=dein_echter_bearer_token_hier")
    print("3. Speichere die .env Datei")
    
    print("\n🎯 WICHTIGE HINWEISE:")
    print("• Der Bearer Token ist GEHEIM - teile ihn niemals!")
    print("• Free Tier: 500,000 Tweets/Monat (mehr als genug für RadioX)")
    print("• API v2 wird verwendet (neueste Version)")
    print("• Nur Read-Permissions benötigt")
    
    print("\n🔗 NÜTZLICHE LINKS:")
    print("• Developer Portal: https://developer.twitter.com/en/portal/dashboard")
    print("• API Dokumentation: https://developer.twitter.com/en/docs/twitter-api")
    print("• Rate Limits: https://developer.twitter.com/en/docs/twitter-api/rate-limits")

async def test_x_api_connection():
    """Testet die X API Verbindung"""
    
    print_header("X API VERBINDUNG TESTEN")
    
    # .env Datei prüfen
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env Datei nicht gefunden!")
        print_info("Kopiere env_example.txt zu .env und fülle deine API Keys ein")
        return False
    
    # Environment laden
    from dotenv import load_dotenv
    load_dotenv()
    
    bearer_token = os.getenv('X_BEARER_TOKEN')
    
    if not bearer_token or bearer_token == 'your_x_bearer_token_here':
        print_error("X_BEARER_TOKEN nicht konfiguriert!")
        print_info("Füge deinen echten Bearer Token in die .env Datei ein")
        return False
    
    print_success("Bearer Token gefunden")
    print_info(f"Token: {bearer_token[:20]}...{bearer_token[-10:]}")
    
    # X API Service testen
    try:
        from src.services.x_api_service import XAPIService
        
        print("\n🔄 Teste X API Verbindung...")
        service = XAPIService(bearer_token)
        
        # Test mit einem bekannten Account
        print("📱 Teste mit @elonmusk Account...")
        tweets = await service.get_user_tweets("elonmusk", max_results=5, since_minutes=1440)  # 24h
        
        if tweets:
            print_success(f"{len(tweets)} Tweets erfolgreich geladen!")
            
            print("\n📊 TWEET BEISPIELE:")
            for i, tweet in enumerate(tweets[:3], 1):
                print(f"{i}. {tweet.text[:80]}...")
                print(f"   ❤️ {tweet.like_count} Likes | 🔄 {tweet.retweet_count} RTs")
                print(f"   📅 {tweet.created_at.strftime('%Y-%m-%d %H:%M')}")
                print()
            
            return True
        else:
            print_error("Keine Tweets gefunden (möglicherweise keine neuen Tweets)")
            print_info("Das ist normal - versuche es mit einem anderen Account oder größerem Zeitfenster")
            return True
            
    except Exception as e:
        print_error(f"X API Fehler: {e}")
        
        if "401" in str(e):
            print_info("401 Unauthorized - Bearer Token ungültig oder abgelaufen")
        elif "403" in str(e):
            print_info("403 Forbidden - App Permissions prüfen")
        elif "429" in str(e):
            print_info("429 Rate Limit - Zu viele Anfragen, warte ein paar Minuten")
        else:
            print_info("Prüfe deine Internetverbindung und API Konfiguration")
        
        return False

async def test_bitcoin_og_accounts():
    """Testet alle Bitcoin OG Accounts"""
    
    print_header("BITCOIN OG ACCOUNTS TESTEN")
    
    from src.services.x_api_service import XAPIService
    
    service = XAPIService()
    
    print("🚀 Teste alle Bitcoin OG Accounts...")
    
    # Alle Accounts testen
    results = await service.get_bitcoin_og_tweets(since_minutes=1440, max_per_account=2)  # 24h
    
    if results:
        print_success(f"{len(results)} Tweets von Bitcoin OGs gesammelt!")
        
        # Nach Account gruppieren
        by_account = {}
        for tweet in results:
            username = tweet.author_username
            if username not in by_account:
                by_account[username] = []
            by_account[username].append(tweet)
        
        print(f"\n📊 ERGEBNISSE PRO ACCOUNT:")
        for username, tweets in by_account.items():
            print(f"   @{username}: {len(tweets)} Tweets")
            for tweet in tweets:
                print(f"      💬 {tweet.text[:60]}...")
                print(f"      ❤️ {tweet.like_count} Likes | 🔥 Priorität: {tweet.priority}/10")
        
        return True
    else:
        print_error("Keine Bitcoin OG Tweets gefunden")
        return False

def create_env_file():
    """Erstellt .env Datei aus Template"""
    
    print_header(".ENV DATEI ERSTELLEN")
    
    env_path = Path(".env")
    example_path = Path("env_example.txt")
    
    if env_path.exists():
        print_info(".env Datei existiert bereits")
        return
    
    if not example_path.exists():
        print_error("env_example.txt nicht gefunden!")
        return
    
    # Kopiere Template
    with open(example_path, 'r') as f:
        content = f.read()
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print_success(".env Datei erstellt!")
    print_info("Bearbeite die .env Datei und füge deine API Keys ein")

async def main():
    """Hauptfunktion"""
    
    print("🎙️ RADIOX X API SETUP")
    print("=" * 80)
    print("Dieses Skript hilft dir bei der Einrichtung der X (Twitter) API")
    print("=" * 80)
    
    while True:
        print("\n🔧 WAS MÖCHTEST DU TUN?")
        print("1. 📖 Anleitung zur X API Einrichtung anzeigen")
        print("2. 📄 .env Datei erstellen")
        print("3. 🧪 X API Verbindung testen")
        print("4. 🐦 Bitcoin OG Accounts testen")
        print("5. 🚪 Beenden")
        
        choice = input("\nWähle eine Option (1-5): ").strip()
        
        if choice == "1":
            setup_x_api_guide()
        elif choice == "2":
            create_env_file()
        elif choice == "3":
            success = await test_x_api_connection()
            if success:
                print_success("X API ist korrekt konfiguriert! 🎉")
        elif choice == "4":
            success = await test_bitcoin_og_accounts()
            if success:
                print_success("Bitcoin OG Accounts funktionieren! 🚀")
        elif choice == "5":
            print("\n👋 Auf Wiedersehen!")
            break
        else:
            print_error("Ungültige Auswahl. Bitte wähle 1-5.")
        
        input("\nDrücke Enter um fortzufahren...")

if __name__ == "__main__":
    asyncio.run(main()) 