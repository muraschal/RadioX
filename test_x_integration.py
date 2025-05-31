#!/usr/bin/env python3
"""
Test-Script für X-API Integration in RadioX
Testet die Verbindung und holt Tweets von VIP-Accounts
"""

import os
from dotenv import load_dotenv
from loguru import logger
from src.content.x_feed import XFeedManager, test_x_feed_integration
from src.content.x_feed_config import VIP_ACCOUNTS

def test_x_api_connection():
    """Testet die X-API Verbindung."""
    print("🐦 RadioX X-Integration Test")
    print("=" * 50)
    
    # Lade Umgebungsvariablen
    load_dotenv()
    
    # Prüfe API-Keys
    print("\n🔑 API-Key Status:")
    
    x_client_id = os.getenv("X_CLIENT_ID")
    x_client_secret = os.getenv("X_CLIENT_SECRET")
    x_bearer_token = os.getenv("X_BEARER_TOKEN")
    
    print(f"   X_CLIENT_ID: {'✅ Gesetzt' if x_client_id else '❌ Fehlt'}")
    print(f"   X_CLIENT_SECRET: {'✅ Gesetzt' if x_client_secret else '❌ Fehlt'}")
    print(f"   X_BEARER_TOKEN: {'✅ Gesetzt' if x_bearer_token else '❌ Fehlt'}")
    
    if x_client_id:
        print(f"   Client ID: {x_client_id[:10]}...")
    if x_bearer_token:
        print(f"   Bearer Token: {x_bearer_token[:10]}...")
    
    # Zeige VIP-Accounts
    print(f"\n👑 VIP-Accounts ({len(VIP_ACCOUNTS)}):")
    for username, account in VIP_ACCOUNTS.items():
        print(f"   - @{username}: {account.display_name} ({account.category})")
        print(f"     Priority: {account.priority}, Keywords: {len(account.keywords)}")
    
    # Teste X-Feed Manager
    print("\n🚀 Teste X-Feed Manager...")
    
    try:
        manager = XFeedManager()
        
        if not manager.enabled:
            print("❌ X-Feed Manager nicht aktiviert")
            print("   Mögliche Ursachen:")
            print("   - Bearer Token fehlt oder ungültig")
            print("   - tweepy nicht installiert")
            print("   - API-Limits erreicht")
            return False
        
        print("✅ X-Feed Manager erfolgreich initialisiert!")
        
        # Test: Hole VIP-Tweets
        print("\n📋 Hole aktuelle Tweets...")
        tweets = manager.get_vip_tweets(count=3, hours_back=48)
        
        if tweets:
            print(f"✅ {len(tweets)} relevante Tweets gefunden!")
            
            for i, tweet in enumerate(tweets, 1):
                print(f"\n📝 Tweet #{i}:")
                print(f"   Account: @{tweet.username} ({tweet.display_name})")
                print(f"   Content: {tweet.content[:100]}...")
                print(f"   Engagement: {tweet.engagement_score}")
                print(f"   Relevanz: {tweet.relevance_score:.2f}")
                print(f"   Kategorie: {tweet.category}")
                print(f"   URL: {tweet.original_url}")
            
            # Test: Radio-Segment generieren
            print("\n🎙️ Generiere Radio-Segment...")
            segment = manager.generate_radio_segment(tweets, "maximalist")
            print(f"✅ Radio-Segment generiert:")
            print(f"   {segment[:200]}...")
            
            return True
            
        else:
            print("⚠️ Keine Tweets gefunden")
            print("   Mögliche Ursachen:")
            print("   - Accounts haben in den letzten 48h nicht getweetet")
            print("   - Tweets erfüllen nicht die Relevanz-Kriterien")
            print("   - API-Rate-Limits")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        return False

def test_specific_account(username: str = "saylor"):
    """Testet einen spezifischen Account."""
    print(f"\n🎯 Teste spezifischen Account: @{username}")
    
    try:
        manager = XFeedManager()
        
        if not manager.enabled:
            print("❌ X-Feed Manager nicht verfügbar")
            return False
        
        # Hole User-Info
        user = manager.client.get_user(username=username)
        if user.data:
            print(f"✅ User gefunden: {user.data.name}")
            print(f"   Followers: {user.data.public_metrics['followers_count']:,}")
            print(f"   Following: {user.data.public_metrics['following_count']:,}")
            print(f"   Tweets: {user.data.public_metrics['tweet_count']:,}")
        
        # Hole neueste Tweets
        tweets = manager.client.get_users_tweets(
            id=user.data.id,
            max_results=5,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if tweets.data:
            print(f"✅ {len(tweets.data)} neueste Tweets:")
            for tweet in tweets.data:
                print(f"   - {tweet.text[:80]}...")
                print(f"     Likes: {tweet.public_metrics['like_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Account-Test: {e}")
        return False

def main():
    """Hauptfunktion für X-Integration Test."""
    success = test_x_api_connection()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 X-Integration erfolgreich!")
        print("✅ RadioX kann jetzt Tweets von VIP-Accounts abrufen")
        print("✅ Radio-Segmente können generiert werden")
        print("✅ Bereit für Live-Radio mit Bitcoin-Alpha!")
        
        # Optional: Teste spezifischen Account
        test_specific_account("saylor")
        
    else:
        print("\n" + "=" * 50)
        print("❌ X-Integration fehlgeschlagen")
        print("🔧 Prüfen Sie:")
        print("   - .env-Datei mit korrekten API-Keys")
        print("   - Bearer Token generiert")
        print("   - Internet-Verbindung")
        print("   - X-API Status")

if __name__ == "__main__":
    main() 