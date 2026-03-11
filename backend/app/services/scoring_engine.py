from typing import List, Dict, Any


DEFAULT_WEIGHTS = {
    "weather_fit": 0.35,
    "formality_match": 0.25,
    "colour_harmony": 0.20,
    "usage_balance": 0.10,
    "comfort": 0.10,
}


OCCASION_TO_FORMALITY = {
    "casual": 3.5,
    "smart-casual": 5.0,
    "office": 6.5,
    "formal": 8.5,
    "party": 6.0,
    "gym": 2.0,
}


NEUTRAL_COLOURS = {"black", "white", "grey", "gray", "beige", "navy", "brown"}


def get_target_formality(occasion: str | None = None, fallback: float = 5.0) -> float:
    """
    Convert occasion into a target formality score.
    If no occasion is given, use fallback.
    """
    if not occasion:
        return fallback

    key = occasion.strip().lower()
    return OCCASION_TO_FORMALITY.get(key, fallback)


def score_weather_fit(outfit_items: List[dict], weather: dict) -> float:
    current_temp = weather.get("temperature", 0.0)

    scores = []
    for item in outfit_items:
        item_min = item.get("temperature_min")
        item_max = item.get("temperature_max")

        if item_min is None or item_max is None:
            scores.append(0.0)
            continue

        if item_min <= current_temp <= item_max:
            scores.append(1.0)
        else:
            if current_temp < item_min:
                diff = item_min - current_temp
            else:
                diff = current_temp - item_max

            score = max(0.0, 1.0 - (diff / 10.0))
            scores.append(score)

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


def score_formality_match(outfit_items: List[dict], target_formality: float = 5.0) -> float:
    if not outfit_items:
        return 0.0

    formality_values = [item.get("formality_level", 0) for item in outfit_items]
    avg_formality = sum(formality_values) / len(formality_values)

    diff = abs(avg_formality - target_formality)
    score = max(0.0, 1.0 - (diff / 10.0))
    return score


def score_colour_harmony(outfit_items: List[dict]) -> float:
    colours = []
    for item in outfit_items:
        primary = str(item.get("colour_primary", "")).strip().lower()
        if primary:
            colours.append(primary)

    if not colours:
        return 0.0

    unique_colours = set(colours)
    neutral_count = sum(1 for c in colours if c in NEUTRAL_COLOURS)

    if len(unique_colours) == 1:
        return 0.95
    if neutral_count >= len(colours) - 1:
        return 0.90
    if len(unique_colours) == 2:
        return 0.85
    if len(unique_colours) == 3:
        return 0.70

    return 0.50


def score_usage_balance(outfit_items: List[dict]) -> float:
    if not outfit_items:
        return 0.0

    wear_counts = [item.get("wear_count", 0) for item in outfit_items]
    avg_wear = sum(wear_counts) / len(wear_counts)

    score = max(0.0, 1.0 - (avg_wear / 20.0))
    return score


def score_comfort(outfit_items: List[dict], weather: dict) -> float:
    temp = weather.get("temperature", 0.0)
    base = score_weather_fit(outfit_items, weather)

    categories = [str(item.get("category", "")).lower() for item in outfit_items]
    has_outerwear = "outerwear" in categories

    if temp <= 10 and has_outerwear:
        base = min(1.0, base + 0.1)

    return min(1.0, base)


def score_outfit(
    outfit: dict,
    weather: dict,
    weights: Dict[str, float] = DEFAULT_WEIGHTS,
    target_formality: float = 5.0,
) -> Dict[str, Any]:
    items = outfit.get("items", [])

    weather_fit = score_weather_fit(items, weather)
    formality_match = score_formality_match(items, target_formality=target_formality)
    colour_harmony = score_colour_harmony(items)
    usage_balance = score_usage_balance(items)
    comfort = score_comfort(items, weather)

    total_score = (
        weights["weather_fit"] * weather_fit
        + weights["formality_match"] * formality_match
        + weights["colour_harmony"] * colour_harmony
        + weights["usage_balance"] * usage_balance
        + weights["comfort"] * comfort
    )

    return {
        "outfit_id": outfit.get("outfit_id"),
        "items": items,
        "categories": outfit.get("categories", []),
        "score": round(total_score, 4),
        "score_breakdown": {
            "weather_fit": round(weather_fit, 4),
            "formality_match": round(formality_match, 4),
            "colour_harmony": round(colour_harmony, 4),
            "usage_balance": round(usage_balance, 4),
            "comfort": round(comfort, 4),
        },
    }


def rank_outfits(
    outfits: List[dict],
    weather: dict,
    top_k: int = 5,
    target_formality: float = 5.0,
    weights: Dict[str, float] = DEFAULT_WEIGHTS,
) -> List[dict]:
    scored = [
        score_outfit(
            outfit,
            weather=weather,
            target_formality=target_formality,
            weights=weights,
        )
        for outfit in outfits
    ]

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]