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
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from ROOT directory
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')

@dataclass
class WeatherLocation:
    """Weather location definition"""
    name: str
    city_id: int  # OpenWeatherMap City ID
    country_code: str = "CH"

@dataclass
class CurrentWeather:
    """Current weather data"""
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    weather_main: str
    weather_description: str
    visibility: int
    clouds: int
    time: datetime

@dataclass
class WeatherForecast:
    """Weather forecast data"""
    date: datetime
    temperature_max: float
    temperature_min: float
    weather_main: str
    weather_description: str
    precipitation: float
    wind_speed: float
    humidity: int

class WeatherService:
    """OpenWeatherMap Weather Service for RadioX"""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
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
    
    async def get_forecast(self, location: str = "zurich", days: int = 5) -> List[Dict[str, Any]]:
        """5-day weather forecast (free with OpenWeatherMap)"""
        try:
            if not self._check_api_key():
                return []
                
            if location not in self.locations:
                location = "zurich"
            
            loc = self.locations[location]
            
            params = {
                "id": loc.city_id,
                "appid": self.api_key,
                "units": "metric",
                "lang": "en"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/forecast", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Group by days (OpenWeatherMap gives 3h intervals)
                        daily_forecasts = {}
                        
                        for item in data["list"]:
                            date = datetime.fromtimestamp(item["dt"]).date()
                            
                            if date not in daily_forecasts:
                                daily_forecasts[date] = {
                                    "temps": [],
                                    "weather": item["weather"][0],
                                    "precipitation": 0,
                                    "wind_speed": item["wind"]["speed"] * 3.6,  # m/s to km/h
                                    "humidity": item["main"]["humidity"]
                                }
                            
                            daily_forecasts[date]["temps"].append(item["main"]["temp"])
                            
                            # Sum precipitation
                            if "rain" in item:
                                daily_forecasts[date]["precipitation"] += item["rain"].get("3h", 0)
                            if "snow" in item:
                                daily_forecasts[date]["precipitation"] += item["snow"].get("3h", 0)
                        
                        # Convert to forecast objects
                        forecasts = []
                        for date, data_item in list(daily_forecasts.items())[:days]:
                            forecast = {
                                "date": date.strftime("%Y-%m-%d"),
                                "day_name": date.strftime("%A"),
                                "temperature_max": round(max(data_item["temps"]), 1),
                                "temperature_min": round(min(data_item["temps"]), 1),
                                "weather_main": data_item["weather"]["main"],
                                "weather_description": data_item["weather"]["description"],
                                "precipitation": round(data_item["precipitation"], 1),
                                "wind_speed": round(data_item["wind_speed"], 1),
                                "humidity": data_item["humidity"]
                            }
                            forecasts.append(forecast)
                        
                        return forecasts
                    else:
                        logger.error(f"❌ OpenWeatherMap Forecast API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"❌ Error retrieving forecast: {e}")
            return []
    
    def format_weather_for_radio(self, weather: CurrentWeather, location_name: str) -> str:
        """Formatiert Wetter für Radio-Ansage"""
        # Wind-Richtung
        wind_directions = {
            (0, 22): "Nord", (23, 67): "Nordost", (68, 112): "Ost",
            (113, 157): "Südost", (158, 202): "Süd", (203, 247): "Südwest",
            (248, 292): "West", (293, 337): "Nordwest", (338, 360): "Nord"
        }
        
        wind_dir = "unbekannt"
        for (start, end), direction in wind_directions.items():
            if start <= weather.wind_direction <= end:
                wind_dir = direction
                break
        
        return f"""Aktuelles Wetter in {location_name}: {weather.weather_description.title()}, 
{weather.temperature:.1f} Grad Celsius, gefühlt wie {weather.feels_like:.1f} Grad. 
Luftfeuchtigkeit {weather.humidity}%, Wind aus {wind_dir} mit {weather.wind_speed:.1f} km/h. 
Luftdruck {weather.pressure} hPa."""
    
    def format_forecast_for_radio(self, forecasts: List[Dict[str, Any]], location: str = "Zurich") -> str:
        """Formats weather forecast for radio announcement"""
        if not forecasts:
            return f"Weather forecast for {location} not available."
        
        forecast_text = f"Weather outlook for {location}: "
        
        for i, forecast in enumerate(forecasts[:3]):  # Only 3 days for radio
            if i == 0:
                day_name = "Today"
            elif i == 1:
                day_name = "Tomorrow"
            else:
                day_name = forecast["day_name"]
            
            forecast_text += f"{day_name}: {forecast['weather_description'].title()}, "
            forecast_text += f"high {forecast['temperature_max']:.1f}, low {forecast['temperature_min']:.1f} degrees. "
            
            if forecast['precipitation'] > 0:
                forecast_text += f"Precipitation: {forecast['precipitation']:.1f} millimeters. "
        
        return forecast_text
    
    async def get_weather_for_station(self, station_id: str) -> Dict[str, Any]:
        """Wetter für spezifische Radio-Station"""
        # Station-spezifische Städte-Zuordnung
        station_cities = {
            "radiox_zurich": "zurich",
            "radiox_basel": "basel", 
            "radiox_geneva": "geneva",
            "radiox_bern": "bern"
        }
        
        city = station_cities.get(station_id, "zurich")
        current = await self.get_current_weather(city)
        forecast = await self.get_forecast(city, 3)
        
        if current:
            return {
                "current": {
                    "temperature": current.temperature,
                    "description": current.weather_description,
                    "humidity": current.humidity,
                    "wind_speed": current.wind_speed
                },
                "forecast": [
                    {
                        "date": f.date.strftime("%Y-%m-%d"),
                        "temp_max": f.temperature_max,
                        "temp_min": f.temperature_min,
                        "description": f.weather_description
                    } for f in forecast
                ],
                "radio_text": self.format_weather_for_radio(current, self.locations[city].name)
            }
        
        return {"error": "Wetterdaten nicht verfügbar"}
    
    async def get_multiple_cities_weather(self) -> Dict[str, Dict[str, Any]]:
        """Wetter für alle konfigurierten Städte"""
        weather_data = {}
        
        for city_key, location in self.locations.items():
            current = await self.get_current_weather(city_key)
            if current:
                weather_data[city_key] = {
                    "city": location.name,
                    "temperature": current.temperature,
                    "description": current.weather_description,
                    "humidity": current.humidity,
                    "wind_speed": current.wind_speed,
                    "radio_text": self.format_weather_for_radio(current, location.name)
                }
        
        return weather_data

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

    async def get_smart_outlook(self, location: str = "zurich") -> Dict[str, Any]:
        """Smart weather outlook based on time of day
        
        00:00-18:00: Next 2 hours forecast
        18:00-23:59: Current weather + tomorrow forecast
        """
        
        current_hour = datetime.now().hour
        
        if current_hour < 18:  # 00:00 - 17:59
            # Get hourly forecast for next 2 hours
            return await self._get_next_hours_outlook(location, 2)
        else:  # 18:00 - 23:59
            # Get current + tomorrow forecast
            return await self._get_current_plus_tomorrow_outlook(location)
    
    async def _get_next_hours_outlook(self, location: str, hours: int = 2) -> Dict[str, Any]:
        """Get hourly forecast for next few hours"""
        
        try:
            if not self._check_api_key():
                return {"error": "API key not available"}
                
            if location not in self.locations:
                location = "zurich"
            
            loc = self.locations[location]
            
            params = {
                "id": loc.city_id,
                "appid": self.api_key,
                "units": "metric",
                "lang": "en"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/forecast", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Get next few hourly forecasts
                        hourly_forecasts = []
                        current_time = datetime.now()
                        
                        for item in data["list"][:hours]:  # Take first few items (3h intervals)
                            forecast_time = datetime.fromtimestamp(item["dt"])
                            
                            hourly_forecast = {
                                "time": forecast_time.strftime("%H:%M"),
                                "temperature": round(item["main"]["temp"], 1),
                                "description": item["weather"][0]["description"],
                                "precipitation_chance": item.get("pop", 0) * 100,  # Probability of precipitation
                                "wind_speed": round(item["wind"]["speed"] * 3.6, 1),
                                "humidity": item["main"]["humidity"]
                            }
                            hourly_forecasts.append(hourly_forecast)
                        
                        return {
                            "type": "hourly",
                            "location": loc.name,
                            "forecasts": hourly_forecasts,
                            "period": f"Next {hours * 3} hours"
                        }
                    else:
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"❌ Error getting hourly outlook: {e}")
            return {"error": str(e)}
    
    async def _get_current_plus_tomorrow_outlook(self, location: str) -> Dict[str, Any]:
        """Get current weather + tomorrow forecast"""
        
        try:
            # Get current weather
            current = await self.get_current_weather(location)
            if not current:
                return {"error": "Current weather not available"}
            
            # Get tomorrow's forecast
            forecast = await self.get_forecast(location, 2)  # Today + Tomorrow
            tomorrow = forecast[1] if len(forecast) > 1 else None
            
            return {
                "type": "current_plus_tomorrow",
                "location": current["location"],
                "current": {
                    "temperature": current["temperature"],
                    "description": current["description"],
                    "wind_speed": current["wind_speed"],
                    "humidity": current["humidity"]
                },
                "tomorrow": tomorrow if tomorrow else {"error": "Tomorrow forecast not available"}
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting current+tomorrow outlook: {e}")
            return {"error": str(e)}
    
    def format_smart_outlook_for_radio(self, outlook_data: Dict[str, Any]) -> str:
        """Formats smart outlook for radio announcement"""
        
        if "error" in outlook_data:
            return f"Weather outlook not available: {outlook_data['error']}"
        
        location = outlook_data.get("location", "Unknown")
        
        if outlook_data["type"] == "hourly":
            # Format hourly forecast
            forecasts = outlook_data["forecasts"]
            if not forecasts:
                return f"Hourly forecast for {location} not available."
            
            text = f"Weather outlook for {location} - next few hours: "
            
            for forecast in forecasts:
                text += f"At {forecast['time']}: {forecast['description'].title()}, "
                text += f"{forecast['temperature']:.1f} degrees"
                
                if forecast['precipitation_chance'] > 30:
                    text += f", {forecast['precipitation_chance']:.0f} percent chance of rain"
                
                text += ". "
            
            return text
            
        elif outlook_data["type"] == "current_plus_tomorrow":
            # Format current + tomorrow
            current = outlook_data["current"]
            tomorrow = outlook_data["tomorrow"]
            
            text = f"Current weather in {location}: {current['description'].title()}, "
            text += f"{current['temperature']:.1f} degrees Celsius. "
            
            if "error" not in tomorrow:
                text += f"Tomorrow: {tomorrow['weather_description'].title()}, "
                text += f"high {tomorrow['temperature_max']:.1f}, low {tomorrow['temperature_min']:.1f} degrees."
                
                if tomorrow['precipitation'] > 0:
                    text += f" Precipitation expected: {tomorrow['precipitation']:.1f} millimeters."
            
            return text
        
        return "Weather outlook format not recognized."

# Convenience Functions für RadioX Integration
async def get_zurich_weather_for_radio() -> str:
    """Schneller Zugriff auf Zürich Wetter für Radio"""
    service = WeatherService()
    weather = await service.get_current_weather("zurich")
    if weather:
        return service.format_weather_for_radio(weather, "Zürich")
    return "Wetterdaten für Zürich nicht verfügbar."

async def get_weather_segment_for_station(station_id: str) -> Dict[str, str]:
    """Komplettes Wetter-Segment für Radio-Station"""
    service = WeatherService()
    weather_data = await service.get_weather_for_station(station_id)
    
    if "error" not in weather_data:
        return {
            "current_weather": weather_data["radio_text"],
            "forecast_summary": f"Aussichten: {weather_data['forecast'][0]['description'] if weather_data['forecast'] else 'Keine Vorhersage verfügbar'}"
        } 
    
    return {"error": "Wetter-Segment nicht verfügbar"} 