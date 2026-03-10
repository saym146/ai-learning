import json
import requests
from langchain.tools import tool


@tool
def get_weather(location: str) -> str:
    """Get the current weather at a location.

    Args:
        location: The name of the city, state, or province to get weather for.
    """
    try:
        # 1. Geocode the location name to lat/lon using Open-Meteo geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = requests.get(geo_url, params={"name": location, "count": 1}, timeout=10)
        geo_data = geo_resp.json()

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return json.dumps({"error": f"Could not find location: {location}"})

        place = geo_data["results"][0]
        lat, lon = place["latitude"], place["longitude"]
        resolved_name = place.get("name", location)

        # 2. Fetch current + daily forecast from Open-Meteo weather API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_resp = requests.get(weather_url, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,visibility",
            "daily": "temperature_2m_max,precipitation_probability_max",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "forecast_days": 1,
        }, timeout=10)
        weather_data = weather_resp.json()

        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})

        result = {
            "location": resolved_name,
            "condition": _weather_code_to_text(current.get("weather_code", -1)),
            "temperature_c": current.get("temperature_2m", "N/A"),
            "humidity_pct": current.get("relative_humidity_2m", "N/A"),
            "wind_speed_kmh": current.get("wind_speed_10m", "N/A"),
            "visibility_m": current.get("visibility", "N/A"),
            "max_temperature_c": daily.get("temperature_2m_max", ["N/A"])[0],
            "rain_probability_pct": daily.get("precipitation_probability_max", ["N/A"])[0],
        }

        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Error fetching weather for {location}: {str(e)}"})


def _weather_code_to_text(code: int) -> str:
    """Map WMO weather code to a human-readable description."""
    mapping = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return mapping.get(code, "Unknown")
