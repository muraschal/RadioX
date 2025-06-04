"""
Twitter/X API Service für RadioX
Sammelt Tweets von konfigurierten Accounts
"""

import tweepy
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import sys
import os

# Backend-Pfad hinzufügen für relative Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import get_settings
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class TwitterService:
    """Service für Twitter/X API Integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase = SupabaseClient()
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Initialisiert Twitter API Client"""
        try:
            # Twitter API v2 Client mit Bearer Token
            self.client = tweepy.Client(
                bearer_token=self.settings.x_bearer_token,
                consumer_key=self.settings.x_api_key,
                consumer_secret=self.settings.x_api_secret,
                access_token=self.settings.x_access_token,
                access_token_secret=self.settings.x_access_token_secret,
                wait_on_rate_limit=True
            )
            logger.info("Twitter API Client erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren des Twitter Clients: {e}")
            self.client = None
    
    async def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """
        Holt die neuesten Tweets eines Users
        
        Args:
            username: Twitter Handle ohne @
            max_results: Anzahl Tweets (max 100)
            
        Returns:
            Liste von Tweet-Dictionaries
        """
        if not self.client:
            logger.error("Twitter Client nicht verfügbar")
            return []
        
        try:
            # User ID abrufen
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"User {username} nicht gefunden")
                return []
            
            user_id = user.data.id
            
            # Tweets abrufen (letzte 24h)
            since_time = datetime.utcnow() - timedelta(hours=24)
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'entities'],
                start_time=since_time,
                exclude=['retweets', 'replies']  # Nur Original-Tweets
            )
            
            if not tweets.data:
                logger.info(f"Keine neuen Tweets von {username} gefunden")
                return []
            
            # Tweets formatieren
            formatted_tweets = []
            for tweet in tweets.data:
                formatted_tweet = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'username': username,
                    'metrics': {
                        'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                        'like_count': tweet.public_metrics.get('like_count', 0),
                        'reply_count': tweet.public_metrics.get('reply_count', 0),
                        'quote_count': tweet.public_metrics.get('quote_count', 0)
                    },
                    'hashtags': self._extract_hashtags(tweet),
                    'mentions': self._extract_mentions(tweet),
                    'urls': self._extract_urls(tweet)
                }
                formatted_tweets.append(formatted_tweet)
            
            logger.info(f"{len(formatted_tweets)} Tweets von {username} abgerufen")
            return formatted_tweets
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Tweets von {username}: {e}")
            return []
    
    def _extract_hashtags(self, tweet) -> List[str]:
        """Extrahiert Hashtags aus Tweet"""
        if hasattr(tweet, 'entities') and tweet.entities and 'hashtags' in tweet.entities:
            return [f"#{tag['tag']}" for tag in tweet.entities['hashtags']]
        return []
    
    def _extract_mentions(self, tweet) -> List[str]:
        """Extrahiert Mentions aus Tweet"""
        if hasattr(tweet, 'entities') and tweet.entities and 'mentions' in tweet.entities:
            return [f"@{mention['username']}" for mention in tweet.entities['mentions']]
        return []
    
    def _extract_urls(self, tweet) -> List[str]:
        """Extrahiert URLs aus Tweet"""
        if hasattr(tweet, 'entities') and tweet.entities and 'urls' in tweet.entities:
            return [url['expanded_url'] for url in tweet.entities['urls']]
        return []
    
    async def collect_tweets_for_category(self, category_slug: str) -> List[Dict]:
        """
        Sammelt Tweets für eine bestimmte Kategorie
        
        Args:
            category_slug: Kategorie (bitcoin, wirtschaft, etc.)
            
        Returns:
            Liste aller Tweets der Kategorie
        """
        try:
            # Twitter Sources für Kategorie abrufen
            sources = await self.supabase.get_content_sources_by_category(
                category_slug=category_slug,
                source_type='twitter',
                active_only=True
            )
            
            if not sources:
                logger.info(f"Keine Twitter Sources für Kategorie {category_slug} gefunden")
                return []
            
            all_tweets = []
            
            # Tweets von allen Sources sammeln
            for source in sources:
                username = source['identifier']
                tweets = await self.get_user_tweets(username, max_results=5)
                
                # Source-Info zu jedem Tweet hinzufügen
                for tweet in tweets:
                    tweet['source_id'] = source['id']
                    tweet['category_slug'] = category_slug
                    tweet['priority_level'] = source['priority_level']
                
                all_tweets.extend(tweets)
            
            # Nach Relevanz und Priorität sortieren
            all_tweets.sort(key=lambda x: (
                -x['priority_level'],  # Höhere Priorität zuerst
                -x['metrics']['like_count'],  # Mehr Likes zuerst
                -x['metrics']['retweet_count']  # Mehr Retweets zuerst
            ))
            
            logger.info(f"{len(all_tweets)} Tweets für Kategorie {category_slug} gesammelt")
            return all_tweets
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der Tweets für {category_slug}: {e}")
            return []
    
    async def collect_all_tweets(self) -> Dict[str, List[Dict]]:
        """
        Sammelt Tweets für alle aktiven Kategorien
        
        Returns:
            Dictionary mit Kategorie -> Tweet-Liste
        """
        try:
            categories = await self.supabase.get_active_categories()
            all_tweets = {}
            
            for category in categories:
                category_slug = category['slug']
                tweets = await self.collect_tweets_for_category(category_slug)
                all_tweets[category_slug] = tweets
            
            total_tweets = sum(len(tweets) for tweets in all_tweets.values())
            logger.info(f"Insgesamt {total_tweets} Tweets von allen Kategorien gesammelt")
            
            return all_tweets
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln aller Tweets: {e}")
            return {}
    
    async def save_tweets_to_db(self, tweets: List[Dict], stream_id: Optional[str] = None) -> int:
        """
        Speichert Tweets in der Datenbank
        
        Args:
            tweets: Liste von Tweet-Dictionaries
            stream_id: Optional Stream ID
            
        Returns:
            Anzahl gespeicherter Tweets
        """
        saved_count = 0
        
        try:
            for tweet in tweets:
                # Prüfen ob Tweet bereits existiert
                existing = await self.supabase.get_news_content_by_external_id(
                    external_id=str(tweet['id'])
                )
                
                if existing:
                    continue  # Tweet bereits vorhanden
                
                # Tweet in news_content speichern
                news_data = {
                    'stream_id': stream_id,
                    'category_id': await self.supabase.get_category_id_by_slug(tweet['category_slug']),
                    'source_id': tweet['source_id'],
                    'content_type': 'tweet',
                    'original_text': tweet['text'],
                    'relevance_score': self._calculate_relevance_score(tweet),
                    'sentiment_score': 0.0,  # Wird später von GPT berechnet
                    'metadata': {
                        'tweet_id': tweet['id'],
                        'username': tweet['username'],
                        'created_at': tweet['created_at'].isoformat(),
                        'metrics': tweet['metrics'],
                        'hashtags': tweet['hashtags'],
                        'mentions': tweet['mentions'],
                        'urls': tweet['urls']
                    }
                }
                
                await self.supabase.create_news_content(news_data)
                saved_count += 1
            
            logger.info(f"{saved_count} neue Tweets in Datenbank gespeichert")
            return saved_count
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Tweets: {e}")
            return saved_count
    
    def _calculate_relevance_score(self, tweet: Dict) -> float:
        """
        Berechnet Relevance Score basierend auf Engagement
        
        Args:
            tweet: Tweet Dictionary
            
        Returns:
            Relevance Score (0.0 - 1.0)
        """
        metrics = tweet['metrics']
        
        # Basis-Score basierend auf Engagement
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        # Gewichtetes Engagement
        engagement_score = (likes * 1) + (retweets * 3) + (replies * 2)
        
        # Normalisierung (logarithmisch für große Zahlen)
        import math
        if engagement_score > 0:
            normalized_score = min(1.0, math.log10(engagement_score + 1) / 4)
        else:
            normalized_score = 0.1  # Minimum Score
        
        # Bonus für Bitcoin-Keywords
        text_lower = tweet['text'].lower()
        bitcoin_keywords = ['bitcoin', 'btc', 'cryptocurrency', 'blockchain']
        if any(keyword in text_lower for keyword in bitcoin_keywords):
            normalized_score = min(1.0, normalized_score * 1.2)
        
        return round(normalized_score, 2)


# Async Wrapper für einfache Nutzung
async def collect_latest_tweets() -> Dict[str, List[Dict]]:
    """Sammelt die neuesten Tweets aller Kategorien"""
    service = TwitterService()
    return await service.collect_all_tweets()


async def collect_tweets_for_stream(stream_id: str, category_mix: Dict[str, int]) -> int:
    """
    Sammelt Tweets für einen spezifischen Stream basierend auf Category Mix
    
    Args:
        stream_id: Stream ID
        category_mix: Dictionary mit Kategorie -> Prozent
        
    Returns:
        Anzahl gesammelter Tweets
    """
    service = TwitterService()
    total_saved = 0
    
    for category_slug, percentage in category_mix.items():
        if percentage > 0:
            # Anzahl Tweets basierend auf Prozentsatz
            max_tweets = max(1, int(percentage / 10))  # 10% = 1 Tweet, 50% = 5 Tweets
            
            tweets = await service.collect_tweets_for_category(category_slug)
            selected_tweets = tweets[:max_tweets]  # Top Tweets nehmen
            
            saved = await service.save_tweets_to_db(selected_tweets, stream_id)
            total_saved += saved
    
    return total_saved 