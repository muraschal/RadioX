"""
Data Services Module
===================

Alle Services für Datensammlung und -akquisition:
- DataCollectionService: Orchestriert alle Datenquellen
- RSSService: RSS Feed Management
- BitcoinService: Cryptocurrency Daten
- WeatherService: Wetterdaten

Best Practice: Domain-driven Design für Data Access Layer
"""

from .data_collection_service import DataCollectionService
from .rss_service import RSSService  
from .bitcoin_service import BitcoinService
from .weather_service import WeatherService

__all__ = [
    "DataCollectionService",
    "RSSService", 
    "BitcoinService",
    "WeatherService"
] 