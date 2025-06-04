"""
RadioX Weather Service - Open-Meteo Integration
Kostenlose Wetter-API für Radio Stations
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass

@dataclass
class WeatherLocation:
    """Wetter-Standort Definition"""
    name: str
    latitude: float
    longitude: float
    timezone: str = "Europe/Zurich"

@dataclass
class CurrentWeather:
    """Aktuelles Wetter"""
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    weather_code: int
    is_day: bool
    time: datetime

@dataclass
class WeatherForecast:
    """Wetter-Vorhersage"""
    date: datetime
    temperature_max: float
    temperature_min: float
    weather_code: int
    precipitation_sum: float
    wind_speed_max: float

class WeatherService:
    """Open-Meteo Weather Service für RadioX"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        
        # Schweizer Städte für RadioX
        self.locations = {
            "zurich": WeatherLocation("Zürich", 47.3769, 8.5417),
            "basel": WeatherLocation("Basel", 47.5596, 7.5886),
            "geneva": WeatherLocation("Genf", 46.2044, 6.1432),
            "bern": WeatherLocation("Bern", 46.9481, 7.4474),
            "lausanne": WeatherLocation("Lausanne", 46.5197, 6.6323),
            "winterthur": WeatherLocation("Winterthur", 47.5022, 8.7386),
            "lucerne": WeatherLocation("Luzern", 47.0502, 8.3093),
            "st_gallen": WeatherLocation("St. Gallen", 47.4245, 9.3767)
        }
        
        # Weather Code Mapping (WMO Weather interpretation codes)
        self.weather_descriptions = {
            0: "Klar",
            1: "Meist klar", 2: "Teilweise bewölkt", 3: "Bewölkt",
            45: "Nebel", 48: "Gefrierender Nebel",
            51: "Leichter Nieselregen", 53: "Nieselregen", 55: "Starker Nieselregen",
            56: "Gefrierender Nieselregen", 57: "Starker gefrierender Nieselregen",
            61: "Leichter Regen", 63: "Regen", 65: "Starker Regen",
            66: "Gefrierender Regen", 67: "Starker gefrierender Regen",
            71: "Leichter Schneefall", 73: "Schneefall", 75: "Starker Schneefall",
            77: "Schneekörner",
            80: "Leichte Regenschauer", 81: "Regenschauer", 82: "Starke Regenschauer",
            85: "Schneeschauer", 86: "Starke Schneeschauer",
            95: "Gewitter", 96: "Gewitter mit Hagel", 99: "Starkes Gewitter mit Hagel"
        }
    
    async def get_current_weather(self, location: str = "zurich") -> Optional[CurrentWeather]:
        """Aktuelles Wetter für eine Stadt abrufen"""
        try:
            if location not in self.locations:
                logger.warning(f"Unbekannte Stadt: {location}")
                location = "zurich"  # Fallback
            
            loc = self.locations[location]
            
            params = {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m", 
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "weather_code",
                    "is_day"
                ],
                "timezone": loc.timezone
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/forecast", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data["current"]
                        
                        return CurrentWeather(
                            temperature=current["temperature_2m"],
                            humidity=current["relative_humidity_2m"],
                            wind_speed=current["wind_speed_10m"],
                            wind_direction=current["wind_direction_10m"],
                            weather_code=current["weather_code"],
                            is_day=current["is_day"] == 1,
                            time=datetime.fromisoformat(current["time"])
                        )
                    else:
                        logger.error(f"Weather API Error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Wetters: {e}")
            return None
    
    async def get_forecast(self, location: str = "zurich", days: int = 7) -> List[WeatherForecast]:
        """Wetter-Vorhersage für mehrere Tage"""
        try:
            if location not in self.locations:
                location = "zurich"
            
            loc = self.locations[location]
            
            params = {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "weather_code",
                    "precipitation_sum",
                    "wind_speed_10m_max"
                ],
                "timezone": loc.timezone,
                "forecast_days": days
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/forecast", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        daily = data["daily"]
                        
                        forecasts = []
                        for i in range(len(daily["time"])):
                            forecast = WeatherForecast(
                                date=datetime.fromisoformat(daily["time"][i]),
                                temperature_max=daily["temperature_2m_max"][i],
                                temperature_min=daily["temperature_2m_min"][i],
                                weather_code=daily["weather_code"][i],
                                precipitation_sum=daily["precipitation_sum"][i],
                                wind_speed_max=daily["wind_speed_10m_max"][i]
                            )
                            forecasts.append(forecast)
                        
                        return forecasts
                    else:
                        logger.error(f"Forecast API Error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Vorhersage: {e}")
            return []
    
    def get_weather_description(self, weather_code: int) -> str:
        """Wetter-Beschreibung basierend auf Code"""
        return self.weather_descriptions.get(weather_code, "Unbekannt")
    
    def format_weather_for_radio(self, weather: CurrentWeather, location_name: str) -> str:
        """Formatiert Wetter für Radio-Ansage"""
        description = self.get_weather_description(weather.weather_code)
        time_of_day = "Tag" if weather.is_day else "Nacht"
        
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
        
        # Radio-freundliche Formatierung
        radio_text = f"Das aktuelle Wetter in {location_name}: {description}, "
        radio_text += f"{weather.temperature:.0f} Grad, "
        radio_text += f"Luftfeuchtigkeit {weather.humidity} Prozent. "
        radio_text += f"Wind aus {wind_dir} mit {weather.wind_speed:.0f} Kilometern pro Stunde."
        
        return radio_text
    
    def format_forecast_for_radio(self, forecasts: List[WeatherForecast], location_name: str) -> str:
        """Formatiert Vorhersage für Radio"""
        if not forecasts:
            return f"Keine Wettervorhersage für {location_name} verfügbar."
        
        # Heute und morgen
        today = forecasts[0] if forecasts else None
        tomorrow = forecasts[1] if len(forecasts) > 1 else None
        
        radio_text = f"Die Wettervorhersage für {location_name}: "
        
        if today:
            today_desc = self.get_weather_description(today.weather_code)
            radio_text += f"Heute {today_desc}, Höchsttemperatur {today.temperature_max:.0f} Grad, "
            radio_text += f"Tiefsttemperatur {today.temperature_min:.0f} Grad. "
            
            if today.precipitation_sum > 0:
                radio_text += f"Niederschlag: {today.precipitation_sum:.1f} Millimeter. "
        
        if tomorrow:
            tomorrow_desc = self.get_weather_description(tomorrow.weather_code)
            radio_text += f"Morgen {tomorrow_desc}, zwischen {tomorrow.temperature_min:.0f} und {tomorrow.temperature_max:.0f} Grad."
        
        return radio_text
    
    async def get_weather_for_station(self, station_id: str) -> Dict[str, Any]:
        """Wetter-Info für spezifische Radio Station"""
        # Station-spezifische Standorte
        station_locations = {
            "breaking_news": "zurich",
            "zueri_style": "zurich", 
            "bitcoin_og": "zurich",
            "tradfi_news": "zurich",
            "tech_insider": "zurich",
            "swiss_local": "bern"  # Hauptstadt für Swiss Local
        }
        
        location = station_locations.get(station_id, "zurich")
        location_name = self.locations[location].name
        
        # Aktuelles Wetter und Vorhersage parallel abrufen
        current_task = self.get_current_weather(location)
        forecast_task = self.get_forecast(location, days=3)
        
        current_weather, forecast = await asyncio.gather(current_task, forecast_task)
        
        result = {
            "location": location_name,
            "current": current_weather,
            "forecast": forecast,
            "radio_current": None,
            "radio_forecast": None
        }
        
        # Radio-Texte generieren
        if current_weather:
            result["radio_current"] = self.format_weather_for_radio(current_weather, location_name)
        
        if forecast:
            result["radio_forecast"] = self.format_forecast_for_radio(forecast, location_name)
        
        return result
    
    async def get_multiple_cities_weather(self) -> Dict[str, Dict[str, Any]]:
        """Wetter für alle wichtigen Schweizer Städte"""
        tasks = {}
        for city_key, location in self.locations.items():
            tasks[city_key] = self.get_current_weather(city_key)
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        weather_data = {}
        for i, (city_key, location) in enumerate(self.locations.items()):
            weather = results[i] if not isinstance(results[i], Exception) else None
            weather_data[city_key] = {
                "location": location.name,
                "weather": weather,
                "radio_text": self.format_weather_for_radio(weather, location.name) if weather else None
            }
        
        return weather_data


# Convenience Functions für RadioX Integration
async def get_zurich_weather_for_radio() -> str:
    """Schnelle Zürich Wetter-Ansage für Radio"""
    service = WeatherService()
    weather_data = await service.get_weather_for_station("zueri_style")
    return weather_data.get("radio_current", "Wetter momentan nicht verfügbar.")

async def get_weather_segment_for_station(station_id: str) -> Dict[str, str]:
    """Komplettes Wetter-Segment für Radio Station"""
    service = WeatherService()
    weather_data = await service.get_weather_for_station(station_id)
    
    return {
        "current": weather_data.get("radio_current", ""),
        "forecast": weather_data.get("radio_forecast", ""),
        "location": weather_data.get("location", "Zürich")
    } 