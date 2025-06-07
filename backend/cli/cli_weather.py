#!/usr/bin/env python3
"""
🌤️ RadioX Weather Service - Standalone CLI
Weather data retrieval for Swiss cities
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.weather_service import WeatherService


async def main():
    print("🌤️ WEATHER SERVICE")
    print("=" * 30)
    
    service = WeatherService()
    success = await service.test_connection()
    
    if success:
        # Current Weather
        zurich_data = await service.get_current_weather("zurich")
        if zurich_data:
            print("🌡️ CURRENT:")
            print(f"   {zurich_data['temperature']:.1f}°C - {zurich_data['description'].title()}")
            print(f"   💨 {zurich_data['wind_speed']:.1f} km/h, 💧 {zurich_data['humidity']}%")
            print()
        
        # Smart Outlook
        current_hour = datetime.now().hour
        
        if current_hour < 18:
            print("🕐 OUTLOOK (Next Hours):")
        else:
            print("🌙 OUTLOOK (Tomorrow):")
        
        smart_outlook = await service.get_smart_outlook("zurich")
        if "error" not in smart_outlook:
            if smart_outlook["type"] == "hourly":
                for forecast in smart_outlook["forecasts"]:
                    rain_info = f", {forecast['precipitation_chance']:.0f}% rain" if forecast['precipitation_chance'] > 30 else ""
                    print(f"   🕐 {forecast['time']}: {forecast['temperature']:.1f}°C - {forecast['description'].title()}{rain_info}")
            
            elif smart_outlook["type"] == "current_plus_tomorrow":
                tomorrow = smart_outlook["tomorrow"]
                if "error" not in tomorrow:
                    rain_info = f", {tomorrow['precipitation']:.1f}mm rain" if tomorrow['precipitation'] > 0 else ""
                    print(f"   📅 Tomorrow: {tomorrow['temperature_min']:.1f}°C - {tomorrow['temperature_max']:.1f}°C")
                    print(f"   📝 {tomorrow['weather_description'].title()}{rain_info}")
            
            print()
            
            # Radio Format
            smart_radio = service.format_smart_outlook_for_radio(smart_outlook)
            print("🎙️ RADIO:")
            print(f"   {smart_radio}")
        else:
            print(f"❌ Outlook error: {smart_outlook['error']}")
        
    else:
        print("❌ Weather API not reachable")
        print("💡 Check WEATHER_API_KEY in .env")


if __name__ == "__main__":
    asyncio.run(main()) 