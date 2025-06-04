#!/usr/bin/env python3

"""
Twitter/X Service
================

Service für Twitter/X API Integration:
- Tweet-Sammlung
- Trend-Analyse
- Social Media Monitoring
- Content-Extraktion
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


class TwitterService:
    """
    Service für Twitter/X API Integration
    
    Sammelt Tweets, Trends und Social Media Daten
    für die Broadcast-Generierung.
    """
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.base_url = "https://api.twitter.com/2"
        
        # Konfiguration
        self.config = {
            "max_tweets_per_request": 10,
            "tweet_fields": ["created_at", "author_id", "public_metrics", "context_annotations"],
            "user_fields": ["name", "username", "verified"],
            "expansions": ["author_id"],
            "default_language": "de"
        }
    
    async def search_tweets(
        self, 
        query: str, 
        max_results: int = 10,
        language: str = "de"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Sucht Tweets basierend auf Query
        
        Args:
            query: Suchbegriff oder -phrase
            max_results: Maximale Anzahl Ergebnisse
            language: Sprache der Tweets
            
        Returns:
            Liste von Tweet-Daten oder None bei Fehler
        """
        
        if not self.bearer_token:
            logger.warning("⚠️ Twitter Bearer Token nicht verfügbar")
            return None
        
        logger.info(f"🐦 Suche Tweets für: '{query}'")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "query": f"{query} lang:{language}",
                "max_results": min(max_results, self.config["max_tweets_per_request"]),
                "tweet.fields": ",".join(self.config["tweet_fields"]),
                "user.fields": ",".join(self.config["user_fields"]),
                "expansions": ",".join(self.config["expansions"])
            }
            
            url = f"{self.base_url}/tweets/search/recent"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._process_tweet_data(data)
                        
                        logger.info(f"✅ {len(tweets)} Tweets gefunden")
                        return tweets
                    
                    elif response.status == 429:
                        logger.warning("⚠️ Twitter API Rate Limit erreicht")
                        return None
                    
                    else:
                        logger.error(f"❌ Twitter API Fehler {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Fehler bei Twitter-Suche: {e}")
            return None
    
    async def get_trending_topics(
        self, 
        location_id: int = 23424957  # Switzerland
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Holt aktuelle Trending Topics
        
        Args:
            location_id: WOEID für Standort (23424957 = Schweiz)
            
        Returns:
            Liste von Trending Topics oder None
        """
        
        if not self.bearer_token:
            logger.warning("⚠️ Twitter Bearer Token nicht verfügbar")
            return None
        
        logger.info(f"📈 Hole Trending Topics für Location {location_id}")
        
        try:
            # Placeholder für Trends API
            # Die v2 API hat eingeschränkten Zugang zu Trends
            # Hier würde normalerweise die v1.1 Trends API verwendet
            
            # Fallback: Simuliere Trends basierend auf aktuellen Themen
            mock_trends = [
                {"name": "#Schweiz", "tweet_volume": 1500},
                {"name": "#Zürich", "tweet_volume": 800},
                {"name": "#Bitcoin", "tweet_volume": 2000},
                {"name": "#Tech", "tweet_volume": 1200}
            ]
            
            logger.info(f"✅ {len(mock_trends)} Trending Topics (Mock-Daten)")
            return mock_trends
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der Trends: {e}")
            return None
    
    async def get_user_tweets(
        self, 
        username: str, 
        max_results: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Holt Tweets eines spezifischen Users
        
        Args:
            username: Twitter Username (ohne @)
            max_results: Maximale Anzahl Tweets
            
        Returns:
            Liste von Tweets oder None
        """
        
        if not self.bearer_token:
            logger.warning("⚠️ Twitter Bearer Token nicht verfügbar")
            return None
        
        logger.info(f"👤 Hole Tweets von @{username}")
        
        try:
            # Erst User-ID ermitteln
            user_id = await self._get_user_id(username)
            if not user_id:
                return None
            
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "max_results": min(max_results, self.config["max_tweets_per_request"]),
                "tweet.fields": ",".join(self.config["tweet_fields"]),
                "exclude": "retweets,replies"
            }
            
            url = f"{self.base_url}/users/{user_id}/tweets"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._process_tweet_data(data)
                        
                        logger.info(f"✅ {len(tweets)} Tweets von @{username} gefunden")
                        return tweets
                    
                    else:
                        logger.error(f"❌ Fehler beim Abrufen der User-Tweets: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Fehler bei User-Tweet-Abruf: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Testet die Twitter API Verbindung"""
        
        if not self.bearer_token:
            return False
        
        try:
            # Einfacher Test mit einer kleinen Suche
            test_tweets = await self.search_tweets("test", max_results=1)
            return test_tweets is not None
            
        except Exception as e:
            logger.error(f"Twitter Connection Test Fehler: {e}")
            return False
    
    # Private Methods
    
    def _process_tweet_data(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verarbeitet Twitter API Response zu einheitlichem Format"""
        
        tweets = []
        
        if "data" not in api_response:
            return tweets
        
        # User-Daten für Lookup
        users = {}
        if "includes" in api_response and "users" in api_response["includes"]:
            for user in api_response["includes"]["users"]:
                users[user["id"]] = user
        
        for tweet_data in api_response["data"]:
            try:
                # Basis-Tweet-Daten
                tweet = {
                    "id": tweet_data["id"],
                    "text": tweet_data["text"],
                    "created_at": tweet_data.get("created_at"),
                    "author_id": tweet_data.get("author_id")
                }
                
                # Author-Informationen hinzufügen
                if tweet["author_id"] in users:
                    user = users[tweet["author_id"]]
                    tweet["author"] = {
                        "name": user.get("name"),
                        "username": user.get("username"),
                        "verified": user.get("verified", False)
                    }
                
                # Public Metrics
                if "public_metrics" in tweet_data:
                    metrics = tweet_data["public_metrics"]
                    tweet["metrics"] = {
                        "retweet_count": metrics.get("retweet_count", 0),
                        "like_count": metrics.get("like_count", 0),
                        "reply_count": metrics.get("reply_count", 0),
                        "quote_count": metrics.get("quote_count", 0)
                    }
                
                # Context Annotations (Themen)
                if "context_annotations" in tweet_data:
                    tweet["topics"] = [
                        annotation.get("entity", {}).get("name", "")
                        for annotation in tweet_data["context_annotations"]
                        if annotation.get("entity", {}).get("name")
                    ]
                
                # Hashtags extrahieren
                tweet["hashtags"] = self._extract_hashtags(tweet["text"])
                
                # Mentions extrahieren
                tweet["mentions"] = self._extract_mentions(tweet["text"])
                
                # Sentiment schätzen (einfach)
                tweet["sentiment"] = self._estimate_sentiment(tweet["text"])
                
                tweets.append(tweet)
                
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Verarbeiten eines Tweets: {e}")
                continue
        
        return tweets
    
    async def _get_user_id(self, username: str) -> Optional[str]:
        """Ermittelt User-ID für Username"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/users/by/username/{username}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("id")
                    
                    return None
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Ermitteln der User-ID: {e}")
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrahiert Hashtags aus Tweet-Text"""
        
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extrahiert Mentions aus Tweet-Text"""
        
        import re
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]
    
    def _estimate_sentiment(self, text: str) -> str:
        """Einfache Sentiment-Schätzung für Tweets"""
        
        text_lower = text.lower()
        
        positive_words = [
            "gut", "super", "toll", "fantastisch", "liebe", "freue", 
            "😊", "😍", "🎉", "👍", "❤️", "great", "awesome", "love"
        ]
        
        negative_words = [
            "schlecht", "schrecklich", "hasse", "furchtbar", "ärgerlich",
            "😢", "😡", "👎", "💔", "terrible", "awful", "hate", "bad"
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    # Utility Methods
    
    async def get_swiss_news_tweets(self, max_results: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Holt News-Tweets aus der Schweiz"""
        
        swiss_news_accounts = [
            "srfnews", "nzz", "tagesanzeiger", "20min", "blickch"
        ]
        
        all_tweets = []
        
        for account in swiss_news_accounts:
            try:
                tweets = await self.get_user_tweets(account, max_results=2)
                if tweets:
                    # Füge Source-Info hinzu
                    for tweet in tweets:
                        tweet["source_account"] = account
                    all_tweets.extend(tweets)
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Abrufen von @{account}: {e}")
                continue
        
        # Sortiere nach Erstellungszeit
        all_tweets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return all_tweets[:max_results]
    
    async def search_crypto_tweets(self, max_results: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Sucht Crypto-bezogene Tweets"""
        
        crypto_queries = [
            "Bitcoin Switzerland",
            "Crypto Schweiz", 
            "Blockchain Zürich"
        ]
        
        all_tweets = []
        
        for query in crypto_queries:
            try:
                tweets = await self.search_tweets(query, max_results=2)
                if tweets:
                    all_tweets.extend(tweets)
            except Exception as e:
                logger.warning(f"⚠️ Fehler bei Crypto-Tweet-Suche '{query}': {e}")
                continue
        
        # Duplikate entfernen (basierend auf Tweet-ID)
        seen_ids = set()
        unique_tweets = []
        
        for tweet in all_tweets:
            if tweet["id"] not in seen_ids:
                seen_ids.add(tweet["id"])
                unique_tweets.append(tweet)
        
        return unique_tweets[:max_results]
    
    def get_api_status(self) -> Dict[str, Any]:
        """Holt API-Status und Konfiguration"""
        
        return {
            "api_configured": bool(self.bearer_token),
            "api_key_available": bool(self.api_key),
            "access_token_available": bool(self.access_token),
            "base_url": self.base_url,
            "max_tweets_per_request": self.config["max_tweets_per_request"],
            "supported_languages": ["de", "en", "fr", "it"]
        } 