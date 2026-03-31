"""
Weather CLI App - Improved Version
===================================
Concepts covered:
- Working with APIs (requests library)
- JSON parsing and nested dict access
- String formatting (f-strings)
- Error handling (try/except, HTTP errors)
- Time and date handling (datetime, timestamps)
- Command-line arguments (sys.argv)
- Environment variables (os.environ)
- Type hints (Optional, Dict, List)
- Functions and separation of concerns
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional, List

# ── Optional colored output ────────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)   # autoreset=True means color resets after every print
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False

    # Dummy classes so the rest of the code works without colorama installed
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# ── API Configuration ──────────────────────────────────────────────────────────
# Hardcoded key as fallback; best practice is to use an environment variable:
#   export OPENWEATHER_API_KEY="your_key_here"   (Linux/Mac)
#   set OPENWEATHER_API_KEY=your_key_here        (Windows CMD)
FALLBACK_API_KEY = "88a9179946d50127eae3cd7a554ffdc2"

BASE_URL      = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL  = "https://api.openweathermap.org/data/2.5/forecast"   # 5-day / 3-hour

DEFAULT_CITY  = "lalitpur"


# ── Helpers ────────────────────────────────────────────────────────────────────

def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit using the standard formula."""
    return (c * 9 / 5) + 32


def wind_degrees_to_compass(degrees: int) -> str:
    """
    Convert a wind direction in degrees (0-360) to a compass label.
    We divide the circle into 8 equal 45° sectors.
    """
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8   # modulo 8 keeps index in [0, 7]
    return directions[index]


def format_temp(celsius: float) -> str:
    """Return a formatted temperature string showing both °C and °F."""
    return f"{celsius:.1f}°C / {celsius_to_fahrenheit(celsius):.1f}°F"


def unix_to_time(timestamp: int) -> str:
    """Convert a Unix timestamp (seconds since epoch) to HH:MM string."""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M")


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_city(city: str) -> bool:
    """
    Basic city name validation.
    - Must be non-empty and ≤ 100 characters
    - Only letters, spaces, hyphens, apostrophes, and periods (e.g. "St. Paul")
    """
    if not city or len(city.strip()) == 0:
        return False
    if len(city) > 100:
        return False
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'.")
    return all(c in valid_chars for c in city)


# ── API Calls ──────────────────────────────────────────────────────────────────

def get_weather_data(city: str, api_key: str) -> Optional[Dict]:
    """
    Fetch CURRENT weather data from OpenWeatherMap.

    Returns the parsed JSON dict on success, or None on failure.
    'units=metric' means temperatures come back in Celsius.
    """
    params = {
        "q":     city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        # raise_for_status() throws an HTTPError for 4xx/5xx responses
        # This is the correct way to catch "city not found" (404) etc.
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        # e.response.status_code tells us exactly what went wrong
        status = e.response.status_code if e.response else "?"
        if status == 401:
            print(f"{Fore.RED}❌ Invalid API key. Check your key at openweathermap.org{Fore.RESET}")
        elif status == 404:
            print(f"{Fore.RED}❌ City '{city}' not found. Try a different spelling.{Fore.RESET}")
        else:
            print(f"{Fore.RED}❌ HTTP error {status}: {e}{Fore.RESET}")
        return None

    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ No internet connection.{Fore.RESET}")
        return None

    except requests.exceptions.Timeout:
        print(f"{Fore.RED}❌ Request timed out. Try again later.{Fore.RESET}")
        return None

    except json.JSONDecodeError as e:
        print(f"{Fore.RED}❌ Could not parse server response: {e}{Fore.RESET}")
        return None


def get_forecast_data(city: str, api_key: str) -> Optional[Dict]:
    """
    Fetch 5-day / 3-hour forecast from OpenWeatherMap.
    Same error handling pattern as get_weather_data().
    """
    params = {
        "q":     city,
        "appid": api_key,
        "units": "metric",
        "cnt":   30,   # 40 × 3 hours = 5 days
    }

    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}❌ Could not fetch forecast: {e}{Fore.RESET}")
        return None


