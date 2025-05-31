#!/usr/bin/env python3
"""
X-Feed Manager für RadioX
Integriert kuratierte X-Accounts in das Radio-System
"""

import os
import re
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger

# Verbesserte tweepy Import-Prüfung
TWEEPY_AVAILABLE = False
try:
    import tweepy
    # Teste ob tweepy wirklich funktioniert
    _ = tweepy.Client
    TWEEPY_AVAILABLE = True
    logger.info("✅ tweepy erfolgreich importiert")
except ImportError as e:
    logger.warning(f"tweepy nicht verfügbar: {e}")
    TWEEPY_AVAILABLE = False
except Exception as e:
    logger.warning(f"tweepy Import-Fehler: {e}")
    TWEEPY_AVAILABLE = False

from .x_feed_config import (
    VIP_ACCOUNTS, 
    CONTENT_CATEGORIES, 
    RELEVANCE_KEYWORDS,
    PERSONA_INTERPRETATIONS,
    TWEET_FILTER_CONFIG,
    get_account_by_username,
    get_high_priority_accounts,
    get_persona_intro
)

@dataclass
class ProcessedTweet:
    """Verarbeiteter Tweet für Radio-Integration."""
    username: str
    display_name: str
    content: str
    timestamp: datetime
    engagement_score: int
    relevance_score: float
    category: str
    radio_intro: str
    radio_outro: str
    original_url: str

