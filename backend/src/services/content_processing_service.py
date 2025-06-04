#!/usr/bin/env python3

"""
Content Processing Service
=========================

Service für die Verarbeitung und Aufbereitung aller gesammelten Daten:
- News-Analyse und Kategorisierung
- Content-Filterung und Priorisierung
- Themen-Extraktion und Clustering
- Sentiment-Analyse
- Content-Optimierung für Radio
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import hashlib
from collections import defaultdict, Counter

from .supabase_service import SupabaseService


class ContentProcessingService:
    """
    Service für die intelligente Verarbeitung von Content
    
    Analysiert, filtert und optimiert alle gesammelten Daten
    für die Broadcast-Generierung.
    """
    
    def __init__(self):
        self.supabase = SupabaseService()
        
        # Konfiguration
        self.config = {
            "min_news_length": 50,
            "max_news_length": 1000,
            "duplicate_threshold": 0.8,
            "sentiment_weights": {
                "positive": 1.2,
                "neutral": 1.0,
                "negative": 0.8
            },
            "category_priorities": {
                "local": 10,
                "breaking": 9,
                "politics": 8,
                "economy": 7,
                "technology": 7,
                "crypto": 6,
                "sports": 5,
                "entertainment": 4
            }
        }
        
        # Kategorisierungs-Keywords
        self.category_keywords = {
            "local": ["zürich", "zurich", "basel", "bern", "schweiz", "switzerland"],
            "politics": ["politik", "regierung", "parlament", "wahl", "partei"],
            "economy": ["wirtschaft", "börse", "unternehmen", "markt", "inflation"],
            "technology": ["technologie", "tech", "ki", "ai", "digital", "software"],
            "crypto": ["bitcoin", "ethereum", "crypto", "blockchain", "kryptowährung"],
            "sports": ["sport", "fussball", "tennis", "ski", "olympia"],
            "entertainment": ["film", "musik", "kultur", "festival", "konzert"],
            "health": ["gesundheit", "medizin", "corona", "impfung", "krankenhaus"],
            "environment": ["umwelt", "klima", "energie", "nachhaltigkeit"]
        }
    
    async def process_content(
        self,
        raw_data: Dict[str, Any],
        target_news_count: int = 4,
        target_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet alle gesammelten Rohdaten
        
        Args:
            raw_data: Rohdaten vom DataCollectionService
            target_news_count: Gewünschte Anzahl News
            target_time: Zielzeit für zeitspezifische Optimierung
            
        Returns:
            Dict mit verarbeiteten und optimierten Daten
        """
        
        logger.info(f"🔄 Verarbeite Content für {target_news_count} News")
        
        # 1. News-Verarbeitung
        processed_news = await self._process_news(
            raw_data.get("news", []),
            target_count=target_news_count
        )
        
        # 2. Kontext-Daten aufbereiten
        processed_context = self._process_context_data(
            weather=raw_data.get("weather"),
            crypto=raw_data.get("crypto"),
            twitter=raw_data.get("twitter")
        )
        
        # 3. Zeitspezifische Optimierung
        if target_time:
            processed_news = self._optimize_for_time(processed_news, target_time)
        
        # 4. Themen-Balance sicherstellen
        balanced_news = self._ensure_topic_balance(processed_news)
        
        # 5. Finale Qualitätsprüfung
        quality_score = self._assess_content_quality(balanced_news, processed_context)
        
        result = {
            "selected_news": balanced_news,
            "context_data": processed_context,
            "processing_stats": {
                "original_news_count": len(raw_data.get("news", [])),
                "processed_news_count": len(balanced_news),
                "quality_score": quality_score,
                "processing_timestamp": datetime.now().isoformat()
            },
            "topic_distribution": self._analyze_topic_distribution(balanced_news),
            "content_metrics": self._calculate_content_metrics(balanced_news)
        }
        
        logger.info(f"✅ Content verarbeitet: {len(balanced_news)} News, "
                   f"Qualität: {quality_score:.2f}")
        
        return result
    
    async def analyze_news(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert News ohne Selektion"""
        
        logger.info(f"📊 Analysiere {len(news_list)} News")
        
        # Kategorisierung
        categorized = [self._categorize_news_item(news) for news in news_list]
        
        # Duplikate finden
        duplicates = self._find_duplicates(categorized)
        
        # Sentiment-Analyse
        sentiment_stats = self._analyze_sentiment_distribution(categorized)
        
        # Themen-Verteilung
        topic_dist = self._analyze_topic_distribution(categorized)
        
        return {
            "total_news": len(news_list),
            "categorized_news": categorized,
            "duplicates_found": len(duplicates),
            "sentiment_distribution": sentiment_stats,
            "topic_distribution": topic_dist,
            "quality_metrics": self._calculate_content_metrics(categorized)
        }
    
    async def test_processing(self) -> bool:
        """Testet die Content-Processing-Funktionalität"""
        
        # Test mit Dummy-Daten
        test_news = [
            {
                "title": "Test News Zürich",
                "summary": "Eine Test-Nachricht über Zürich für die Verarbeitung.",
                "source": "test",
                "published_date": datetime.now().isoformat()
            }
        ]
        
        try:
            result = await self.analyze_news(test_news)
            return result["total_news"] == 1
        except Exception as e:
            logger.error(f"Content Processing Test Fehler: {e}")
            return False
    
    # Private Processing Methods
    
    async def _process_news(
        self, 
        news_list: List[Dict[str, Any]], 
        target_count: int
    ) -> List[Dict[str, Any]]:
        """Verarbeitet und selektiert News"""
        
        if not news_list:
            logger.warning("⚠️ Keine News zum Verarbeiten")
            return []
        
        # 1. Basis-Filterung
        filtered_news = self._filter_news_quality(news_list)
        logger.info(f"📰 {len(filtered_news)} News nach Qualitäts-Filter")
        
        # 2. Kategorisierung
        categorized_news = [self._categorize_news_item(news) for news in filtered_news]
        
        # 3. Duplikate entfernen
        deduplicated_news = self._remove_duplicates(categorized_news)
        logger.info(f"📰 {len(deduplicated_news)} News nach Duplikat-Entfernung")
        
        # 4. Priorisierung
        prioritized_news = self._prioritize_news(deduplicated_news)
        
        # 5. Selektion der besten News
        selected_news = self._select_top_news(prioritized_news, target_count)
        
        # 6. Verwendete News markieren
        await self._mark_news_as_used(selected_news)
        
        return selected_news
    
    def _filter_news_quality(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtert News nach Qualitätskriterien"""
        
        filtered = []
        
        for news in news_list:
            # Mindestlänge prüfen
            title_len = len(news.get("title", ""))
            summary_len = len(news.get("summary", ""))
            
            if title_len < 10 or summary_len < self.config["min_news_length"]:
                continue
            
            # Maximallänge prüfen
            if summary_len > self.config["max_news_length"]:
                # Kürze Summary
                news["summary"] = news["summary"][:self.config["max_news_length"]] + "..."
            
            # Spam-Filter
            if self._is_spam_content(news):
                continue
            
            filtered.append(news)
        
        return filtered
    
    def _categorize_news_item(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """Kategorisiert eine einzelne News"""
        
        text = f"{news.get('title', '')} {news.get('summary', '')}".lower()
        
        # Kategorien bestimmen
        categories = []
        for category, keywords in self.category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Fallback-Kategorie
        if not categories:
            categories = ["general"]
        
        # Sentiment schätzen
        sentiment = self._estimate_sentiment(text)
        
        # Lokalität bestimmen
        is_local = any(keyword in text for keyword in self.category_keywords["local"])
        
        # News erweitern
        enhanced_news = news.copy()
        enhanced_news.update({
            "categories": categories,
            "primary_category": categories[0],
            "sentiment": sentiment,
            "is_local": is_local,
            "priority_score": self._calculate_priority_score(news, categories, sentiment, is_local),
            "content_hash": self._generate_content_hash(news)
        })
        
        return enhanced_news
    
    def _remove_duplicates(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Entfernt Duplikate basierend auf Content-Ähnlichkeit"""
        
        seen_hashes = set()
        unique_news = []
        
        for news in news_list:
            content_hash = news.get("content_hash")
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_news.append(news)
        
        return unique_news
    
    def _prioritize_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Priorisiert News nach verschiedenen Kriterien"""
        
        return sorted(
            news_list,
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )
    
    def _select_top_news(self, news_list: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """Selektiert die besten News mit Diversitäts-Berücksichtigung"""
        
        if len(news_list) <= target_count:
            return news_list
        
        selected = []
        used_categories = set()
        
        # Erste Runde: Eine News pro Kategorie
        for news in news_list:
            if len(selected) >= target_count:
                break
            
            primary_cat = news.get("primary_category")
            if primary_cat not in used_categories:
                selected.append(news)
                used_categories.add(primary_cat)
        
        # Zweite Runde: Auffüllen mit besten verbleibenden News
        remaining = [n for n in news_list if n not in selected]
        remaining_needed = target_count - len(selected)
        
        selected.extend(remaining[:remaining_needed])
        
        return selected
    
    def _ensure_topic_balance(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stellt sicher, dass verschiedene Themen vertreten sind"""
        
        if len(news_list) <= 2:
            return news_list
        
        # Analysiere aktuelle Verteilung
        categories = [news.get("primary_category") for news in news_list]
        category_counts = Counter(categories)
        
        # Wenn eine Kategorie dominiert, diversifiziere
        max_count = max(category_counts.values())
        total_news = len(news_list)
        
        if max_count > total_news * 0.6:  # Mehr als 60% einer Kategorie
            # Reduziere dominante Kategorie
            dominant_category = max(category_counts, key=category_counts.get)
            
            balanced = []
            category_added = defaultdict(int)
            
            for news in news_list:
                cat = news.get("primary_category")
                
                # Erlaube maximal die Hälfte einer Kategorie
                if cat == dominant_category and category_added[cat] >= total_news // 2:
                    continue
                
                balanced.append(news)
                category_added[cat] += 1
            
            return balanced
        
        return news_list
    
    def _optimize_for_time(self, news_list: List[Dict[str, Any]], target_time: str) -> List[Dict[str, Any]]:
        """Optimiert News-Auswahl für spezifische Tageszeit"""
        
        try:
            hour = int(target_time.split(":")[0])
        except:
            return news_list
        
        # Zeitspezifische Gewichtungen
        time_weights = {
            "morning": (6, 11),    # 6-11 Uhr
            "afternoon": (12, 17), # 12-17 Uhr  
            "evening": (18, 22),   # 18-22 Uhr
            "night": (23, 5)       # 23-5 Uhr
        }
        
        # Bestimme Tageszeit
        current_period = "afternoon"  # Default
        for period, (start, end) in time_weights.items():
            if start <= hour <= end or (period == "night" and (hour >= 23 or hour <= 5)):
                current_period = period
                break
        
        # Zeitspezifische Anpassungen
        if current_period == "morning":
            # Morgens: Mehr positive News, Wetter wichtiger
            for news in news_list:
                if news.get("sentiment") == "positive":
                    news["priority_score"] *= 1.2
                if news.get("is_local"):
                    news["priority_score"] *= 1.1
        
        elif current_period == "evening":
            # Abends: Mehr entspannte Themen
            for news in news_list:
                if news.get("primary_category") in ["entertainment", "sports"]:
                    news["priority_score"] *= 1.2
        
        # Neu sortieren
        return sorted(news_list, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    def _process_context_data(
        self, 
        weather: Optional[Dict[str, Any]], 
        crypto: Optional[Dict[str, Any]], 
        twitter: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Verarbeitet Kontext-Daten"""
        
        processed = {
            "weather": None,
            "crypto": None,
            "twitter_trends": None,
            "context_quality": 0
        }
        
        # Wetter verarbeiten
        if weather:
            processed["weather"] = {
                "temperature": weather.get("temperature"),
                "description": weather.get("description"),
                "formatted": f"{weather.get('temperature', '?')}°C, {weather.get('description', 'unbekannt')}"
            }
            processed["context_quality"] += 0.4
        
        # Crypto verarbeiten
        if crypto:
            processed["crypto"] = {
                "bitcoin_price": crypto.get("price"),
                "change_24h": crypto.get("change_24h"),
                "formatted": f"${crypto.get('price', 0):,.0f} ({crypto.get('change_24h', 0):+.1f}%)"
            }
            processed["context_quality"] += 0.3
        
        # Twitter Trends verarbeiten
        if twitter and len(twitter) > 0:
            # Extrahiere häufige Hashtags/Begriffe
            trends = self._extract_twitter_trends(twitter)
            processed["twitter_trends"] = trends
            processed["context_quality"] += 0.3
        
        return processed
    
    # Helper Methods
    
    def _calculate_priority_score(
        self, 
        news: Dict[str, Any], 
        categories: List[str], 
        sentiment: str, 
        is_local: bool
    ) -> float:
        """Berechnet Priority Score für News"""
        
        base_score = 5.0
        
        # Kategorie-Bonus
        for category in categories:
            base_score += self.config["category_priorities"].get(category, 0)
        
        # Sentiment-Gewichtung
        base_score *= self.config["sentiment_weights"].get(sentiment, 1.0)
        
        # Lokal-Bonus
        if is_local:
            base_score *= 1.3
        
        # Aktualitäts-Bonus
        hours_old = news.get("hours_old", 24)
        if hours_old < 1:
            base_score *= 1.5
        elif hours_old < 3:
            base_score *= 1.2
        
        # Source-Gewichtung
        source_weight = news.get("weight", 1.0)
        base_score *= source_weight
        
        return base_score
    
    def _estimate_sentiment(self, text: str) -> str:
        """Einfache Sentiment-Schätzung"""
        
        positive_words = ["gut", "erfolg", "gewinn", "positiv", "freude", "sieg"]
        negative_words = ["schlecht", "verlust", "negativ", "problem", "krise", "fehler"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _generate_content_hash(self, news: Dict[str, Any]) -> str:
        """Generiert Hash für Duplikat-Erkennung"""
        
        content = f"{news.get('title', '')}{news.get('summary', '')}"
        # Normalisiere Text
        content = re.sub(r'\s+', ' ', content.lower().strip())
        
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _is_spam_content(self, news: Dict[str, Any]) -> bool:
        """Erkennt Spam-Content"""
        
        title = news.get("title", "").lower()
        summary = news.get("summary", "").lower()
        
        spam_indicators = [
            "werbung", "anzeige", "sponsored", "promotion",
            "klicken sie hier", "jetzt kaufen", "gratis"
        ]
        
        return any(indicator in title or indicator in summary for indicator in spam_indicators)
    
    def _find_duplicates(self, news_list: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """Findet Duplikate in News-Liste"""
        
        duplicates = []
        hashes = {}
        
        for i, news in enumerate(news_list):
            content_hash = news.get("content_hash")
            if content_hash in hashes:
                duplicates.append((hashes[content_hash], i))
            else:
                hashes[content_hash] = i
        
        return duplicates
    
    def _analyze_sentiment_distribution(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert Sentiment-Verteilung"""
        
        sentiments = [news.get("sentiment", "neutral") for news in news_list]
        sentiment_counts = Counter(sentiments)
        total = len(sentiments)
        
        return {
            "positive": sentiment_counts.get("positive", 0),
            "neutral": sentiment_counts.get("neutral", 0),
            "negative": sentiment_counts.get("negative", 0),
            "positive_ratio": sentiment_counts.get("positive", 0) / total if total > 0 else 0,
            "negative_ratio": sentiment_counts.get("negative", 0) / total if total > 0 else 0
        }
    
    def _analyze_topic_distribution(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert Themen-Verteilung"""
        
        categories = [news.get("primary_category", "general") for news in news_list]
        category_counts = Counter(categories)
        
        return dict(category_counts)
    
    def _calculate_content_metrics(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Berechnet Content-Metriken"""
        
        if not news_list:
            return {"diversity_score": 0, "quality_score": 0, "local_ratio": 0}
        
        # Diversitäts-Score
        categories = [news.get("primary_category") for news in news_list]
        unique_categories = len(set(categories))
        diversity_score = unique_categories / len(news_list)
        
        # Qualitäts-Score (basierend auf Priority Scores)
        priority_scores = [news.get("priority_score", 0) for news in news_list]
        avg_quality = sum(priority_scores) / len(priority_scores) if priority_scores else 0
        quality_score = min(avg_quality / 10, 1.0)  # Normalisiert auf 0-1
        
        # Lokal-Anteil
        local_count = sum(1 for news in news_list if news.get("is_local", False))
        local_ratio = local_count / len(news_list)
        
        return {
            "diversity_score": diversity_score,
            "quality_score": quality_score,
            "local_ratio": local_ratio,
            "average_priority": avg_quality
        }
    
    def _assess_content_quality(
        self, 
        news_list: List[Dict[str, Any]], 
        context_data: Dict[str, Any]
    ) -> float:
        """Bewertet die Gesamtqualität des Contents"""
        
        if not news_list:
            return 0.0
        
        # News-Qualität (60%)
        news_metrics = self._calculate_content_metrics(news_list)
        news_quality = (
            news_metrics["diversity_score"] * 0.4 +
            news_metrics["quality_score"] * 0.4 +
            news_metrics["local_ratio"] * 0.2
        ) * 0.6
        
        # Kontext-Qualität (40%)
        context_quality = context_data.get("context_quality", 0) * 0.4
        
        return news_quality + context_quality
    
    def _extract_twitter_trends(self, tweets: List[Dict[str, Any]]) -> List[str]:
        """Extrahiert Trends aus Twitter-Daten"""
        
        # Einfache Hashtag-Extraktion
        hashtags = []
        for tweet in tweets:
            text = tweet.get("text", "")
            found_hashtags = re.findall(r'#\w+', text)
            hashtags.extend(found_hashtags)
        
        # Häufigste Hashtags
        hashtag_counts = Counter(hashtags)
        return [tag for tag, count in hashtag_counts.most_common(5)]
    
    async def _mark_news_as_used(self, news_list: List[Dict[str, Any]]) -> None:
        """Markiert News als verwendet in der Datenbank"""
        
        try:
            for news in news_list:
                used_news_data = {
                    "content_hash": news.get("content_hash"),
                    "title": news.get("title"),
                    "source": news.get("source"),
                    "used_at": datetime.now().isoformat(),
                    "category": news.get("primary_category")
                }
                
                self.supabase.client.table('used_news').insert(used_news_data).execute()
                
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim Markieren verwendeter News: {e}")
            # Nicht kritisch, daher nur Warning 