# ── Display Functions ──────────────────────────────────────────────────────────

def display_weather(data: Dict) -> None:
    """
    Pretty-print current weather data.
    We use .get() with defaults everywhere so the app doesn't crash
    if the API ever returns incomplete data.
    """
    # ── Extract fields from the nested JSON ──────────────────────────────────
    city_name    = data.get("name", "Unknown")
    country      = data.get("sys", {}).get("country", "")

    # 'weather' is a LIST; we take the first element ([0])
    weather_list = data.get("weather", [{}])
    weather_desc = weather_list[0].get("description", "Unknown") if weather_list else "Unknown"
    weather_icon_id = weather_list[0].get("id", 800) if weather_list else 800

    main         = data.get("main", {})
    temp         = main.get("temp", 0)
    feels_like   = main.get("feels_like", 0)
    temp_min     = main.get("temp_min", 0)
    temp_max     = main.get("temp_max", 0)
    humidity     = main.get("humidity", 0)
    pressure     = main.get("pressure", 0)

    wind         = data.get("wind", {})
    wind_speed   = wind.get("speed", 0)             # metres/second
    wind_deg     = wind.get("deg", 0)               # degrees
    wind_dir     = wind_degrees_to_compass(wind_deg)

    clouds       = data.get("clouds", {}).get("all", 0)
    visibility   = data.get("visibility", 0) / 1000  # metres → km

    sys_info     = data.get("sys", {})
    sunrise      = unix_to_time(sys_info.get("sunrise", 0))
    sunset       = unix_to_time(sys_info.get("sunset",  0))

    # ── Emoji for weather condition ───────────────────────────────────────────
    emoji = weather_emoji(weather_icon_id)

    # ── Print the report ──────────────────────────────────────────────────────
    sep = f"{Fore.CYAN}{'═' * 52}{Fore.RESET}"
    print(f"\n{sep}")
    print(f"  {Fore.YELLOW}⛅ CURRENT WEATHER REPORT{Fore.RESET}")
    print(sep)

    print(f"\n  {Fore.GREEN}📍 {city_name}, {country}{Fore.RESET}")
    print(f"  {Fore.GREEN}🕐 {datetime.now().strftime('%A, %d %b %Y  %H:%M:%S')}{Fore.RESET}")

    print(f"\n  {emoji}  {weather_desc.title()}")
    print(f"  🌡️  Temperature  : {Fore.RED}{format_temp(temp)}{Fore.RESET}")
    print(f"  🤔  Feels like   : {format_temp(feels_like)}")
    print(f"  ⬇️   Min / ⬆️  Max : {format_temp(temp_min)}  /  {format_temp(temp_max)}")

    print(f"\n  💧  Humidity     : {humidity}%")
    print(f"  📊  Pressure     : {pressure} hPa")
    print(f"  💨  Wind         : {wind_speed} m/s  ({wind_dir})")
    print(f"  ☁️   Cloud cover  : {clouds}%")
    print(f"  👁️   Visibility   : {visibility:.1f} km")

    print(f"\n  🌄  Sunrise      : {sunrise}")
    print(f"  🌇  Sunset       : {sunset}")

    print(f"\n  {Fore.YELLOW}💡 Advice:{Fore.RESET}")
    give_weather_advice(temp, humidity, wind_speed, weather_desc)

    print(f"\n{sep}\n")


