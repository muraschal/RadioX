#!/usr/bin/env python3
"""
Schneller Test für tweepy Import
"""

print("🔍 Teste tweepy Import...")

try:
    import tweepy
    print("✅ tweepy importiert")
    print(f"   Version: {tweepy.__version__}")
    
    # Teste Client-Klasse
    client_class = tweepy.Client
    print("✅ tweepy.Client verfügbar")
    
    # Teste mit Bearer Token
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    bearer_token = os.getenv("X_BEARER_TOKEN")
    if bearer_token:
        print(f"✅ Bearer Token gefunden: {bearer_token[:10]}...")
        
        try:
            client = tweepy.Client(bearer_token=bearer_token)
            print("✅ Client erstellt")
            
            # Teste einfachen API-Call
            user = client.get_user(username="saylor")
            if user.data:
                print(f"✅ API-Test erfolgreich: {user.data.name}")
            else:
                print("⚠️ API-Test: Kein User gefunden")
                
        except Exception as e:
            print(f"❌ API-Test fehlgeschlagen: {e}")
    else:
        print("❌ Bearer Token nicht gefunden")
        
except ImportError as e:
    print(f"❌ tweepy Import fehlgeschlagen: {e}")
except Exception as e:
    print(f"❌ Unerwarteter Fehler: {e}")

print("\n🎯 Test abgeschlossen") 