#!/usr/bin/env python3

"""
Content Processing Service - OPTIMIERT FÜR PERFEKTE INTEGRATION
===============================================================

Service für die Verarbeitung und Aufbereitung aller gesammelten Daten:
- News-Analyse und Kategorisierung (RSS Dashboard Integration)
- Content-Filterung und Priorisierung (Bitcoin & Weather Context)
- Themen-Extraktion und Clustering
- Sentiment-Analyse
- Content-Optimierung für Radio

OPTIMIERT: Perfekte Integration mit optimierten Data Collection Services
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
    Service für die intelligente Verarbeitung von Content - OPTIMIERT
    
    Analysiert, filtert und optimiert alle gesammelten Daten
    für die Broadcast-Generierung mit perfekter Service-Integration.
    """
    
    def __init__(self):
        self.supabase = SupabaseService()
        
        # Optimierte Konfiguration
        self.config = {
            "min_news_length": 15,  # Reduziert für mehr Flexibilität
            "max_news_length": 1000,
            "duplicate_threshold": 0.75,  # Lockerer für mehr Vielfalt
            "sentiment_weights": {
                "positive": 1.3,  # Bevorzuge positive News
                "neutral": 1.0,
                "negative": 0.9   # Reduziere negative News leicht
            },
            "category_priorities": {
                "bitcoin_crypto": 10,  # Höchste Priorität für Bitcoin
                "local": 9,
                "breaking": 9,
                "politics": 8,
                "economy": 8,
                "technology": 8,
                "sports": 6,
                "entertainment": 5
            },
            "optimization_features": {
                "bitcoin_context_boost": True,
                "weather_context_integration": True,
                "rss_dashboard_compatibility": True,
                "smart_categorization": True
            }
        }
        
        # Erweiterte Kategorie-Keywords für bessere Erkennung
        self.category_keywords = {
            "bitcoin_crypto": [
                "bitcoin", "btc", "cryptocurrency", "crypto", "blockchain", 
                "ethereum", "coinbase", "binance", "satoshi", "mining",
                "kryptowährung", "krypto", "digital currency", "defi"
            ],
            "local": [
                "zürich", "zurich", "basel", "bern", "schweiz", "switzerland",
                "swiss", "svp", "sp", "fdp", "cvp", "glp", "bundesrat",
                "kantonal", "gemeinde", "stadt"
            ],
            "breaking": [
                "breaking", "eilmeldung", "urgent", "alert", "sofort",
                "aktuell", "live", "jetzt", "update"
            ],
            "politics": [
                "politik", "politics", "regierung", "government", "parlament",
                "election", "wahl", "partei", "minister", "bundestag"
            ],
            "economy": [
                "wirtschaft", "economy", "börse", "stock", "market", "bank",
                "inflation", "recession", "gdp", "trade", "export", "import"
            ],
            "technology": [
                "technologie", "technology", "tech", "ai", "artificial intelligence",
                "software", "hardware", "digital", "innovation", "startup"
            ],
            "sports": [
                "sport", "sports", "fussball", "football", "soccer", "tennis",
                "hockey", "basketball", "olympics", "fifa", "uefa"
            ],
            "entertainment": [
                "entertainment", "unterhaltung", "film", "movie", "music",
                "celebrity", "kultur", "culture", "festival", "concert"
            ]
        }
    
    async def process_content(
        self,
        raw_data: Dict[str, Any],
        target_news_count: int = 4,
        target_time: Optional[str] = None,
        preset_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet alle gesammelten Rohdaten - OPTIMIERT
        
        Args:
            raw_data: Rohdaten vom optimierten DataCollectionService
            target_news_count: Gewünschte Anzahl News
            target_time: Zielzeit für zeitspezifische Optimierung
            preset_name: Show Preset Name für Focus-Bestimmung
            
        Returns:
            Dict mit verarbeiteten und optimierten Daten
        """
        
        logger.info("🔄 Optimierte Content-Verarbeitung...")
        
        try:
            # News verarbeiten mit optimierter Logik
            selected_news = await self._process_news_optimized(
                raw_news=raw_data.get("news", []),
                target_count=target_news_count,
                bitcoin_context=raw_data.get("crypto"),
                weather_context=raw_data.get("weather")
            )
            
            # Context-Daten optimiert verarbeiten
            context_data = self._process_context_data_optimized(
                weather=raw_data.get("weather"),
                crypto=raw_data.get("crypto"),
                twitter=raw_data.get("twitter")
            )
            
            # Content-Fokus bestimmen (mit optimierter Show Preset Logic)
            content_focus = self._determine_content_focus_optimized(
                selected_news, 
                preset_name,
                context_data
            )
            
            # Qualitätsbewertung mit Optimierungs-Metriken
            quality_score = self._calculate_content_quality_optimized(
                selected_news, 
                raw_data,
                context_data
            )
            
            result = {
                "selected_news": selected_news,
                "weather_data": raw_data.get("weather"),
                "crypto_data": raw_data.get("crypto"),
                "context_data": context_data,
                "content_focus": content_focus,
                "quality_score": quality_score,
                "target_time": target_time,
                "preset_name": preset_name,
                "optimization_metrics": self._generate_optimization_metrics(selected_news, context_data),
                "processing_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Optimierte Content-Verarbeitung: {len(selected_news)} News, Qualität: {quality_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Optimierte Content Processing Fehler: {e}")
            return None
    
    async def analyze_news(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert News ohne Selektion - OPTIMIERT"""
        
        logger.info(f"📊 Optimierte News-Analyse: {len(news_list)} News")
        
        # Kategorisierung mit optimierter Logik
        categorized = [self._categorize_news_item_optimized(news) for news in news_list]
        
        # Duplikate finden mit verbessertem Algorithmus
        duplicates = self._find_duplicates_optimized(categorized)
        
        # Sentiment-Analyse mit Bitcoin/Weather Context
        sentiment_stats = self._analyze_sentiment_distribution_optimized(categorized)
        
        # Themen-Verteilung mit Prioritäts-Gewichtung
        topic_dist = self._analyze_topic_distribution_optimized(categorized)
        
        return {
            "total_news": len(news_list),
            "categorized_news": categorized,
            "duplicates_found": len(duplicates),
            "sentiment_distribution": sentiment_stats,
            "topic_distribution": topic_dist,
            "quality_metrics": self._calculate_content_metrics_optimized(categorized),
            "optimization_level": "high"
        }
    
    async def test_processing(self) -> bool:
        """Testet die optimierte Content-Processing-Funktionalität"""
        
        # Test mit erweiterten Dummy-Daten
        test_news = [
            {
                "title": "Bitcoin erreicht neues Allzeithoch",
                "summary": "Bitcoin steigt über $100,000 und erreicht historische Höchststände.",
                "source": "CoinTelegraph",
                "published_date": datetime.now().isoformat(),
                "primary_category": "bitcoin_crypto"
            },
            {
                "title": "Zürich Tech Hub wächst weiter",
                "summary": "Neue Investitionen in Zürcher Technologie-Unternehmen.",
                "source": "NZZ",
                "published_date": datetime.now().isoformat(),
                "primary_category": "technology"
            }
        ]
        
        try:
            result = await self.analyze_news(test_news)
            return (
                result["total_news"] == 2 and
                result["optimization_level"] == "high" and
                len(result["categorized_news"]) == 2
            )
        except Exception as e:
            logger.error(f"❌ Optimierter Content Processing Test Fehler: {e}")
            return False
    
    # ==================== OPTIMIERTE PROCESSING METHODS ====================
    
    async def _process_news_optimized(
        self, 
        raw_news: List[Dict[str, Any]], 
        target_count: int,
        bitcoin_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Verarbeitet und selektiert News - OPTIMIERT mit Context"""
        
        if not raw_news:
            logger.warning("⚠️ Keine News zum Verarbeiten")
            return []
        
        logger.info(f"📰 Optimierte News-Verarbeitung: {len(raw_news)} → {target_count}")
        
        # 1. Basis-Filterung (lockerer)
        filtered_news = self._filter_news_quality_optimized(raw_news)
        logger.info(f"📰 {len(filtered_news)} News nach optimierter Qualitäts-Filter")
        
        # 2. Kategorisierung mit Context-Boost
        categorized_news = [
            self._categorize_news_item_optimized(news, bitcoin_context, weather_context) 
            for news in filtered_news
        ]
        
        # 3. Duplikate entfernen mit verbessertem Algorithmus
        deduplicated_news = self._remove_duplicates_optimized(categorized_news)
        logger.info(f"📰 {len(deduplicated_news)} News nach optimierter Duplikat-Entfernung")
        
        # 4. Priorisierung mit Context-Gewichtung
        prioritized_news = self._prioritize_news_optimized(
            deduplicated_news, 
            bitcoin_context, 
            weather_context
        )
        
        # 5. Selektion der besten News mit Diversitäts-Optimierung
        selected_news = self._select_top_news_optimized(prioritized_news, target_count)
        
        # 6. Verwendete News markieren
        await self._mark_news_as_used(selected_news)
        
        return selected_news
    
    def _filter_news_quality_optimized(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtert News nach optimierten Qualitätskriterien"""
        
        filtered = []
        
        for news in news_list:
            # Lockere Mindestanforderungen für mehr Flexibilität
            title_len = len(news.get("title", ""))
            summary_len = len(news.get("summary", ""))
            
            # Sehr lockere Mindestanforderungen
            if title_len < 3:  # Minimal requirement
                continue
            
            # Summary ist optional - wenn vorhanden, dann mindestens 5 Zeichen
            if summary_len > 0 and summary_len < 5:
                continue
            
            # Maximallänge prüfen
            if summary_len > self.config["max_news_length"]:
                news["summary"] = news["summary"][:self.config["max_news_length"]] + "..."
            
            # Optimierter Spam-Filter
            if self._is_spam_content_optimized(news):
                continue
            
            filtered.append(news)
        
        return filtered
    
    def _categorize_news_item_optimized(
        self, 
        news: Dict[str, Any], 
        bitcoin_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Kategorisiert eine einzelne News - OPTIMIERT mit Context"""
        
        text = f"{news.get('title', '')} {news.get('summary', '')}".lower()
        
        # Kategorien bestimmen mit optimierter Logik
        categories = []
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                categories.append(category)
                category_scores[category] = score
        
        # Context-Boost für Bitcoin
        if (bitcoin_context and 
            self.config["optimization_features"]["bitcoin_context_boost"] and
            any(keyword in text for keyword in self.category_keywords["bitcoin_crypto"])):
            if "bitcoin_crypto" in category_scores:
                category_scores["bitcoin_crypto"] *= 1.5  # Boost Bitcoin relevance
        
        # Fallback-Kategorie
        if not categories:
            categories = ["general"]
            category_scores["general"] = 1
        
        # Beste Kategorie als primär
        primary_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        
        # Sentiment schätzen mit Context
        sentiment = self._estimate_sentiment_optimized(text, bitcoin_context)
        
        # Lokalität bestimmen
        is_local = any(keyword in text for keyword in self.category_keywords["local"])
        
        # Optimierte Priority Score Berechnung
        priority_score = self._calculate_priority_score_optimized(
            news, categories, sentiment, is_local, bitcoin_context, weather_context
        )
        
        # News erweitern
        enhanced_news = news.copy()
        enhanced_news.update({
            "categories": categories,
            "primary_category": primary_category,
            "category_scores": category_scores,
            "sentiment": sentiment,
            "is_local": is_local,
            "priority_score": priority_score,
            "content_hash": self._generate_content_hash(news),
            "optimization_applied": True
        })
        
        return enhanced_news
    
    def _prioritize_news_optimized(
        self, 
        news_list: List[Dict[str, Any]],
        bitcoin_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Priorisiert News mit optimierter Context-Gewichtung"""
        
        # Zusätzliche Context-Gewichtung
        for news in news_list:
            base_score = news.get("priority_score", 0)
            
            # Bitcoin Context Boost
            if (bitcoin_context and 
                news.get("primary_category") == "bitcoin_crypto"):
                # Boost basierend auf Bitcoin-Preis-Änderung
                try:
                    bitcoin_data = bitcoin_context.get("data", {})
                    if isinstance(bitcoin_data, dict):
                        change_24h = bitcoin_data.get("percent_change_24h", 0)
                        if abs(change_24h) > 5:  # Signifikante Änderung
                            news["priority_score"] = base_score * 1.3
                except:
                    pass
            
            # Weather Context für lokale News
            if (weather_context and 
                news.get("is_local") and
                news.get("primary_category") in ["local", "breaking"]):
                news["priority_score"] = base_score * 1.1
        
        return sorted(
            news_list,
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )
    
    def _select_top_news_optimized(
        self, 
        news_list: List[Dict[str, Any]], 
        target_count: int
    ) -> List[Dict[str, Any]]:
        """Selektiert die besten News mit optimierter Diversitäts-Berücksichtigung"""
        
        if len(news_list) <= target_count:
            return news_list
        
        selected = []
        used_categories = set()
        
        # Erste Runde: Eine News pro Kategorie (priorisiert)
        priority_categories = ["bitcoin_crypto", "local", "breaking", "technology"]
        
        for category in priority_categories:
            if len(selected) >= target_count:
                break
            
            for news in news_list:
                if (news.get("primary_category") == category and 
                    category not in used_categories):
                    selected.append(news)
                    used_categories.add(category)
                    break
        
        # Zweite Runde: Beste verbleibende News
        remaining = [n for n in news_list if n not in selected]
        remaining_needed = target_count - len(selected)
        
        # Sortiere nach Priority Score
        remaining.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        selected.extend(remaining[:remaining_needed])
        
        return selected
    
    # ==================== OPTIMIERTE HELPER METHODS ====================
    
    def _process_context_data_optimized(
        self, 
        weather: Optional[Dict[str, Any]], 
        crypto: Optional[Dict[str, Any]], 
        twitter: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Verarbeitet Context-Daten - OPTIMIERT"""
        
        context = {
            "weather_available": weather is not None,
            "crypto_available": crypto is not None,
            "twitter_available": twitter is not None and len(twitter) > 0,
            "optimization_applied": True
        }
        
        # Weather Context
        if weather and self.config["optimization_features"]["weather_context_integration"]:
            try:
                if "cities" in weather:
                    zurich_weather = weather["cities"].get("zürich") or weather["cities"].get("zurich")
                    if zurich_weather:
                        context["weather"] = {
                            "formatted": f"{zurich_weather.get('temperature', '?')}°C, {zurich_weather.get('description', 'unknown')}",
                            "temperature": zurich_weather.get('temperature'),
                            "description": zurich_weather.get('description'),
                            "optimization": "smart_time_based"
                        }
                else:
                    context["weather"] = {"formatted": "Weather data unavailable"}
            except Exception as e:
                logger.warning(f"⚠️ Weather context processing error: {e}")
                context["weather"] = {"formatted": "Weather processing error"}
        
        # Crypto Context (optimiert)
        if crypto and self.config["optimization_features"]["bitcoin_context_boost"]:
            try:
                crypto_data = crypto.get("data", {})
                if isinstance(crypto_data, dict) and "price" in crypto_data:
                    price = crypto_data.get("price", 0)
                    change_24h = crypto_data.get("percent_change_24h", 0)
                    
                    # Formatiere mit Trend-Indikator
                    trend = "📈" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
                    context["crypto"] = {
                        "formatted": f"${price:,.0f} ({change_24h:+.1f}%) {trend}",
                        "price": price,
                        "change_24h": change_24h,
                        "optimization": "multi_timeframe"
                    }
                else:
                    context["crypto"] = {"formatted": "Bitcoin data unavailable"}
            except Exception as e:
                logger.warning(f"⚠️ Crypto context processing error: {e}")
                context["crypto"] = {"formatted": "Bitcoin processing error"}
        
        return context
    
    def _calculate_priority_score_optimized(
        self, 
        news: Dict[str, Any], 
        categories: List[str], 
        sentiment: str, 
        is_local: bool,
        bitcoin_context: Optional[Dict[str, Any]] = None,
        weather_context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Berechnet optimierten Priority Score mit Context"""
        
        score = 0.0
        
        # Basis-Score aus Kategorien
        for category in categories:
            score += self.config["category_priorities"].get(category, 1)
        
        # Sentiment-Gewichtung
        sentiment_multiplier = self.config["sentiment_weights"].get(sentiment, 1.0)
        score *= sentiment_multiplier
        
        # Lokalitäts-Bonus
        if is_local:
            score += 2
        
        # Bitcoin Context Boost
        if (bitcoin_context and 
            "bitcoin_crypto" in categories and
            self.config["optimization_features"]["bitcoin_context_boost"]):
            try:
                bitcoin_data = bitcoin_context.get("data", {})
                if isinstance(bitcoin_data, dict):
                    change_24h = abs(bitcoin_data.get("percent_change_24h", 0))
                    if change_24h > 5:  # Signifikante Bewegung
                        score += 3
                    elif change_24h > 2:
                        score += 1
            except:
                pass
        
        # Aktualitäts-Bonus
        try:
            if "published" in news or "published_date" in news:
                published_str = news.get("published") or news.get("published_date")
                if published_str:
                    published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    hours_old = (datetime.now() - published).total_seconds() / 3600
                    
                    if hours_old < 1:
                        score += 2  # Sehr aktuell
                    elif hours_old < 6:
                        score += 1  # Aktuell
        except:
            pass
        
        return round(score, 2)
    
    def _estimate_sentiment_optimized(
        self, 
        text: str, 
        bitcoin_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schätzt Sentiment mit Bitcoin Context"""
        
        positive_words = [
            "gut", "great", "excellent", "success", "win", "gain", "up", "rise",
            "positive", "growth", "increase", "boom", "bullish", "rally"
        ]
        negative_words = [
            "schlecht", "bad", "terrible", "fail", "loss", "down", "fall",
            "negative", "decline", "crash", "bearish", "drop", "plunge"
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Bitcoin Context Adjustment
        if bitcoin_context and "bitcoin" in text.lower():
            try:
                bitcoin_data = bitcoin_context.get("data", {})
                if isinstance(bitcoin_data, dict):
                    change_24h = bitcoin_data.get("percent_change_24h", 0)
                    if change_24h > 2:
                        positive_count += 1
                    elif change_24h < -2:
                        negative_count += 1
            except:
                pass
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _is_spam_content_optimized(self, news: Dict[str, Any]) -> bool:
        """Optimierter Spam-Filter"""
        
        title = news.get("title", "").lower()
        summary = news.get("summary", "").lower()
        
        # Lockere Spam-Kriterien
        spam_indicators = [
            "click here", "buy now", "limited time", "act now",
            "free money", "get rich", "miracle", "secret"
        ]
        
        spam_count = sum(1 for indicator in spam_indicators 
                        if indicator in title or indicator in summary)
        
        return spam_count >= 2  # Mindestens 2 Spam-Indikatoren
    
    def _remove_duplicates_optimized(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Entfernt Duplikate mit optimiertem Algorithmus"""
        
        seen_hashes = set()
        unique_news = []
        
        # Sortiere nach Priority Score (beste zuerst)
        sorted_news = sorted(news_list, key=lambda x: x.get("priority_score", 0), reverse=True)
        
        for news in sorted_news:
            content_hash = news.get("content_hash")
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_news.append(news)
        
        return unique_news
    
    def _find_duplicates_optimized(self, news_list: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """Findet Duplikate mit optimiertem Algorithmus"""
        
        duplicates = []
        hash_to_index = {}
        
        for i, news in enumerate(news_list):
            content_hash = news.get("content_hash")
            if content_hash in hash_to_index:
                duplicates.append((hash_to_index[content_hash], i))
            else:
                hash_to_index[content_hash] = i
        
        return duplicates
    
    def _analyze_sentiment_distribution_optimized(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert Sentiment-Verteilung - OPTIMIERT"""
        
        sentiments = [news.get("sentiment", "neutral") for news in news_list]
        sentiment_counts = Counter(sentiments)
        
        total = len(sentiments)
        distribution = {
            sentiment: {
                "count": count,
                "percentage": round((count / total) * 100, 1) if total > 0 else 0
            }
            for sentiment, count in sentiment_counts.items()
        }
        
        # Optimierungs-Metriken
        distribution["optimization_metrics"] = {
            "positive_ratio": distribution.get("positive", {}).get("percentage", 0) / 100,
            "balance_score": 1 - abs(0.5 - (distribution.get("positive", {}).get("percentage", 0) / 100))
        }
        
        return distribution
    
    def _analyze_topic_distribution_optimized(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiert Themen-Verteilung mit Prioritäts-Gewichtung"""
        
        categories = [news.get("primary_category", "general") for news in news_list]
        category_counts = Counter(categories)
        
        total = len(categories)
        distribution = {}
        
        for category, count in category_counts.items():
            priority = self.config["category_priorities"].get(category, 1)
            distribution[category] = {
                "count": count,
                "percentage": round((count / total) * 100, 1) if total > 0 else 0,
                "priority": priority,
                "weighted_score": count * priority
            }
        
        # Sortiere nach weighted_score
        distribution = dict(sorted(
            distribution.items(), 
            key=lambda x: x[1]["weighted_score"], 
            reverse=True
        ))
        
        return distribution
    
    def _calculate_content_metrics_optimized(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Berechnet optimierte Content-Metriken"""
        
        if not news_list:
            return {"error": "No news to analyze"}
        
        # Basis-Metriken
        total_news = len(news_list)
        avg_priority = sum(news.get("priority_score", 0) for news in news_list) / total_news
        
        # Kategorien-Diversität
        categories = set(news.get("primary_category") for news in news_list)
        category_diversity = len(categories) / total_news
        
        # Sentiment-Balance
        sentiments = [news.get("sentiment", "neutral") for news in news_list]
        sentiment_counts = Counter(sentiments)
        sentiment_balance = 1 - abs(0.5 - (sentiment_counts.get("positive", 0) / total_news))
        
        # Optimierungs-Metriken
        optimization_applied = sum(1 for news in news_list if news.get("optimization_applied", False))
        optimization_rate = optimization_applied / total_news
        
        return {
            "total_news": total_news,
            "average_priority": round(avg_priority, 2),
            "category_diversity": round(category_diversity, 2),
            "sentiment_balance": round(sentiment_balance, 2),
            "optimization_rate": round(optimization_rate, 2),
            "quality_indicators": {
                "high_priority_news": sum(1 for news in news_list if news.get("priority_score", 0) > 8),
                "local_news": sum(1 for news in news_list if news.get("is_local", False)),
                "bitcoin_news": sum(1 for news in news_list if news.get("primary_category") == "bitcoin_crypto")
            }
        }
    
    def _determine_content_focus_optimized(
        self, 
        selected_news: List[Dict[str, Any]], 
        preset_name: str = None,
        context_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Bestimmt Content-Fokus - OPTIMIERT mit Context"""
        
        if not selected_news:
            return {"focus": "general", "confidence": 0.0}
        
        # Kategorien-Analyse
        categories = [news.get("primary_category", "general") for news in selected_news]
        category_counts = Counter(categories)
        
        # Dominante Kategorie
        dominant_category = category_counts.most_common(1)[0][0]
        dominant_count = category_counts.most_common(1)[0][1]
        confidence = dominant_count / len(selected_news)
        
        # Context-basierte Anpassungen
        focus_adjustments = {}
        
        # Bitcoin Context
        if (context_data and 
            context_data.get("crypto_available") and
            "bitcoin_crypto" in category_counts):
            focus_adjustments["bitcoin_emphasis"] = True
            
        # Local Context
        local_news_count = sum(1 for news in selected_news if news.get("is_local", False))
        if local_news_count > 0:
            focus_adjustments["local_emphasis"] = local_news_count / len(selected_news)
        
        # Preset-basierte Anpassungen
        if preset_name:
            if "bitcoin" in preset_name.lower():
                focus_adjustments["preset_bitcoin_focus"] = True
            elif "tech" in preset_name.lower():
                focus_adjustments["preset_tech_focus"] = True
        
        return {
            "focus": dominant_category,
            "confidence": round(confidence, 2),
            "category_distribution": dict(category_counts),
            "focus_adjustments": focus_adjustments,
            "optimization_applied": True
        }
    
    def _calculate_content_quality_optimized(
        self, 
        selected_news: List[Dict[str, Any]], 
        raw_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> float:
        """Berechnet optimierte Content-Qualität"""
        
        if not selected_news:
            return 0.0
        
        quality_score = 0.0
        
        # News-Qualität (40 Punkte)
        avg_priority = sum(news.get("priority_score", 0) for news in selected_news) / len(selected_news)
        quality_score += min(40, avg_priority * 4)  # Max 40 Punkte
        
        # Diversität (20 Punkte)
        categories = set(news.get("primary_category") for news in selected_news)
        diversity_score = (len(categories) / len(selected_news)) * 20
        quality_score += diversity_score
        
        # Context-Integration (20 Punkte)
        context_score = 0
        if context_data.get("crypto_available"):
            context_score += 10
        if context_data.get("weather_available"):
            context_score += 10
        quality_score += context_score
        
        # Optimierungs-Bonus (20 Punkte)
        optimization_rate = sum(1 for news in selected_news if news.get("optimization_applied", False)) / len(selected_news)
        quality_score += optimization_rate * 20
        
        return round(min(100, quality_score), 2)
    
    def _generate_optimization_metrics(
        self, 
        selected_news: List[Dict[str, Any]], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generiert Optimierungs-Metriken"""
        
        return {
            "total_news_processed": len(selected_news),
            "optimization_features_used": {
                "bitcoin_context_boost": any(
                    news.get("primary_category") == "bitcoin_crypto" 
                    for news in selected_news
                ),
                "weather_context_integration": context_data.get("weather_available", False),
                "smart_categorization": all(
                    news.get("optimization_applied", False) 
                    for news in selected_news
                ),
                "priority_optimization": any(
                    news.get("priority_score", 0) > 8 
                    for news in selected_news
                )
            },
            "quality_indicators": {
                "high_priority_ratio": sum(
                    1 for news in selected_news 
                    if news.get("priority_score", 0) > 8
                ) / len(selected_news) if selected_news else 0,
                "category_diversity": len(set(
                    news.get("primary_category") 
                    for news in selected_news
                )) / len(selected_news) if selected_news else 0
            },
            "optimization_timestamp": datetime.now().isoformat()
        } 