class XFeedManager:
    """Manager für X-Feed Integration in RadioX."""
    
    def __init__(self, api_key: Optional[str] = None):
        if not TWEEPY_AVAILABLE:
            logger.warning("X-Integration nicht verfügbar - tweepy fehlt")
            self.enabled = False
            return
            
        # X API Credentials
        self.api_key = api_key or os.getenv("X_API_KEY") or os.getenv("X_CLIENT_ID")
        self.api_secret = os.getenv("X_API_SECRET") or os.getenv("X_CLIENT_SECRET")
        self.access_token = os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("X_BEARER_TOKEN")
        
        # Für OAuth 2.0 brauchen wir mindestens Bearer Token
        if not self.bearer_token:
            logger.warning("X API Bearer Token fehlt - X-Integration deaktiviert")
            self.enabled = False
            return
            
        try:
            # Initialisiere X API Client (OAuth 2.0)
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Teste die Verbindung
            try:
                # Einfacher Test: Hole eigene User-Info
                me = self.client.get_me()
                logger.info(f"✅ X-API Verbindung erfolgreich")
                self.enabled = True
            except Exception as test_error:
                logger.warning(f"X-API Test fehlgeschlagen: {test_error}")
                # Versuche trotzdem weiterzumachen (manche Endpoints funktionieren auch ohne User-Context)
                self.enabled = True
            
        except Exception as e:
            logger.error(f"X API Initialisierung fehlgeschlagen: {e}")
            self.enabled = False
    
    def get_vip_tweets(self, count: int = 10, hours_back: int = 24) -> List[ProcessedTweet]:
        """Holt aktuelle Tweets von VIP-Accounts."""
        if not self.enabled:
            logger.warning("X-Integration deaktiviert")
            return []
            
        all_tweets = []
        
        try:
            # Hole Tweets von jedem VIP-Account
            for username, account in VIP_ACCOUNTS.items():
                try:
                    logger.info(f"Hole Tweets von @{username}...")
                    
                    # Hole User-Tweets
                    user = self.client.get_user(username=username)
                    if not user.data:
                        logger.warning(f"User @{username} nicht gefunden")
                        continue
                    
                    tweets = self.client.get_users_tweets(
                        id=user.data.id,
                        max_results=10,
                        tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                        exclude=['replies', 'retweets'] if TWEET_FILTER_CONFIG['exclude_replies'] else None
                    )
                    
                    if not tweets.data:
                        logger.info(f"Keine Tweets von @{username} gefunden")
                        continue
                    
                    # Verarbeite Tweets
                    for tweet in tweets.data:
                        processed = self._process_tweet(tweet, account, username)
                        if processed and self._is_relevant_tweet(processed):
                            all_tweets.append(processed)
                            
                except Exception as e:
                    logger.error(f"Fehler beim Abrufen von @{username}: {e}")
                    continue
            
            # Sortiere nach Relevanz und Priorität
            all_tweets.sort(key=lambda t: (t.relevance_score, t.engagement_score), reverse=True)
            
            logger.info(f"✅ {len(all_tweets)} relevante Tweets gefunden")
            return all_tweets[:count]
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der VIP-Tweets: {e}")
            return []
    
    def _process_tweet(self, tweet: Any, account: Any, username: str) -> Optional[ProcessedTweet]:
        """Verarbeitet einen einzelnen Tweet."""
        try:
            # Berechne Engagement Score
            metrics = tweet.public_metrics
            engagement = (
                metrics['like_count'] * 1 +
                metrics['retweet_count'] * 2 +
                metrics['reply_count'] * 1.5 +
                metrics['quote_count'] * 3
            )
            
            # Berechne Relevanz Score
            relevance = self._calculate_relevance_score(tweet.text, account.keywords)
            
            # Erstelle Radio-Intro/Outro
            category_config = CONTENT_CATEGORIES.get(account.category, {})
            intro = category_config.get('intro_style', 'Update von {name}:').format(name=account.display_name)
            outro = category_config.get('outro_style', 'Das war {name}!').format(name=account.display_name)
            
            return ProcessedTweet(
                username=username,
                display_name=account.display_name,
                content=self._clean_tweet_text(tweet.text),
                timestamp=tweet.created_at,
                engagement_score=int(engagement),
                relevance_score=relevance,
                category=account.category,
                radio_intro=intro,
                radio_outro=outro,
                original_url=f"https://x.com/{username}/status/{tweet.id}"
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Tweet-Verarbeitung: {e}")
            return None
    
    def _calculate_relevance_score(self, text: str, account_keywords: List[str]) -> float:
        """Berechnet Relevanz-Score basierend auf Keywords."""
        text_lower = text.lower()
        score = 0.0
        
        # Account-spezifische Keywords (höchste Gewichtung)
        for keyword in account_keywords:
            if keyword.lower() in text_lower:
                score += 0.3
        
        # High-Priority Keywords
        for keyword in RELEVANCE_KEYWORDS['high_priority']:
            if keyword.lower() in text_lower:
                score += 0.2
        
        # Medium-Priority Keywords
        for keyword in RELEVANCE_KEYWORDS['medium_priority']:
            if keyword.lower() in text_lower:
                score += 0.1
        
        # Low-Priority Keywords (Abzug)
        for keyword in RELEVANCE_KEYWORDS['low_priority']:
            if keyword.lower() in text_lower:
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _clean_tweet_text(self, text: str) -> str:
        """Bereinigt Tweet-Text für Radio-Verwendung."""
        # Entferne URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Entferne @mentions (außer am Anfang)
        text = re.sub(r'(?<!^)@\w+', '', text)
        
        # Entferne übermäßige Whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Kürze auf Radio-taugliche Länge
        if len(text) > TWEET_FILTER_CONFIG['max_length']:
            text = text[:TWEET_FILTER_CONFIG['max_length']-3] + "..."
        
        return text
    
    def _is_relevant_tweet(self, tweet: ProcessedTweet) -> bool:
        """Prüft ob Tweet für Radio relevant ist."""
        # Mindest-Engagement
        if tweet.engagement_score < TWEET_FILTER_CONFIG['min_engagement']:
            return False
        
        # Mindest-Relevanz
        if tweet.relevance_score < 0.1:
            return False
        
        # Mindest-Länge
        if len(tweet.content) < TWEET_FILTER_CONFIG['min_length']:
            return False
        
        # Maximales Alter
        max_age = datetime.now() - timedelta(hours=TWEET_FILTER_CONFIG['max_age_hours'])
        if tweet.timestamp < max_age:
            return False
        
        return True
    
    def generate_radio_segment(self, tweets: List[ProcessedTweet], persona: str = "maximalist") -> str:
        """Generiert Radio-Segment aus Tweets."""
        if not tweets:
            return "Keine aktuellen Updates von unseren Bitcoin-OGs verfügbar."
        
        segments = []
        
        # Intro
        if persona == "maximalist":
            intro = "Zeit für Bitcoin-Alpha! Hier sind die neuesten Updates von unseren OGs:"
        elif persona == "cyberpunk":
            intro = "Incoming transmissions from the Bitcoin network:"
        else:  # retro
            intro = "Hey Leute! Hier sind die heißesten Bitcoin-News:"
        
        segments.append(intro)
        
        # Tweet-Segmente
        for i, tweet in enumerate(tweets[:3]):  # Max 3 Tweets pro Segment
            persona_intro = get_persona_intro(persona, tweet.username)
            
            segment = f"{persona_intro} {tweet.content}"
            segments.append(segment)
            
            if i < len(tweets) - 1:
                segments.append("Und weiter geht's...")
        
        # Outro
        if persona == "maximalist":
            outro = "Das war euer Bitcoin-Update! Stack Sats und HODL strong!"
        elif persona == "cyberpunk":
            outro = "End of transmission. Stay connected to the network."
        else:  # retro
            outro = "Das waren eure Bitcoin-Updates! Bleibt dran für mehr!"
        
        segments.append(outro)
        
        return " ".join(segments)
    
    def get_breaking_news(self) -> Optional[ProcessedTweet]:
        """Holt Breaking News von News-Accounts."""
        if not self.enabled:
            return None
        
        try:
            # Fokus auf News-Accounts
            news_accounts = [acc for acc in VIP_ACCOUNTS.values() if acc.category == "news_aggregator"]
            
            for account in news_accounts:
                tweets = self.get_vip_tweets(count=5, hours_back=2)  # Nur letzte 2 Stunden
                
                for tweet in tweets:
                    if tweet.engagement_score > 500:  # Hohe Engagement = Breaking News
                        return tweet
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Breaking News: {e}")
            return None

def test_x_feed_integration():
    """Testet die X-Feed Integration."""
    print("🐦 Teste X-Feed Integration...")
    
    try:
        manager = XFeedManager()
        
        if not manager.enabled:
            print("❌ X-Integration deaktiviert (API-Keys fehlen)")
            return False
        
        print("✅ X-Feed Manager initialisiert")
        
        # Test: VIP-Tweets abrufen
        print("\n📋 Hole VIP-Tweets...")
        tweets = manager.get_vip_tweets(count=5)
        
        print(f"✅ {len(tweets)} Tweets gefunden")
        
        for tweet in tweets[:3]:
            print(f"\n📝 @{tweet.username}: {tweet.content[:100]}...")
            print(f"   Engagement: {tweet.engagement_score}, Relevanz: {tweet.relevance_score:.2f}")
        
        # Test: Radio-Segment generieren
        if tweets:
            print("\n🎙️ Generiere Radio-Segment...")
            segment = manager.generate_radio_segment(tweets, "maximalist")
            print(f"✅ Segment generiert: {segment[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    test_x_feed_integration() 