"""
RadioX RSS Service - Pure Data Collection
=========================================

Minimalistic RSS service for data collection only.
Collects ALL active RSS feeds without filtering or intelligence.
"""

import asyncio
import aiohttp
import feedparser
import html
import re
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import logging

from database.supabase_client import get_db

logger = logging.getLogger(__name__)

@dataclass
class RSSNewsItem:
    """RSS News Item - Raw Data Only"""
    title: str
    summary: str
    link: str
    published: datetime
    source: str
    category: str
    priority: int
    weight: float


class RSSService:
    """Pure RSS data collection service - collects ALL active feeds"""
    
    def __init__(self):
        # Lazy loading - only initialize when needed
        self._supabase = None
    
    @property
    def supabase(self):
        """Lazy loading of Supabase connection"""
        if self._supabase is None:
            db_wrapper = get_db()
            self._supabase = db_wrapper.client
        return self._supabase
    
    async def get_all_active_feeds(self) -> List[Dict[str, Any]]:
        """Get ALL active RSS feed configurations"""
        try:
            # Load ALL active feeds from database
            response = self.supabase.table("rss_feed_preferences").select("*").eq("is_active", True).order("priority", desc=True).execute()
            
            feeds = []
            for row in response.data:
                feed_config = {
                    "id": f"{row.get('source_name', 'unknown')}_{row['feed_category']}",
                    "source_name": row.get('source_name', 'unknown'),
                    "feed_category": row['feed_category'],
                    "feed_url": row['feed_url'],
                    "priority": row['priority'],
                    "weight": float(row['weight']),
                    "is_active": row['is_active']
                }
                feeds.append(feed_config)
            
            return feeds
            
        except Exception as e:
            logger.error(f"Failed to get active feeds: {e}")
            return []
    
    async def get_all_recent_news(self, max_age_hours: int = 12) -> List[RSSNewsItem]:
        """Collect recent news from ALL active RSS feeds - pure data collection"""
        try:
            # Get ALL active feed configurations
            feeds = await self.get_all_active_feeds()
            
            if not feeds:
                logger.warning("No active RSS feeds found")
                return []
            
            # Collect news from ALL feeds in parallel
            tasks = []
            for feed in feeds:
                task = self._fetch_feed(
                    url=feed['feed_url'],
                    source=feed['source_name'],
                    category=feed['feed_category'],
                    priority=feed['priority'],
                    weight=feed['weight'],
                    max_age_hours=max_age_hours
                )
                tasks.append(task)
            
            # Execute all feed requests in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_news = []
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Feed error: {result}")
            
            # Filter by age
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            recent_news = [
                news for news in all_news 
                if news.published > cutoff_time
            ]
            
            # Remove duplicates
            unique_news = self._remove_duplicates(recent_news)
            
            # Simple sorting by priority and weight only
            sorted_news = sorted(
                unique_news,
                key=lambda x: (x.priority, x.weight),
                reverse=True
            )
            
            return sorted_news
            
        except Exception as e:
            logger.error(f"Failed to collect all news: {e}")
            return []
    
    async def _fetch_feed(self, url: str, source: str, category: str, priority: int, weight: float, max_age_hours: int) -> List[RSSNewsItem]:
        """Fetch and parse RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_feed_content(content, source, category, priority, weight, max_age_hours)
                    else:
                        logger.warning(f"RSS feed error {response.status}: {url}")
                        return []
        except Exception as e:
            logger.warning(f"Failed to fetch RSS feed {url}: {e}")
            return []
    
    def _parse_feed_content(self, content: str, source: str, category: str, priority: int, weight: float, max_age_hours: int) -> List[RSSNewsItem]:
        """Parse RSS content to news items - no intelligence, pure data"""
        try:
            feed = feedparser.parse(content)
            news_items = []
            
            for entry in feed.entries[:25]:  # Top 25 per feed (increased)
                # Parse publication date
                published = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                
                # Only include news within time range
                if published < datetime.now() - timedelta(hours=max_age_hours):
                    continue
                
                # Clean text content
                title = self._clean_html(entry.title)
                summary = self._clean_html(getattr(entry, 'summary', entry.title)[:300])
                
                news_item = RSSNewsItem(
                    title=title,
                    summary=summary,
                    link=getattr(entry, 'link', ''),
                    published=published,
                    source=source,
                    category=category,
                    priority=priority,
                    weight=weight
                )
                
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            logger.warning(f"Failed to parse RSS content: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        clean_text = html.unescape(clean_text)
        
        # Remove multiple whitespaces
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _remove_duplicates(self, news_items: List[RSSNewsItem]) -> List[RSSNewsItem]:
        """Remove similar news items based on title similarity"""
        unique_news = []
        seen_titles = set()
        
        for item in news_items:
            # Simplified title for duplicate detection
            simple_title = re.sub(r'[^\w\s]', '', item.title.lower())
            title_words = set(simple_title.split())
            
            # Check for similar titles
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                # If 80% of words match = duplicate (less aggressive)
                if len(title_words) > 0 and len(title_words | seen_words) > 0:
                    if len(title_words & seen_words) / len(title_words | seen_words) > 0.8:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_news.append(item)
                seen_titles.add(simple_title)
        
        return unique_news 