def display_forecast(data: Dict) -> None:
    """
    Display a 5-day daily summary from the 3-hourly forecast data.
    We group the 3-hour slots by calendar date and pick the midday reading.
    """
    city    = data.get("city", {}).get("name", "Unknown")
    country = data.get("city", {}).get("country", "")
    items   = data.get("list", [])

    # Group forecast items by date (YYYY-MM-DD)
    # A dict of {date_str: [forecast_item, ...]}
    days: Dict[str, List[Dict]] = {}
    for item in items:
        date_str = item["dt_txt"].split(" ")[0]   # "2024-01-15 12:00:00" → "2024-01-15"
        days.setdefault(date_str, []).append(item)

    sep = f"{Fore.CYAN}{'═' * 52}{Fore.RESET}"
    print(f"\n{sep}")
    print(f"  {Fore.YELLOW}📅 5-DAY FORECAST — {city}, {country}{Fore.RESET}")
    print(sep)

    for date_str, readings in list(days.items())[:5]:   # max 5 days
        # Pick the reading closest to 12:00 for a representative daytime value
        midday = min(readings, key=lambda r: abs(12 - int(r["dt_txt"][11:13])))

        temp        = midday["main"]["temp"]
        desc        = midday["weather"][0]["description"].title() if midday.get("weather") else "?"
        humidity    = midday["main"]["humidity"]
        wind_speed  = midday["wind"]["speed"]
        icon_id     = midday["weather"][0]["id"] if midday.get("weather") else 800
        emoji       = weather_emoji(icon_id)

        # Parse the date string into a datetime object to get the weekday name
        date_obj    = datetime.strptime(date_str, "%Y-%m-%d")
        day_label   = date_obj.strftime("%a %d %b")   # e.g. "Mon 15 Jan"

        print(f"\n  {Fore.BLUE}{day_label}{Fore.RESET}  {emoji}  {desc}")
        print(f"    🌡️  {format_temp(temp)}   💧 {humidity}%   💨 {wind_speed} m/s")

    print(f"\n{sep}\n")


def weather_emoji(condition_id: int) -> str:
    """
    Map an OpenWeatherMap condition ID to an emoji.
    Full list: https://openweathermap.org/weather-conditions
    IDs are grouped by hundreds (2xx = thunderstorm, 3xx = drizzle, etc.)
    """
    if   200 <= condition_id < 300:  return "⛈️"
    elif 300 <= condition_id < 400:  return "🌦️"
    elif 500 <= condition_id < 600:  return "🌧️"
    elif 600 <= condition_id < 700:  return "❄️"
    elif 700 <= condition_id < 800:  return "🌫️"
    elif condition_id == 800:        return "☀️"
    elif 801 <= condition_id <= 804: return "⛅"
    else:                            return "🌡️"


def give_weather_advice(temp: float, humidity: int, wind_speed: float, weather_desc: str) -> None:
    """Give practical tips based on current conditions. Show at most 3."""
    advice: List[str] = []

    if   temp < 0:   advice.append("❄️  Freezing — wear heavy winter clothing.")
    elif temp < 10:  advice.append("🧥  Cold — bring a jacket.")
    elif temp < 20:  advice.append("👕  Cool — comfortable for outdoor activities.")
    elif temp < 30:  advice.append("☀️  Warm — enjoy the sunshine!")
    else:            advice.append("🥵  Hot — stay hydrated and use sunscreen.")

    desc_lower = weather_desc.lower()
    if   "rain"    in desc_lower: advice.append("☔  Rain expected — bring an umbrella.")
    elif "snow"    in desc_lower: advice.append("⛄  Snowfall — wear waterproof boots.")
    elif "thunder" in desc_lower: advice.append("⚡  Thunderstorm — stay indoors if possible.")
    elif "clear"   in desc_lower: advice.append("🕶️  Clear skies — great for outdoor activities.")
    elif "fog"     in desc_lower or "mist" in desc_lower:
        advice.append("🌫️  Low visibility — drive carefully.")

    if wind_speed > 10:  advice.append("💨  Windy — secure loose objects outside.")
    if humidity   > 80:  advice.append("💧  High humidity — it may feel hotter than it is.")

    for tip in advice[:3]:
        print(f"    {tip}")


# ── History ────────────────────────────────────────────────────────────────────

def save_weather_to_file(data: Dict, filename: str = "weather_history.txt") -> None:
    """Append a one-line summary to the history file."""
    try:
        with open(filename, "a") as f:
            ts      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            city    = data.get("name", "Unknown")
            country = data.get("sys", {}).get("country", "")
            temp    = data.get("main", {}).get("temp", 0)
            desc    = (data.get("weather") or [{}])[0].get("description", "?")
            f.write(f"{ts} | {city}, {country} | {temp:.1f}°C | {desc}\n")
        print(f"{Fore.GREEN}✅  Saved to {filename}{Fore.RESET}")
    except IOError as e:
        print(f"{Fore.RED}❌  Could not save: {e}{Fore.RESET}")


