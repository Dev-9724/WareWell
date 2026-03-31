from typing import List, Dict, Any
from datetime import datetime


def get_season_from_month(month: int) -> str:
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"


def check_temperature(item: dict, temperature: float) -> tuple[bool, str | None]:
    item_min = item.get("temperature_min")
    item_max = item.get("temperature_max")

    if item_min is None or item_max is None:
        return False, "missing_temperature_range"

    TEMP_BUFFER = 3.0

    if temperature < (item_min - TEMP_BUFFER):
        return False, "too_cold_for_item"

    if temperature > (item_max + TEMP_BUFFER):
        return False, "too_hot_for_item"

    return True, None


def check_rain(item: dict, rain: float) -> tuple[bool, str | None]:
    rain_suitable = item.get("rain_suitable")

    if rain > 0 and rain_suitable is False:
        return False, "not_rain_suitable"

    return True, None


def check_season(item: dict, current_season: str) -> tuple[bool, str | None]:
    seasons = item.get("season", [])

    if not seasons:
        return False, "missing_season_data"

    if isinstance(seasons, str):
        seasons = [seasons]

    normalized_seasons = [str(s).strip().lower() for s in seasons]

    if current_season.lower() not in normalized_seasons:
        return False, "season_mismatch"

    return True, None


def apply_constraints(items: List[dict], weather_snapshot: dict) -> Dict[str, Any]:
    temperature = weather_snapshot.get("temperature")
    rain = weather_snapshot.get("rain", 0.0)
    timestamp = weather_snapshot.get("timestamp")

    if temperature is None:
        raise ValueError("Weather snapshot missing temperature")

    if timestamp is None:
        current_month = datetime.utcnow().month
    else:
        if isinstance(timestamp, str):
            current_month = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).month
        else:
            current_month = timestamp.month

    current_season = get_season_from_month(current_month)

    valid_items = []
    rejected_items = []

    for item in items:
        reasons = []

        ok_temp, reason_temp = check_temperature(item, temperature)
        if not ok_temp:
            reasons.append(reason_temp)

        ok_rain, reason_rain = check_rain(item, rain)
        if not ok_rain:
            reasons.append(reason_rain)

        ok_season, reason_season = check_season(item, current_season)
        if not ok_season:
            reasons.append(reason_season)

        if reasons:
            rejected_items.append({
                "id": str(item.get("_id")),
                "category": item.get("category"),
                "colour_primary": item.get("colour_primary"),
                "reasons": reasons
            })
        else:
            valid_items.append({
                "id": str(item.get("_id")),
                "user_id": item.get("user_id"),
                "category": item.get("category"),
                "colour_primary": item.get("colour_primary"),
                "colour_secondary": item.get("colour_secondary"),
                "formality_level": item.get("formality_level"),
                "season": item.get("season"),
                "temperature_min": item.get("temperature_min"),
                "temperature_max": item.get("temperature_max"),
                "rain_suitable": item.get("rain_suitable"),
                "wear_count": item.get("wear_count"),
                "last_worn_date": item.get("last_worn_date"),
                "cost": item.get("cost"),
                "image_url": item.get("image_url"),
                "created_at": item.get("created_at"),
            })

    return {
        "weather_used": {
            "temperature": temperature,
            "rain": rain,
            "season": current_season,
            "city": weather_snapshot.get("city"),
            "condition": weather_snapshot.get("condition"),
        },
        "valid_count": len(valid_items),
        "rejected_count": len(rejected_items),
        "valid_items": valid_items,
        "rejected_items": rejected_items,
    }