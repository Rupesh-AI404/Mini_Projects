"""
Weather CLI App - A small project covering Python fundamentals
Concepts covered:
- Working with APIs
- JSON parsing
- Dictionary manipulation
- String formatting
- Error handling
- Time and date handling
- Command-line arguments
- Environment variables
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple

# Try to import for colored output (optional)
try:
    from colorama import init, Fore, Style

    init()  # Initialize colorama for Windows
    COLORS_ENABLED = True
except ImportError:
    # Fallback if colorama not installed
    COLORS_ENABLED = False


    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = RESET = ''


    Style = Fore  # For compatibility

# API Configuration
API_KEY = "694e1c2ee810ebdf4429e4816e8d1596"  # Get free key from https://openweathermap.org/api
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Default city if none provided
DEFAULT_CITY = "London"


def get_weather_data(city: str, api_key: str) -> Optional[Dict]:
    """Fetch weather data from OpenWeatherMap API"""
    try:
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # Use Celsius
        }

        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}❌ Network error: {e}{Fore.RESET}")
        return None
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}❌ Error parsing weather data: {e}{Fore.RESET}")
        return None


def display_weather(data: Dict) -> None:
    """Display formatted weather information"""
    # Extract data from API response
    city_name = data.get('name', 'Unknown')
    country = data.get('sys', {}).get('country', '')
    weather_desc = data.get('weather', [{}])[0].get('description', 'Unknown')
    temp = data.get('main', {}).get('temp', 0)
    feels_like = data.get('main', {}).get('feels_like', 0)
    humidity = data.get('main', {}).get('humidity', 0)
    pressure = data.get('main', {}).get('pressure', 0)
    wind_speed = data.get('wind', {}).get('speed', 0)
    clouds = data.get('clouds', {}).get('all', 0)
    sunrise = data.get('sys', {}).get('sunrise', 0)
    sunset = data.get('sys', {}).get('sunset', 0)

    # Convert sunrise/sunset timestamps to readable time
    sunrise_time = datetime.fromtimestamp(sunrise).strftime('%H:%M')
    sunset_time = datetime.fromtimestamp(sunset).strftime('%H:%M')

    # Display formatted weather
    print(f"\n{Fore.CYAN}{'=' * 50}{Fore.RESET}")
    print(f"{Fore.YELLOW}🌍 WEATHER REPORT{Fore.RESET}")
    print(f"{Fore.CYAN}{'=' * 50}{Fore.RESET}")

    print(f"\n{Fore.GREEN}📍 Location:{Fore.RESET} {city_name}, {country}")
    print(f"{Fore.GREEN}📅 Date/Time:{Fore.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n{Fore.BLUE}🌤️ Current Weather:{Fore.RESET}")
    print(f"   {weather_desc.upper()}")
    print(f"   🌡️ Temperature: {Fore.RED}{temp:.1f}°C{Fore.RESET} (Feels like: {feels_like:.1f}°C)")

    print(f"\n{Fore.BLUE}💨 Additional Info:{Fore.RESET}")
    print(f"   💧 Humidity: {humidity}%")
    print(f"   📊 Pressure: {pressure} hPa")
    print(f"   💨 Wind Speed: {wind_speed} m/s")
    print(f"   ☁️ Cloud Cover: {clouds}%")

    print(f"\n{Fore.BLUE}🌅 Sun Schedule:{Fore.RESET}")
    print(f"   🌄 Sunrise: {sunrise_time}")
    print(f"   🌇 Sunset: {sunset_time}")

    # Weather advice
    print(f"\n{Fore.YELLOW}💡 Weather Advice:{Fore.RESET}")
    give_weather_advice(temp, humidity, wind_speed, weather_desc)

    print(f"\n{Fore.CYAN}{'=' * 50}{Fore.RESET}")


def give_weather_advice(temp: float, humidity: int, wind_speed: float, weather_desc: str) -> None:
    """Give practical advice based on weather conditions"""
    advice = []

    # Temperature-based advice
    if temp < 0:
        advice.append("❄️ Freezing! Wear heavy winter clothing.")
    elif temp < 10:
        advice.append("🧥 Cold! Bring a jacket.")
    elif temp < 20:
        advice.append("👕 Cool weather, comfortable for outdoor activities.")
    elif temp < 30:
        advice.append("☀️ Warm weather, enjoy the sunshine!")
    else:
        advice.append("🥵 Hot! Stay hydrated and use sunscreen.")

    # Weather condition advice
    if 'rain' in weather_desc.lower():
        advice.append("☔ Rain expected! Bring an umbrella.")
    elif 'snow' in weather_desc.lower():
        advice.append("⛄ Snowfall! Wear waterproof boots.")
    elif 'thunder' in weather_desc.lower():
        advice.append("⚡ Thunderstorm! Stay indoors.")
    elif 'clear' in weather_desc.lower():
        advice.append("🕶️ Clear skies! Great day for outdoor activities.")

    # Wind advice
    if wind_speed > 10:
        advice.append("💨 Windy! Secure loose items.")

    # Humidity advice
    if humidity > 80:
        advice.append("💧 High humidity! Might feel warmer than actual temperature.")

    for tip in advice[:3]:  # Show max 3 tips
        print(f"   {tip}")


def validate_city(city: str) -> bool:
    """Basic city name validation"""
    if not city or len(city.strip()) == 0:
        return False
    if len(city) > 100:
        return False
    # Check if city name contains only letters, spaces, hyphens, and apostrophes
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
    return all(c in valid_chars for c in city)


def save_weather_to_file(data: Dict, filename: str = "weather_history.txt") -> None:
    """Save weather data to a text file"""
    try:
        with open(filename, 'a') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            city = data.get('name', 'Unknown')
            temp = data.get('main', {}).get('temp', 0)
            weather = data.get('weather', [{}])[0].get('description', 'Unknown')

            file.write(f"{timestamp} | {city} | {temp:.1f}°C | {weather}\n")
        print(f"{Fore.GREEN}✅ Weather saved to {filename}{Fore.RESET}")
    except IOError as e:
        print(f"{Fore.RED}❌ Error saving weather data: {e}{Fore.RESET}")


def show_weather_history(filename: str = "weather_history.txt") -> None:
    """Display weather history from file"""
    if not os.path.exists(filename):
        print(f"{Fore.YELLOW}📭 No weather history found.{Fore.RESET}")
        return

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        if not lines:
            print(f"{Fore.YELLOW}📭 Weather history is empty.{Fore.RESET}")
            return

        print(f"\n{Fore.CYAN}{'=' * 60}{Fore.RESET}")
        print(f"{Fore.YELLOW}📜 WEATHER HISTORY{Fore.RESET}")
        print(f"{Fore.CYAN}{'=' * 60}{Fore.RESET}")

        # Show last 10 entries
        for line in lines[-10:]:
            print(f"   {line.strip()}")

        print(f"{Fore.CYAN}{'=' * 60}{Fore.RESET}")

    except IOError as e:
        print(f"{Fore.RED}❌ Error reading weather history: {e}{Fore.RESET}")


def get_api_key() -> str:
    """Get API key from environment or user input"""
    # Try to get from environment variable first
    api_key = os.environ.get('OPENWEATHER_API_KEY', '')

    if not api_key:
        print(f"{Fore.YELLOW}⚠️  No API key found in environment variables.{Fore.RESET}")
        print("Get a free API key from: https://openweathermap.org/api")
        api_key = input("Enter your API key: ").strip()

        if not api_key:
            print(f"{Fore.RED}❌ API key is required to use this app.{Fore.RESET}")
            sys.exit(1)

    return api_key


def show_help() -> None:
    """Display help information"""
    print(f"""
{Fore.CYAN}WEATHER CLI APP - HELP{Fore.RESET}
{'=' * 40}