def show_weather_history(filename: str = "weather_history.txt") -> None:
    """Print the last 10 entries from the history file."""
    if not os.path.exists(filename):
        print(f"{Fore.YELLOW}📭  No history file found yet.{Fore.RESET}")
        return
    try:
        with open(filename) as f:
            lines = f.readlines()
        if not lines:
            print(f"{Fore.YELLOW}📭  History file is empty.{Fore.RESET}")
            return
        print(f"\n{Fore.CYAN}{'═' * 60}{Fore.RESET}")
        print(f"  {Fore.YELLOW}📜  WEATHER HISTORY (last 10 entries){Fore.RESET}")
        print(f"{Fore.CYAN}{'═' * 60}{Fore.RESET}")
        for line in lines[-10:]:
            print(f"  {line.rstrip()}")
        print(f"{Fore.CYAN}{'═' * 60}{Fore.RESET}\n")
    except IOError as e:
        print(f"{Fore.RED}❌  Could not read history: {e}{Fore.RESET}")


# ── Setup ──────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """
    Return the API key.
    Priority: 1) environment variable  2) hardcoded fallback
    This pattern is common in real apps — secrets come from env vars in production.
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if api_key:
        print(f"{Fore.GREEN}🔑  Using API key from environment variable.{Fore.RESET}")
        return api_key

    # Use hardcoded fallback for convenience while learning
    print(f"{Fore.YELLOW}⚠️   Using fallback API key (set OPENWEATHER_API_KEY env var for production).{Fore.RESET}")
    return FALLBACK_API_KEY


def show_help() -> None:
    print(f"""
{Fore.CYAN}WEATHER CLI — HELP{Fore.RESET}
{'─' * 40}
Usage:
  python weather_app.py [city] [options]

Options:
  -h  --help       Show this message
  -s  --save       Save result to weather_history.txt
  -H  --history    Show saved history
  -f  --forecast   Show 5-day forecast

Examples:
  python weather_app.py Mumbai
  python weather_app.py "New York" --save
  python weather_app.py London --forecast
  python weather_app.py --history

Default city: {DEFAULT_CITY}

Tip: Set your own API key with:
  export OPENWEATHER_API_KEY="your_key"
""")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args         = sys.argv[1:]
    city         = DEFAULT_CITY
    save_to_file = False
    show_history = False
    show_forecast= False

    # Simple manual argument parsing — good exercise to understand sys.argv
    for arg in args:
        if   arg in ("-h", "--help"):     show_help(); return
        elif arg in ("-s", "--save"):     save_to_file  = True
        elif arg in ("-H", "--history"):  show_history  = True
        elif arg in ("-f", "--forecast"): show_forecast = True
        elif not arg.startswith("-"):     city = arg

    if show_history:
        show_weather_history()
        return

    api_key = get_api_key()

    if not validate_city(city):
        print(f"{Fore.RED}❌  Invalid city name: '{city}'{Fore.RESET}")
        print("    Use only letters, spaces, hyphens, apostrophes, or periods.")
        return

    # ── Current weather ───────────────────────────────────────────────────────
    print(f"{Fore.CYAN}🔍  Fetching weather for {city}...{Fore.RESET}")
    weather_data = get_weather_data(city, api_key)

    if weather_data:
        display_weather(weather_data)
        if save_to_file:
            save_weather_to_file(weather_data)

    # ── Forecast (optional) ───────────────────────────────────────────────────
    if show_forecast:
        print(f"{Fore.CYAN}📅  Fetching 5-day forecast for {city}...{Fore.RESET}")
        forecast_data = get_forecast_data(city, api_key)
        if forecast_data:
            display_forecast(forecast_data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋  Goodbye!{Fore.RESET}")
    except Exception as e:
        # Catch-all so the user always gets a readable error instead of a traceback
        print(f"{Fore.RED}❌  Unexpected error: {e}{Fore.RESET}")
        raise   # re-raise during development so you can see the full traceback