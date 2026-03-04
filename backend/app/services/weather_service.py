import os
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHERAPI_KEY")
BASE_URL = os.getenv("WEATHERAPI_BASE_URL", "http://api.weatherapi.com/v1")


class WeatherServiceError(Exception):
    """Raised when the external weather provider fails."""
    pass


def _normalize_condition(condition_text: str) -> str:
    """
    Convert WeatherAPI 'text' into simple categories used by our algorithm.
    This helps the Constraint Engine later.
    """
    txt = (condition_text or "").strip().lower()

    if any(x in txt for x in ["thunder", "storm"]):
        return "Storm"
    if any(x in txt for x in ["rain", "drizzle", "shower", "sleet"]):
        return "Rain"
    if any(x in txt for x in ["snow", "blizzard", "ice", "hail"]):
        return "Snow"
    if any(x in txt for x in ["mist", "fog", "haze"]):
        return "Mist"
    if any(x in txt for x in ["cloud", "overcast"]):
        return "Cloudy"
    if any(x in txt for x in ["sun", "clear"]):
        return "Clear"

    # fallback (still predictable)
    return "Other"


def fetch_current_weather(city: str) -> dict:
    """
    Fetch current weather from WeatherAPI.com and return a normalized snapshot dict.

    WeatherAPI endpoint:
    GET {BASE_URL}/current.json?key=KEY&q=London&aqi=no
    """
    if not API_KEY:
        raise WeatherServiceError("WEATHERAPI_KEY missing in backend/.env")

    url = f"{BASE_URL}/current.json"
    params = {"key": API_KEY, "q": city, "aqi": "no"}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.HTTPError:
        # Try to show WeatherAPI's JSON error message if available
        try:
            err = r.json()
            raise WeatherServiceError(f"WeatherAPI error: {err}")
        except Exception:
            raise WeatherServiceError(f"WeatherAPI HTTP error: {r.status_code}")
    except requests.RequestException as e:
        raise WeatherServiceError(f"WeatherAPI request failed: {e}")

    current = data.get("current") or {}
    location = data.get("location") or {}

    condition_text = (current.get("condition") or {}).get("text", "Unknown")
    condition = _normalize_condition(condition_text)

    # Precip in mm (current total)
    precip_mm = float(current.get("precip_mm", 0.0) or 0.0)

    # wind_kph exists; we store as float (kph)
    wind_kph = float(current.get("wind_kph", 0.0) or 0.0)

    snapshot = {
        "temperature": float(current.get("temp_c", 0.0) or 0.0),
        "humidity": int(current.get("humidity", 0) or 0),
        "wind": wind_kph,
        "rain": precip_mm,
        "condition": condition,          # normalized category (Clear/Rain/Cloudy/Mist/Snow/Storm/Other)
        "city": str(location.get("name") or city),
        "timestamp": datetime.now(timezone.utc),
        "source": "weatherapi"
    }

    return snapshot