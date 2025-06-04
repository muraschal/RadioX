"""
RadioX X (Twitter) API Service - Bitcoin OG Accounts
Sammelt Top Tweets der letzten 30min basierend auf Likes - NUR ECHTE DATEN!
"""

import asyncio
import aiohttp
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
import json
import re
from pathlib import Path

# Load environment variables from root directory
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')


@dataclass
class XTweet:
    """X Tweet Item"""
    id: str
    text: str
    author_username: str
    author_name: str
    created_at: datetime
    like_count: int
    retweet_count: int
    reply_count: int
    url: str
    category: str
    priority: int
    tags: List[str]


class XAPIService:
    """X (Twitter) API Service für Bitcoin OG Accounts - NUR ECHTE DATEN"""
    
    def __init__(self, bearer_token: str = None):
        self.bearer_token = bearer_token or os.getenv('X_BEARER_TOKEN')
        
        if not self.bearer_token:
            logger.error("❌ X_BEARER_TOKEN nicht gefunden!")
            logger.info("💡 Prüfe die .env Datei im Root-Verzeichnis")
            logger.info(f"🔍 Suche in: {Path(__file__).parent.parent.parent.parent / '.env'}")
            raise ValueError("❌ X_BEARER_TOKEN nicht gefunden! Konfiguriere deine .env Datei.")
        
        logger.info(f"✅ X Bearer Token geladen: {self.bearer_token[:20]}...{self.bearer_token[-10:]}")
        
        # Rate Limit Tracking
        self.rate_limit_reset = {}
        self.rate_limit_remaining = {}
        
        # Cache für User IDs (um API Calls zu sparen)
        self.user_id_cache = {}
        
        # Bitcoin OG Accounts (aus der ursprünglichen Liste)
        self.bitcoin_og_accounts = {
            "saylor": {
                "username": "saylor",
                "name": "Michael Saylor",
                "description": "MicroStrategy CEO, Bitcoin Maximalist"
            },
            "jack": {
                "username": "jack", 
                "name": "Jack Dorsey",
                "description": "Twitter Founder, Bitcoin Advocate"
            },
            "elonmusk": {
                "username": "elonmusk",
                "name": "Elon Musk", 
                "description": "Tesla CEO, Crypto Influencer"
            },
            "APompliano": {
                "username": "APompliano",
                "name": "Anthony Pompliano",
                "description": "Bitcoin Podcaster & Investor"
            },
            "PeterMcCormack": {
                "username": "PeterMcCormack",
                "name": "Peter McCormack",
                "description": "What Bitcoin Did Podcast Host"
            },
            "nvk": {
                "username": "nvk",
                "name": "Rodolfo Novak",
                "description": "Coinkite CEO, Bitcoin Hardware"
            },
            "lopp": {
                "username": "lopp",
                "name": "Jameson Lopp",
                "description": "Bitcoin Security Expert"
            },
            "starkness": {
                "username": "starkness",
                "name": "Elizabeth Stark",
                "description": "Lightning Labs CEO"
            },
            "pierre_rochard": {
                "username": "pierre_rochard",
                "name": "Pierre Rochard",
                "description": "Bitcoin Developer"
            }
        }
        
        # Kategorie-Keywords für Tweet-Klassifizierung
        self.category_keywords = {
            "bitcoin": ["bitcoin", "btc", "#bitcoin", "satoshi", "hodl", "stack sats"],
            "wirtschaft": ["economy", "inflation", "fed", "dollar", "market", "stocks"],
            "technologie": ["tech", "ai", "software", "development", "innovation"],
            "weltpolitik": ["politics", "government", "policy", "regulation", "cbdc"],
            "philosophie": ["freedom", "liberty", "decentralization", "sovereignty"]
        }
        
        # Priority Keywords
        self.priority_keywords = {
            "breaking": ["breaking", "urgent", "alert", "announcement"],
            "high": ["important", "major", "significant", "huge", "massive"],
            "bitcoin": ["100k", "ath", "all time high", "moon", "adoption"],
            "market": ["crash", "pump", "dump", "rally", "bull", "bear"]
        }
    
    def _check_rate_limit(self, endpoint: str) -> bool:
        """Prüft ob Rate Limit erreicht ist"""
        now = time.time()
        
        if endpoint in self.rate_limit_reset:
            if now < self.rate_limit_reset[endpoint]:
                remaining = self.rate_limit_remaining.get(endpoint, 0)
                if remaining <= 0:
                    reset_in = int(self.rate_limit_reset[endpoint] - now)
                    logger.warning(f"⏳ Rate Limit erreicht für {endpoint}. Reset in {reset_in}s")
                    return False
        
        return True
    
    def _update_rate_limit(self, response_headers: Dict, endpoint: str):
        """Aktualisiert Rate Limit Info aus Response Headers"""
        if 'x-rate-limit-remaining' in response_headers:
            self.rate_limit_remaining[endpoint] = int(response_headers['x-rate-limit-remaining'])
        
        if 'x-rate-limit-reset' in response_headers:
            self.rate_limit_reset[endpoint] = int(response_headers['x-rate-limit-reset'])
    
    async def get_user_tweets(
        self, 
        username: str, 
        max_results: int = 10,
        since_minutes: int = 30
    ) -> List[XTweet]:
        """Holt Tweets eines Users der letzten X Minuten - NUR ECHTE DATEN"""
        
        endpoint = "user_timeline"
        
        # Rate Limit prüfen
        if not self._check_rate_limit(endpoint):
            logger.warning(f"⏳ Überspringe @{username} wegen Rate Limit")
            return []
        
        try:
            # User ID holen (mit Cache)
            user_id = await self._get_user_id(username)
            if not user_id:
                logger.error(f"❌ User ID für @{username} nicht gefunden")
                return []
            
            # Zeitfilter für die letzten X Minuten
            since_time = datetime.utcnow() - timedelta(minutes=since_minutes)
            start_time = since_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': min(max_results, 100),  # API Maximum
                'start_time': start_time,
                'tweet.fields': 'created_at,public_metrics,context_annotations,author_id',
                'user.fields': 'name,username',
                'expansions': 'author_id'
            }
            
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=30) as response:
                    
                    # Rate Limit Info aktualisieren
                    self._update_rate_limit(response.headers, endpoint)
                    
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._parse_tweets(data, username)
                        logger.info(f"✅ @{username}: {len(tweets)} Tweets geladen")
                        return tweets
                    
                    elif response.status == 429:
                        logger.warning(f"⏳ Rate Limit für @{username} - warte bis Reset")
                        return []
                    
                    elif response.status == 401:
                        logger.error(f"🔐 Unauthorized für @{username} - Bearer Token prüfen")
                        return []
                    
                    elif response.status == 404:
                        logger.warning(f"👤 User @{username} nicht gefunden oder privat")
                        return []
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ X API Error {response.status} für @{username}: {error_text}")
                        return []
                        
        except asyncio.TimeoutError:
            logger.error(f"⏰ Timeout beim Laden von @{username}")
            return []
        except Exception as e:
            logger.error(f"💥 Fehler beim Laden von @{username}: {e}")
            return []
    
    async def _get_user_id(self, username: str) -> Optional[str]:
        """Holt User ID für Username (mit Cache)"""
        
        # Cache prüfen
        if username in self.user_id_cache:
            return self.user_id_cache[username]
        
        try:
            url = f"https://api.twitter.com/2/users/by/username/{username}"
            headers = {'Authorization': f'Bearer {self.bearer_token}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_id = data['data']['id']
                        
                        # Cache speichern
                        self.user_id_cache[username] = user_id
                        logger.debug(f"📋 User ID für @{username}: {user_id}")
                        
                        return user_id
                    else:
                        logger.error(f"❌ User ID Fehler {response.status} für @{username}")
                        return None
        except Exception as e:
            logger.error(f"💥 Fehler beim Holen der User ID für @{username}: {e}")
            return None
    
    def _parse_tweets(self, data: Dict, username: str) -> List[XTweet]:
        """Parst X API Response zu Tweet Objects"""
        tweets = []
        
        if 'data' not in data:
            logger.debug(f"📭 Keine Tweets für @{username} im Zeitfenster")
            return tweets
        
        account_info = self.bitcoin_og_accounts.get(username, {})
        
        for tweet_data in data['data']:
            try:
                # Datum parsen
                created_at = datetime.fromisoformat(
                    tweet_data['created_at'].replace('Z', '+00:00')
                )
                
                # Metrics extrahieren
                metrics = tweet_data.get('public_metrics', {})
                like_count = metrics.get('like_count', 0)
                retweet_count = metrics.get('retweet_count', 0)
                reply_count = metrics.get('reply_count', 0)
                
                # Text für Analyse
                text = tweet_data['text']
                
                # Kategorie und Priorität bestimmen
                category = self._detect_category(text)
                priority = self._calculate_priority(text, like_count, retweet_count)
                tags = self._extract_tags(text)
                
                tweet = XTweet(
                    id=tweet_data['id'],
                    text=text,
                    author_username=username,
                    author_name=account_info.get('name', username),
                    created_at=created_at,
                    like_count=like_count,
                    retweet_count=retweet_count,
                    reply_count=reply_count,
                    url=f"https://twitter.com/{username}/status/{tweet_data['id']}",
                    category=category,
                    priority=priority,
                    tags=tags
                )
                
                tweets.append(tweet)
                
            except Exception as e:
                logger.error(f"💥 Fehler beim Parsen von Tweet: {e}")
                continue
        
        return tweets
    
    def _detect_category(self, text: str) -> str:
        """Erkennt Kategorie basierend auf Tweet-Text"""
        text_lower = text.lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        # Beste Kategorie oder Default
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0] if best_category[1] > 0 else "bitcoin"
    
    def _calculate_priority(self, text: str, likes: int, retweets: int) -> int:
        """Berechnet Tweet-Priorität basierend auf Engagement und Keywords"""
        text_lower = text.lower()
        priority = 5  # Base priority
        
        # Engagement-basierte Priorität
        if likes > 1000:
            priority += 3
        elif likes > 500:
            priority += 2
        elif likes > 100:
            priority += 1
        
        if retweets > 100:
            priority += 2
        elif retweets > 50:
            priority += 1
        
        # Keyword-basierte Priorität
        for keyword in self.priority_keywords["breaking"]:
            if keyword in text_lower:
                priority += 3
                break
        
        for keyword in self.priority_keywords["bitcoin"]:
            if keyword in text_lower:
                priority += 2
                break
        
        for keyword in self.priority_keywords["high"]:
            if keyword in text_lower:
                priority += 1
                break
        
        return max(1, min(10, priority))
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extrahiert Hashtags und wichtige Keywords"""
        tags = []
        
        # Hashtags extrahieren
        hashtags = re.findall(r'#(\w+)', text.lower())
        tags.extend(hashtags[:3])
        
        # Wichtige Keywords
        text_lower = text.lower()
        important_keywords = ["bitcoin", "btc", "hodl", "sats", "lightning", "defi"]
        
        for keyword in important_keywords:
            if keyword in text_lower and keyword not in tags:
                tags.append(keyword)
        
        return tags[:5]
    
    async def get_bitcoin_og_tweets(
        self, 
        since_minutes: int = 30,
        max_per_account: int = 4
    ) -> List[XTweet]:
        """Sammelt Top Tweets aller Bitcoin OG Accounts der letzten 30min - NUR ECHTE DATEN"""
        
        logger.info(f"🐦 Sammle Bitcoin OG Tweets der letzten {since_minutes} Minuten...")
        
        all_tweets = []
        
        # Accounts in kleineren Batches verarbeiten (wegen Rate Limits)
        batch_size = 3
        account_list = list(self.bitcoin_og_accounts.keys())
        
        for i in range(0, len(account_list), batch_size):
            batch = account_list[i:i + batch_size]
            
            # Batch parallel verarbeiten
            tasks = []
            for username in batch:
                task = self.get_user_tweets(username, max_per_account, since_minutes)
                tasks.append(task)
            
            # Batch Results sammeln
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(results):
                username = batch[j]
                if isinstance(result, list):
                    all_tweets.extend(result)
                    logger.info(f"   📱 @{username}: {len(result)} Tweets")
                elif isinstance(result, Exception):
                    logger.error(f"   ❌ @{username}: {result}")
            
            # Kurze Pause zwischen Batches (Rate Limit schonen)
            if i + batch_size < len(account_list):
                await asyncio.sleep(1)
        
        # Nach Likes sortieren
        all_tweets.sort(key=lambda x: x.like_count, reverse=True)
        
        # Top Tweets pro Account filtern
        account_tweet_counts = {}
        filtered_tweets = []
        
        for tweet in all_tweets:
            username = tweet.author_username
            count = account_tweet_counts.get(username, 0)
            
            if count < max_per_account:
                filtered_tweets.append(tweet)
                account_tweet_counts[username] = count + 1
        
        logger.info(f"✅ {len(filtered_tweets)} Bitcoin OG Tweets gesammelt")
        
        return filtered_tweets[:20]  # Max 20 für eine Stunde
    
    async def get_breaking_bitcoin_tweets(self) -> List[XTweet]:
        """Spezielle Funktion für Breaking News Station - nur High-Priority Bitcoin Tweets"""
        
        tweets = await self.get_bitcoin_og_tweets(since_minutes=60, max_per_account=3)  # Längeres Zeitfenster
        
        # Nur hohe Priorität für Breaking News
        breaking_tweets = [tweet for tweet in tweets if tweet.priority >= 7]
        
        logger.info(f"🚨 {len(breaking_tweets)} Breaking Bitcoin Tweets gefiltert")
        
        return breaking_tweets[:6]  # Top 6 für Breaking News


# Convenience Functions
async def get_bitcoin_tweets(since_minutes: int = 30) -> List[XTweet]:
    """Holt aktuelle Bitcoin OG Tweets - NUR ECHTE DATEN"""
    service = XAPIService()
    return await service.get_bitcoin_og_tweets(since_minutes=since_minutes)

async def get_breaking_bitcoin_news() -> List[XTweet]:
    """Holt Breaking Bitcoin Tweets für Radio Station - NUR ECHTE DATEN"""
    service = XAPIService()
    return await service.get_breaking_bitcoin_tweets() 