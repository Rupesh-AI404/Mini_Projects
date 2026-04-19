import os
import time

import requests
from dotenv import load_dotenv
import requests
import json


class WeatherMonitor:
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("WEATHER_API_KEY") or self.prompt_api_key()
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def prompt_api_key(self):
        """Prompt for API key if it is not set in environment variables."""
        print("\nGet a free API key from: https://openweathermap.org/api")
        while True:
            key = input("Enter your OpenWeatherMap API key: ").strip()
            if key:
                return key
            print("API key is required. Try again or cancel with Ctrl+C.")

    def _make_request(self, endpoint, params):
        """Make API request with basic error handling."""
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as exc:
            print(f"\nRequest failed: {exc}")
            try:
                error_data = response.json()
                message = error_data.get("message")
                if message:
                    print(f"API message: {message}")
            except Exception:
                pass
            return None
        except requests.exceptions.RequestException as exc:
            print(f"\nNetwork error while fetching weather data: {exc}")
            return None

    def get_current_weather(self, city_name):
        """Get current weather conditions for a city."""
        params = {
            "q": city_name,
            "appid": self.api_key,
            "units": "metric",
            "lang": "en",
        }

        data = self._make_request(self.base_url, params)
        if not data:
            return None

        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "condition": data["weather"][0]["main"],
            "updated_at": data["dt"],
        }

    def get_5_day_forecast(self, city_name):
        """Get the next five 3-hour forecast entries for a city."""
        params = {
            "q": city_name,
            "appid": self.api_key,
            "units": "metric",
            "cnt": 5,
            "lang": "en",
        }

        data = self._make_request(self.forecast_url, params)
        if not data:
            return None

        forecast = []
        for item in data.get("list", []):
            forecast.append(
                {
                    "date": item["dt_txt"],
                    "temp_max": item["main"]["temp_max"],
                    "temp_min": item["main"]["temp_min"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "description": item["weather"][0]["description"],
                    "condition": item["weather"][0]["main"],
                }
            )
        return forecast

    def display_weather(self, weather_data):
        """Display formatted current weather information."""
        if not weather_data:
            return False

        print(
            f"\nWeather for {weather_data['city']} "
            f"(Updated: {time.ctime(weather_data['updated_at'])})"
        )
        print(f"Temperature: {weather_data['temp']} C (feels like {weather_data['feels_like']} C)")
        print(f"Condition: {weather_data['condition']} - {weather_data['description']}")
        print(f"Wind: {weather_data['wind_speed']} m/s")
        print(f"Humidity: {weather_data['humidity']}%")
        return True


def main():
    monitor = WeatherMonitor()

    if not monitor.api_key:
        print("API key required but not found. Exiting...")
        return

    try:
        print("\nEnter city name for weather information (Ctrl+C to quit).")
        while True:
            city = input("\nCity name: ").strip()
            if not city:
                continue

            print(f"\nFetching current weather for {city}...")
            current_weather = monitor.get_current_weather(city)

            if current_weather:
                monitor.display_weather(current_weather)

                if input("\nGet 5-entry forecast? (y/n): ").strip().lower() == "y":
                    forecast = monitor.get_5_day_forecast(city)
                    if forecast:
                        print("\nForecast:")
                        for entry in forecast:
                            print(f"\n{entry['date']}")
                            print(f"High: {entry['temp_max']} C / Low: {entry['temp_min']} C")
                            print(f"Humidity: {entry['humidity']}%")
                            print(f"Wind: {entry['wind_speed']} m/s")
                            print(f"Condition: {entry['condition']} - {entry['description']}")

            if input("\nCheck another city? (y/n): ").strip().lower() != "y":
                break

    except KeyboardInterrupt:
        print("\n\nWeather monitoring stopped. Goodbye!")


if __name__ == "__main__":
    main()