Usage:
  python weather_app.py [city_name] [options]

Options:
  city_name     Name of the city to check weather for
  -h, --help    Show this help message
  -s, --save    Save weather data to history file
  -H, --history Show weather history

Examples:
  python weather_app.py London
  python weather_app.py "New York" --save
  python weather_app.py --history

If no city is provided, uses default city: {DEFAULT_CITY}

Environment Variable:
  OPENWEATHER_API_KEY    Your OpenWeatherMap API key
    """)


def main():
    """Main program logic"""
    # Parse command line arguments
    args = sys.argv[1:]

    city = DEFAULT_CITY
    save_to_file = False
    show_history = False

    # Simple argument parsing
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['-h', '--help']:
            show_help()
            return
        elif arg in ['-s', '--save']:
            save_to_file = True
        elif arg in ['-H', '--history']:
            show_history = True
        elif not arg.startswith('-'):
            city = arg
        i += 1

    # Show history if requested
    if show_history:
        show_weather_history()
        return

    # Get API key
    api_key = get_api_key()

    # Validate city name
    if not validate_city(city):
        print(f"{Fore.RED}❌ Invalid city name: '{city}'{Fore.RESET}")
        print("City name should only contain letters, spaces, hyphens, and apostrophes.")
        return

    # Fetch weather data
    print(f"{Fore.CYAN}🔍 Fetching weather for {city}...{Fore.RESET}")
    weather_data = get_weather_data(city, api_key)

    if weather_data:
        # Check if city was found
        if weather_data.get('cod') == '404':
            print(f"{Fore.RED}❌ City '{city}' not found.{Fore.RESET}")
            return

        # Display weather information
        display_weather(weather_data)

        # Save to file if requested
        if save_to_file:
            save_weather_to_file(weather_data)
    else:
        print(f"{Fore.RED}❌ Failed to retrieve weather data.{Fore.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Fore.RESET}")