#!/usr/bin/env python3

"""
Weather Service
===============

Service for weather data:
- OpenWeatherMap API Integration
- Current weather for Swiss cities
- Weather forecasts
- Radio-formatted weather reports

DEPENDENCIES: Only OpenWeatherMap API Key
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass

# Import Settings
from config.settings import get_settings

@dataclass
class WeatherLocation:
    """Weather location definition"""
    name: str
    city_id: int  # OpenWeatherMap City ID
    country_code: str = "CH"

class WeatherService:
    """OpenWeatherMap Weather Service for RadioX"""
    
    def __init__(self):
        # Load Weather API Key from Settings
        settings = get_settings()
        self.api_key = settings.weather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Swiss cities with OpenWeatherMap City IDs
        self.locations = {
            "zurich": WeatherLocation("Zürich", 2657896, "CH"),
            "basel": WeatherLocation("Basel", 2661604, "CH"),
            "geneva": WeatherLocation("Geneva", 2660646, "CH"),
            "bern": WeatherLocation("Bern", 2661552, "CH"),
            "lausanne": WeatherLocation("Lausanne", 2659994, "CH"),
            "winterthur": WeatherLocation("Winterthur", 2657970, "CH"),
            "lucerne": WeatherLocation("Lucerne", 2659811, "CH"),
            "st_gallen": WeatherLocation("St. Gallen", 2658822, "CH")
        }
        
    def _check_api_key(self) -> bool:
        """Checks if API key is available"""
        if not self.api_key or self.api_key == "your_openweathermap_api_key_here":
            logger.warning("⚠️ Weather API Key not configured")
            return False
        return True
    
    async def get_current_weather(self, location: str = "zurich") -> Optional[Dict[str, Any]]:
        """Retrieves current weather for a city"""
        try:
            if not self._check_api_key():
                return None
                
            # Normalize city names
            location_mapping = {
                "zürich": "zurich",
                "zuerich": "zurich",
                "Zürich": "zurich",
                "Zuerich": "zurich"
            }
            location = location_mapping.get(location, location.lower())
            
            if location not in self.locations:
                logger.warning(f"Unknown city: {location}, using fallback: zurich")
                location = "zurich"
            
            loc = self.locations[location]
            
            # Build API URL
            url = f"{self.base_url}/weather"
            params = {
                "id": loc.city_id,
                "appid": self.api_key,
                "units": "metric",
                "lang": "en"
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    # Get weather data from OpenWeatherMap
                    response = await session.get(url, params=params)
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract relevant data
                        weather_info = {
                            "temperature": round(data["main"]["temp"], 1),
                            "feels_like": round(data["main"]["feels_like"], 1),
                            "humidity": data["main"]["humidity"],
                            "pressure": data["main"]["pressure"],
                            "description": data["weather"][0]["description"],
                            "wind_speed": round(data.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s to km/h
                            "wind_direction": data.get("wind", {}).get("deg", 0),
                            "visibility": round(data.get("visibility", 0) / 1000, 1),  # km
                            "clouds": data.get("clouds", {}).get("all", 0),
                            "location": loc.name,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        return weather_info
                    else:
                        logger.error(f"❌ OpenWeatherMap API error: {response.status}")
                        return None
                        
                except Exception as e:
                    logger.error(f"❌ Error retrieving weather: {e}")
                    return None
                        
        except Exception as e:
            logger.error(f"❌ Error retrieving weather: {e}")
            return None

    async def test_connection(self) -> bool:
        """Tests weather API connection"""
        try:
            weather_data = await self.get_current_weather("zurich")
            return weather_data is not None and "temperature" in weather_data
        except Exception as e:
            logger.error(f"Weather Service test error: {e}")
            return False
    
    def format_for_radio(self, weather_data: Optional[Dict[str, Any]] = None, location: str = "Zurich") -> str:
        """Formats weather data for radio announcement"""
        if not weather_data:
            return f"Weather data for {location} not available"
        
        temp = weather_data.get('temperature', 0)
        description = weather_data.get('description', 'unknown')
        wind_speed = weather_data.get('wind_speed', 0)
        humidity = weather_data.get('humidity', 0)
        
        return f"Current weather in {location}: {description.title()}, {temp:.1f} degrees Celsius, wind {wind_speed:.1f} kilometers per hour, humidity {humidity} percent."