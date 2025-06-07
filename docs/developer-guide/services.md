# 🔧 Service Documentation

<div align="center">

![Developer Guide](https://img.shields.io/badge/guide-developer-purple)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-25%20min-orange)

**⚙️ Complete guide to RadioX microservices architecture**

[🏠 Documentation](../) • [👨‍💻 Developer Guides](../README.md#-developer-guides) • [🏗️ Architecture](architecture.md) • [🔧 Development](development.md)

</div>

---

## 🎯 Overview

RadioX implements a **microservices architecture** with specialized services for data collection, content processing, and media generation. Each service is designed for **independence**, **scalability**, and **maintainability**.

### ✨ **Service Principles**
- 🔄 **Single Responsibility** - Each service has one clear purpose
- 🔗 **Loose Coupling** - Minimal dependencies between services
- 📦 **High Cohesion** - Related functionality grouped together
- 🚀 **Production Ready** - Enterprise-grade error handling and logging

---

## 💰 Bitcoin Service

### **🎯 Purpose**
Provides real-time Bitcoin price data, market analysis, and radio-ready announcements using CoinMarketCap API.

### **📁 Files**
- `src/services/bitcoin_service.py` - Core service implementation
- `cli/cli_bitcoin.py` - CLI testing interface

### **🔧 Configuration**
```bash
# .env file
COINMARKETCAP_API_KEY=your_api_key_here
```

### **📊 Features**
- ✅ **Real-time Bitcoin Price** - Current USD price with high precision
- ✅ **Multi-timeframe Changes** - 1h, 24h, 7d, 30d, 60d, 90d percentage changes
- ✅ **Market Data** - Market cap, 24h volume, circulating supply
- ✅ **Trend Analysis** - Intelligent trend detection and descriptions
- ✅ **Radio Announcements** - Professional, time-aware announcements
- ✅ **Caching System** - 5-minute cache to optimize API calls
- ✅ **Error Handling** - Graceful fallbacks and comprehensive logging

### **🏗️ Architecture**

```python
class BitcoinService:
    def __init__(self):
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    async def get_bitcoin_data(self) -> Dict[str, Any]
    async def get_radio_announcement(self, time_period: str = "24h") -> str
    def _analyze_trend(self, change_24h: float, change_7d: float) -> str
    def _format_large_number(self, number: float) -> str
```

### **📡 API Reference**

#### **get_bitcoin_data()**
Returns comprehensive Bitcoin market data.

**Returns:**
```python
{
    "price": 105503.45,
    "changes": {
        "1h": 0.2,
        "24h": 0.6,
        "7d": -2.1,
        "30d": 15.8,
        "60d": 45.2,
        "90d": 78.9
    },
    "market_cap": 2087234567890.12,
    "volume_24h": 45678901234.56,
    "circulating_supply": 19789456.78,
    "last_updated": "2024-12-19T10:30:00Z",
    "trend": "slightly_up",
    "trend_description": "showing modest gains"
}
```

#### **get_radio_announcement(time_period)**
Generates professional radio announcement.

**Parameters:**
- `time_period` (str): "1h", "24h", "7d", "30d", "60d", "90d"

**Returns:**
```python
"Bitcoin is trading at 105,503 dollars and is up 0.6 percent in the last 24 hours, showing modest gains with a market cap of 2.09 trillion dollars."
```

### **🎙️ Radio Announcement Examples**

```python
# Positive trend (24h)
"Bitcoin is trading at 105,503 dollars and is up 0.6 percent in the last 24 hours, showing modest gains with a market cap of 2.09 trillion dollars."

# Negative trend (7d)
"Bitcoin is trading at 98,234 dollars and is down 2.1 percent over the last 7 days, experiencing some volatility with a market cap of 1.94 trillion dollars."

# Strong positive (30d)
"Bitcoin is trading at 112,890 dollars and is up 15.8 percent over the last 30 days, showing strong bullish momentum with a market cap of 2.23 trillion dollars."
```

### **🔄 Trend Analysis Logic**

```python
def _analyze_trend(self, change_24h: float, change_7d: float) -> Tuple[str, str]:
    """Intelligent trend analysis based on multiple timeframes"""
    
    if change_24h > 5:
        return "strongly_up", "surging with strong bullish momentum"
    elif change_24h > 2:
        return "up", "showing solid gains"
    elif change_24h > 0:
        return "slightly_up", "showing modest gains"
    elif change_24h > -2:
        return "slightly_down", "experiencing minor declines"
    elif change_24h > -5:
        return "down", "facing selling pressure"
    else:
        return "strongly_down", "under significant bearish pressure"
```

### **🧪 CLI Usage**

```bash
# Basic test (default 24h timeframe)
python cli_bitcoin.py

# Specific timeframe
python cli_bitcoin.py --timeframe 7d

# Output example:
💰 BITCOIN SERVICE
📈 PRICE: $105,503.45 (+0.6% 24h, -2.1% 7d)
📊 MARKET: $2.09T cap, $45.68B volume
🕐 UPDATED: 2024-12-19 10:30:00 UTC
✅ API: Connected, ⚡ CACHE: Active (3m remaining)
📈 TREND: Slightly up - showing modest gains
🎙️ RADIO: Bitcoin is trading at 105,503 dollars...
```

---

## 🌤️ Weather Service

### **🎯 Purpose**
Provides current weather conditions and intelligent forecasts for Swiss cities using OpenWeatherMap API with smart time-based outlook logic.

### **📁 Files**
- `src/services/weather_service.py` - Core service implementation
- `cli/cli_weather.py` - CLI testing interface

### **🔧 Configuration**
```bash
# .env file
OPENWEATHERMAP_API_KEY=your_api_key_here
```

### **📊 Features**
- ✅ **Multi-city Support** - All major Swiss cities (Zürich, Basel, Geneva, Bern, Lausanne, Winterthur, Lucerne, St. Gallen)
- ✅ **Current Weather** - Temperature, conditions, humidity, wind speed
- ✅ **Smart Outlook** - Time-aware forecasting logic
- ✅ **5-day Forecast** - Extended weather predictions
- ✅ **Radio Announcements** - Professional weather reports
- ✅ **Precipitation Probability** - Rain/snow likelihood
- ✅ **Emoji Integration** - Visual weather representation

### **🏗️ Architecture**

```python
class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.swiss_cities = [
            "Zürich", "Basel", "Geneva", "Bern", 
            "Lausanne", "Winterthur", "Lucerne", "St. Gallen"
        ]
    
    async def get_current_weather(self, city: str = "Zürich") -> Dict[str, Any]
    async def get_smart_outlook(self, city: str = "Zürich") -> Dict[str, Any]
    async def get_5day_forecast(self, city: str = "Zürich") -> List[Dict[str, Any]]
    async def get_radio_announcement(self, city: str = "Zürich") -> str
```

### **📡 API Reference**

#### **get_current_weather(city)**
Returns current weather conditions for specified city.

**Parameters:**
- `city` (str): Swiss city name (default: "Zürich")

**Returns:**
```python
{
    "city": "Zürich",
    "temperature": 15.6,
    "feels_like": 14.2,
    "humidity": 88,
    "wind_speed": 4.8,
    "wind_direction": 240,
    "description": "Heavy Rain",
    "emoji": "🌧️",
    "pressure": 1013.2,
    "visibility": 8.5,
    "timestamp": "2024-12-19T20:00:00Z"
}
```

#### **get_smart_outlook(city)**
Provides intelligent time-based weather outlook.

**Smart Logic:**
- **00:00-18:00**: Next 2 hours forecast with precipitation probability
- **18:00-23:59**: Current weather + tomorrow forecast

**Returns:**
```python
{
    "type": "next_hours",  # or "tomorrow"
    "time": "20:00",
    "temperature": 16.9,
    "description": "Light Rain",
    "precipitation_probability": 100,
    "announcement": "Weather outlook for Zürich - next few hours: Light rain expected around 20:00 with temperatures around 17 degrees and 100 percent chance of rain."
}
```

#### **get_5day_forecast(city)**
Returns 5-day weather forecast with daily summaries.

**Returns:**
```python
[
    {
        "date": "2024-12-20",
        "day": "Friday",
        "temp_min": 12.3,
        "temp_max": 18.7,
        "description": "Partly Cloudy",
        "emoji": "⛅",
        "precipitation_probability": 20,
        "humidity": 65,
        "wind_speed": 3.2
    },
    # ... 4 more days
]
```

### **🧠 Smart Outlook Logic**

```python
async def get_smart_outlook(self, city: str = "Zürich") -> Dict[str, Any]:
    """Time-aware weather outlook logic"""
    
    current_hour = datetime.now().hour
    
    if 0 <= current_hour < 18:
        # Morning/Afternoon: Next 2 hours forecast
        forecast = await self._get_hourly_forecast(city, hours=2)
        return {
            "type": "next_hours",
            "time": forecast["time"],
            "temperature": forecast["temperature"],
            "description": forecast["description"],
            "precipitation_probability": forecast["precipitation_probability"],
            "announcement": f"Weather outlook for {city} - next few hours: {forecast['description']} expected around {forecast['time']} with temperatures around {forecast['temperature']:.0f} degrees and {forecast['precipitation_probability']} percent chance of rain."
        }
    else:
        # Evening/Night: Tomorrow forecast
        tomorrow = await self._get_tomorrow_forecast(city)
        return {
            "type": "tomorrow",
            "date": tomorrow["date"],
            "temp_min": tomorrow["temp_min"],
            "temp_max": tomorrow["temp_max"],
            "description": tomorrow["description"],
            "announcement": f"Weather outlook for {city} - tomorrow: {tomorrow['description']} with temperatures between {tomorrow['temp_min']:.0f} and {tomorrow['temp_max']:.0f} degrees."
        }
```

### **🎙️ Radio Announcement Examples**

```python
# Morning/Afternoon (Next 2 hours)
"Weather outlook for Zürich - next few hours: Light rain expected around 20:00 with temperatures around 17 degrees and 100 percent chance of rain."

# Evening/Night (Tomorrow)
"Weather outlook for Zürich - tomorrow: Partly cloudy with temperatures between 12 and 19 degrees."

# Current weather
"Current weather in Zürich: 16 degrees with heavy rain, humidity at 88 percent and wind at 5 kilometers per hour."
```

### **🌍 Supported Swiss Cities**

| 🏙️ City | 🗺️ Region | 📍 Coordinates |
|----------|-----------|----------------|
| **Zürich** | German-speaking | 47.3769°N, 8.5417°E |
| **Basel** | German-speaking | 47.5596°N, 7.5886°E |
| **Geneva** | French-speaking | 46.2044°N, 6.1432°E |
| **Bern** | German-speaking | 46.9481°N, 7.4474°E |
| **Lausanne** | French-speaking | 46.5197°N, 6.6323°E |
| **Winterthur** | German-speaking | 47.5034°N, 8.7240°E |
| **Lucerne** | German-speaking | 47.0502°N, 8.3093°E |
| **St. Gallen** | German-speaking | 47.4245°N, 9.3767°E |

### **🧪 CLI Usage**

```bash
# Basic test (Zürich, current + smart outlook)
python cli_weather.py

# Specific city
python cli_weather.py --city Basel

# All cities overview
python cli_weather.py --all-cities

# Output example:
🌤️ WEATHER SERVICE
🌡️ CURRENT: 15.6°C - Heavy Rain, 💨 4.8 km/h, 💧 88%
🕐 OUTLOOK: 20:00: 16.9°C - Light Rain, 100% rain
🎙️ RADIO: Weather outlook for Zürich - next few hours...
```

---

## 📰 RSS Service

### **🎯 Purpose**
Comprehensive RSS feed management and news aggregation system with professional HTML dashboard, real-time filtering, and intelligent content processing.

### **📁 Files**
- `src/services/rss_service.py` - Core RSS service implementation
- `cli/cli_rss.py` - CLI interface with HTML dashboard generation

### **🔧 Configuration**
```bash
# Database connection via Supabase
# RSS feeds managed in rss_feed_preferences table
```

### **📊 Features**
- ✅ **30+ RSS Feeds** - Swiss & international news sources
- ✅ **11 Active Sources** - NZZ, 20min, Heise, SRF, Tagesanzeiger, etc.
- ✅ **Professional Dashboard** - Modern HTML interface with tables
- ✅ **Live Filtering** - Category-based filtering with JavaScript
- ✅ **Smart Sorting** - Latest, Priority, Source, Category sorting
- ✅ **Dual Links** - Article links + RSS feed links in each row
- ✅ **Real-time Analytics** - 98+ articles with live statistics
- ✅ **Category Management** - 12 categories (news, wirtschaft, zurich, tech, etc.)
- ✅ **Duplicate Removal** - 80% similarity threshold for clean results
- ✅ **Enterprise Design** - Professional blue/gray color scheme

### **🏗️ Architecture**

```python
class RSSService:
    def __init__(self):
        self._supabase = None  # Lazy loading
    
    async def get_all_active_feeds(self) -> List[Dict[str, Any]]
    async def get_all_recent_news(self, max_age_hours: int = 12) -> List[RSSNewsItem]
    async def _fetch_feed(self, url: str, source: str, category: str, ...) -> List[RSSNewsItem]
    def _parse_feed_content(self, content: str, ...) -> List[RSSNewsItem]
    def _remove_duplicates(self, news_items: List[RSSNewsItem]) -> List[RSSNewsItem]
```

### **📡 API Reference**

#### **get_all_active_feeds()**
Returns all active RSS feed configurations from database.

**Returns:**
```python
[
    {
        "id": "nzz_zurich",
        "source_name": "nzz",
        "feed_category": "zurich", 
        "feed_url": "https://www.nzz.ch/zuerich.rss",
        "priority": 10,
        "weight": 3.0,
        "is_active": True
    },
    # ... 29 more feeds
]
```

#### **get_all_recent_news(max_age_hours)**
Collects recent news from ALL active feeds.

**Parameters:**
- `max_age_hours` (int): Maximum age of articles in hours (default: 12)

**Returns:**
```python
[
    RSSNewsItem(
        title="Kampfjets fangen Hobbypilot ab",
        summary="Ein E-Flugzeug wurde von Kampfjets abgefangen...",
        link="https://www.20min.ch/story/...",
        published=datetime(2024, 12, 19, 14, 30),
        source="20min",
        category="zurich",
        priority=10,
        weight=2.5
    ),
    # ... 97 more articles
]
```

### **🎨 HTML Dashboard Features**

#### **📊 Professional Design**
- **Modern Business Colors** - Blue (#3498db), Gray (#2c3e50), Orange (#e67e22)
- **Responsive Tables** - Works on desktop and mobile
- **Sticky Headers** - Column headers stay visible while scrolling
- **Hover Effects** - Interactive row highlighting

#### **🏷️ Live Filtering System**
```javascript
// Category filter tags
<a href="#" class="filter-tag active" data-category="all">All</a>
<a href="#" class="filter-tag" data-category="news">news (24)</a>
<a href="#" class="filter-tag" data-category="wirtschaft">wirtschaft (22)</a>
<a href="#" class="filter-tag" data-category="zurich">zurich (13)</a>
// ... more categories

// JavaScript event listeners
filterTags.forEach(tag => {
    tag.addEventListener('click', function(e) {
        e.preventDefault();
        filterByCategory(this.dataset.category);
    });
});
```

#### **🔄 Smart Sorting Options**
- **Latest First** - Newest articles at top (default)
- **Oldest First** - Historical articles first
- **Priority High→Low** - P10, P9, P8 priority sorting
- **Source A→Z** - Alphabetical by news source
- **Category A→Z** - Alphabetical by category

#### **🔗 Dual Link System**
Each table row contains both:
```html
<div class="link-group">
    <a href="article_url" class="external-link">📰 Article</a>
    <a href="rss_feed_url" class="rss-link">📡 RSS Feed</a>
</div>
```

### **📈 Current Statistics**
- **30 Total Feeds** configured in database
- **98 Articles** collected in last 12 hours
- **11 Active Sources** providing content
- **12 Categories** with balanced distribution

### **📊 Category Distribution**
```
news: 24 articles          wirtschaft: 22 articles
zurich: 13 articles         tech: 11 articles  
schweiz: 8 articles         international: 8 articles
crypto: 4 articles          bitcoin: 3 articles
weather: 2 articles         latest: 1 article
science: 1 article          lifestyle: 1 article
```

### **🏢 Active News Sources**
```
📰 nzz: P10, W3.0 (zurich, schweiz, wirtschaft, international)
📰 20min: P10, W0.8 (weather, zurich, schweiz, wirtschaft, crypto, science, tech, lifestyle)  
📰 heise: P9, W1.5 (news, tech)
📰 srf: P9, W2.0 (news, schweiz, international, wirtschaft)
📰 tagesanzeiger: P8, W3.0 (zurich, schweiz, wirtschaft)
📰 cointelegraph: P8, W2.0 (bitcoin, crypto)
📰 cash: P7, W1.5 (wirtschaft)
📰 techcrunch: P7, W1.3 (latest)
📰 bbc: P7, W1.5 (tech, wirtschaft, international)
📰 theverge: P6, W1.2 (tech)
📰 rt: P6, W1.0 (international)
```

### **🧪 CLI Usage**

```bash
# Basic RSS collection and dashboard
python cli_rss.py

# Limit CLI output, generate full dashboard
python cli_rss.py --limit 5

# Custom time range
python cli_rss.py --hours 24

# Skip HTML generation
python cli_rss.py --no-html

# Output example:
📰 RSS SERVICE
==============================
📡 FEEDS: 30 total configured
📰 NEWS: 98 articles collected (12h)
🔗 SOURCES: 11 active

🎯 TOP 5 NEWS:
 1. [zurich] Kampfjets fangen Hobbypilot ab...
    📰 20min | ⏰ 5h | 🎯 P10 | ⚖️ W2.5
 2. [news] Diese Juni-Regenwetterquiz...
    📰 srf | ⏰ 2h | 🎯 P9 | ⚖️ W2.0

🎨 Generating HTML dashboard...
✅ HTML dashboard created: /outplay/rss.html
🌐 Open in browser: file:///path/to/rss.html
```

### **🌐 HTML Dashboard Output**
The CLI automatically generates a professional HTML dashboard at `/outplay/rss.html` with:

- **Statistics Cards** - Total feeds, articles, sources, categories
- **Filter Controls** - Category tags and sort dropdown
- **News Table** - All articles with dual links
- **RSS Sources Table** - Feed management overview
- **Responsive Design** - Works on all devices
- **Live JavaScript** - No page reloads needed

### **🔧 Integration Example**

```python
from src.services.rss_service import RSSService

# Initialize service
rss_service = RSSService()

# Get all active feeds
feeds = await rss_service.get_all_active_feeds()
print(f"Found {len(feeds)} active RSS feeds")

# Collect recent news
news = await rss_service.get_all_recent_news(max_age_hours=6)
print(f"Collected {len(news)} recent articles")

# Process by category
categories = {}
for article in news:
    if article.category not in categories:
        categories[article.category] = []
    categories[article.category].append(article)

print(f"Categories: {list(categories.keys())}")
```

---

## 🔗 Service Integration

### **📊 Data Collection Integration**

Both services integrate seamlessly with the main `DataCollectionService`:

```python
class DataCollectionService:
    def __init__(self):
        self.bitcoin_service = BitcoinService()
        self.weather_service = WeatherService()
    
    async def collect_all_data(self) -> Dict[str, Any]:
        # Parallel data collection for optimal performance
        bitcoin_data, weather_data = await asyncio.gather(
            self.bitcoin_service.get_bitcoin_data(),
            self.weather_service.get_current_weather("Zürich")
        )
        
        return {
            "bitcoin": bitcoin_data,
            "weather": weather_data,
            "timestamp": datetime.now().isoformat()
        }
```

### **🎙️ Radio Integration**

Services provide radio-ready announcements for broadcast generation:

```python
# Bitcoin announcement in broadcast
bitcoin_announcement = await bitcoin_service.get_radio_announcement("24h")

# Weather announcement in broadcast  
weather_announcement = await weather_service.get_radio_announcement("Zürich")

# Integrated into broadcast script
broadcast_script = f"""
Good morning! Here's your market update: {bitcoin_announcement}

And now for the weather: {weather_announcement}
"""
```

---

## 🚀 Performance Optimization

### **⚡ Caching Strategy**

Both services implement intelligent caching:

```python
# Bitcoin Service - 5-minute cache
if self._is_cache_valid("bitcoin", 300):
    return self.cache["bitcoin"]["data"]

# Weather Service - 10-minute cache  
if self._is_cache_valid("weather", 600):
    return self.cache["weather"]["data"]
```

### **🔄 Async Operations**

All API calls are asynchronous for optimal performance:

```python
async with aiohttp.ClientSession() as session:
    async with session.get(url, headers=headers) as response:
        data = await response.json()
        return self._process_response(data)
```

### **📊 Error Handling**

Comprehensive error handling with graceful fallbacks:

```python
try:
    data = await self._fetch_api_data()
    return self._process_data(data)
except aiohttp.ClientError as e:
    logger.warning(f"API request failed: {e}")
    return self._get_cached_data_or_fallback()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return self._get_emergency_fallback()
```

---

## 🧪 Testing

### **🔧 Unit Testing**

```bash
# Test individual services
python cli_bitcoin.py --test
python cli_weather.py --test

# Test with specific parameters
python cli_bitcoin.py --timeframe 7d
python cli_weather.py --city Geneva
```

### **📊 Integration Testing**

```bash
# Test data collection integration
python cli_master.py test --services bitcoin,weather

# Test radio announcement generation
python cli_master.py test --radio-announcements
```

### **🚀 Production Testing**

```bash
# Full system test with real APIs
python production/radiox_master.py --action system_status

# Generate test broadcast with services
python production/radiox_master.py --action generate_broadcast --test-mode
```

---

## 📈 Monitoring & Logging

### **📊 Service Metrics**

Both services provide comprehensive metrics:

```python
{
    "service": "bitcoin",
    "status": "healthy",
    "api_calls_today": 245,
    "cache_hit_rate": 0.78,
    "average_response_time": 0.234,
    "last_successful_call": "2024-12-19T20:00:00Z",
    "errors_last_24h": 2
}
```

### **🔍 Logging Strategy**

Minimalistic logging focused on essential information:

```python
# Only warnings and errors are logged
logger.warning("API rate limit approaching")
logger.error("Failed to fetch data after 3 retries")

# Debug messages removed for production clarity
# logger.info() calls eliminated
```

---

## 🔧 Configuration Management

### **⚙️ Environment Variables**

```bash
# Required for Bitcoin Service
COINMARKETCAP_API_KEY=your_coinmarketcap_key

# Required for Weather Service  
OPENWEATHERMAP_API_KEY=your_openweather_key

# Optional: Cache settings
BITCOIN_CACHE_DURATION=300  # 5 minutes
WEATHER_CACHE_DURATION=600  # 10 minutes
```

### **🎛️ Service Configuration**

```python
# Bitcoin Service Configuration
BITCOIN_CONFIG = {
    "cache_duration": 300,
    "supported_timeframes": ["1h", "24h", "7d", "30d", "60d", "90d"],
    "default_timeframe": "24h",
    "api_timeout": 10
}

# Weather Service Configuration
WEATHER_CONFIG = {
    "cache_duration": 600,
    "default_city": "Zürich",
    "supported_cities": ["Zürich", "Basel", "Geneva", "Bern", "Lausanne", "Winterthur", "Lucerne", "St. Gallen"],
    "api_timeout": 15,
    "smart_outlook_threshold": 18  # Hour to switch from next_hours to tomorrow
}
```

---

## 🎯 Best Practices

### **✅ Service Development**

1. **Single Responsibility** - Each service handles one domain
2. **Async by Default** - All I/O operations are asynchronous
3. **Comprehensive Error Handling** - Graceful fallbacks for all scenarios
4. **Intelligent Caching** - Optimize API calls without sacrificing freshness
5. **Professional Logging** - Minimal, actionable log messages
6. **Radio-Ready Output** - All announcements are broadcast-quality

### **🔧 Integration Guidelines**

1. **Loose Coupling** - Services don't depend on each other
2. **Standardized Interfaces** - Consistent method signatures
3. **Parallel Execution** - Use `asyncio.gather()` for concurrent calls
4. **Graceful Degradation** - System continues working if one service fails
5. **Comprehensive Testing** - Both unit and integration tests

### **🚀 Production Deployment**

1. **Environment Validation** - Check all required API keys
2. **Health Checks** - Regular service health monitoring
3. **Rate Limiting** - Respect API rate limits with caching
4. **Error Monitoring** - Track and alert on service failures
5. **Performance Metrics** - Monitor response times and success rates

---

## 📚 Additional Resources

- [🏗️ Architecture Overview](architecture.md)
- [🔧 Development Setup](development.md)
- [🧪 Testing Guide](testing.md)
- [🚀 Production Deployment](../deployment/production.md)
- [📊 Monitoring Setup](../deployment/monitoring.md) 