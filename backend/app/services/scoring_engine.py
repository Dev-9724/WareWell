from typing import List, Dict, Any


DEFAULT_WEIGHTS = {
    "weather_fit": 0.30,
    "formality_match": 0.25,
    "colour_harmony": 0.18,
    "usage_balance": 0.17,
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

    key = str(occasion).strip().lower()
    return OCCASION_TO_FORMALITY.get(key, fallback)


def get_active_weights(weights: Dict[str, float] | None = None) -> Dict[str, float]:
    """
    Merge incoming weights with defaults so scoring never fails
    if a learned-weight document is incomplete.
    """
    merged = DEFAULT_WEIGHTS.copy()

    if weights:
        for key, value in weights.items():
            if key in merged:
                merged[key] = float(value)

    return merged


def normalise_category(category: str | None) -> str:
    if not category:
        return ""
    return str(category).strip().lower()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_weather_fit(outfit_items: List[dict], weather: dict) -> float:
    current_temp = safe_float(weather.get("temperature"), 0.0)

    scores = []
    for item in outfit_items:
        item_min = item.get("temperature_min")
        item_max = item.get("temperature_max")

        if item_min is None or item_max is None:
            scores.append(0.5)
            continue

        item_min = safe_float(item_min, 0.0)
        item_max = safe_float(item_max, 0.0)

        if item_min <= current_temp <= item_max:
            scores.append(1.0)
        else:
            if current_temp < item_min:
                diff = item_min - current_temp
            else:
                diff = current_temp - item_max

            score = max(0.0, 1.0 - (diff / 12.0))
            scores.append(score)

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 4)


def score_formality_match(outfit_items: List[dict], target_formality: float = 5.0) -> float:
    if not outfit_items:
        return 0.0

    formality_values = [
        safe_float(item.get("formality_level"), 0.0)
        for item in outfit_items
    ]

    avg_formality = sum(formality_values) / len(formality_values)

    # more sensitive than dividing by 10,
    # since wardrobe formality usually sits in a smaller practical range
    diff = abs(avg_formality - target_formality)
    score = max(0.0, 1.0 - (diff / 6.0))

    return round(score, 4)


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
        return 0.72

    return 0.50


def score_usage_balance(outfit_items: List[dict]) -> float:
    """
    Reward outfits that reuse less-worn items, supporting wardrobe rotation.
    """
    if not outfit_items:
        return 0.0

    wear_counts = [safe_float(item.get("wear_count"), 0.0) for item in outfit_items]
    avg_wear = sum(wear_counts) / len(wear_counts)

    # lower average wear count = better sustainability / balance
    base_score = max(0.0, 1.0 - (avg_wear / 15.0))

    # small bonus if outfit mixes wear frequencies instead of always same-used items
    unique_wears = len(set(int(w) for w in wear_counts))
    variation_bonus = min(0.1, unique_wears * 0.02)

    return round(min(1.0, base_score + variation_bonus), 4)


def score_comfort(outfit_items: List[dict], weather: dict) -> float:
    temp = safe_float(weather.get("temperature"), 0.0)
    rain = bool(weather.get("rain", False))
    base = score_weather_fit(outfit_items, weather)

    categories = [normalise_category(item.get("category")) for item in outfit_items]
    has_outerwear = "outerwear" in categories
    has_shoes = "shoes" in categories

    if temp <= 10 and has_outerwear:
        base += 0.08

    if rain:
        rain_ready_count = sum(1 for item in outfit_items if item.get("rain_suitable") is True)
        if rain_ready_count > 0:
            base += 0.05
        else:
            base -= 0.08

    if has_shoes:
        base += 0.02

    return round(max(0.0, min(1.0, base)), 4)


def build_explanation(
    score_breakdown: Dict[str, float],
    target_formality: float,
) -> tuple[list[str], str]:
    reasons = []

    if score_breakdown["weather_fit"] >= 0.8:
        reasons.append("Strong weather suitability for current conditions")
    elif score_breakdown["weather_fit"] <= 0.4:
        reasons.append("Limited weather suitability")

    if score_breakdown["formality_match"] >= 0.8:
        reasons.append(f"Good formality alignment for target level {target_formality}")
    elif score_breakdown["formality_match"] <= 0.4:
        reasons.append("Weak occasion-formality alignment")

    if score_breakdown["colour_harmony"] >= 0.8:
        reasons.append("Colour combination is visually consistent")

    if score_breakdown["usage_balance"] >= 0.75:
        reasons.append("Supports sustainable wardrobe rotation")

    if score_breakdown["comfort"] >= 0.8:
        reasons.append("Comfort is likely to be high in the current weather")

    if not reasons:
        reasons.append("Balanced outfit with moderate overall suitability")

    explanation = "; ".join(reasons) + "."

    return reasons, explanation


def score_outfit(
    outfit: dict,
    weather: dict,
    weights: Dict[str, float] | None = None,
    target_formality: float = 5.0,
) -> Dict[str, Any]:
    items = outfit.get("items", [])
    active_weights = get_active_weights(weights)

    weather_fit = score_weather_fit(items, weather)
    formality_match = score_formality_match(items, target_formality=target_formality)
    colour_harmony = score_colour_harmony(items)
    usage_balance = score_usage_balance(items)
    comfort = score_comfort(items, weather)

    total_score = (
        active_weights["weather_fit"] * weather_fit
        + active_weights["formality_match"] * formality_match
        + active_weights["colour_harmony"] * colour_harmony
        + active_weights["usage_balance"] * usage_balance
        + active_weights["comfort"] * comfort
    )

    score_breakdown = {
        "weather_fit": round(weather_fit, 4),
        "formality_match": round(formality_match, 4),
        "colour_harmony": round(colour_harmony, 4),
        "usage_balance": round(usage_balance, 4),
        "comfort": round(comfort, 4),
    }

    reasons, explanation = build_explanation(
        score_breakdown=score_breakdown,
        target_formality=target_formality,
    )

    return {
        "outfit_id": outfit.get("outfit_id"),
        "items": items,
        "categories": outfit.get("categories", []),
        "score": round(total_score, 4),
        "score_percentage": round(total_score * 100, 2),
        "score_breakdown": score_breakdown,
        "reasons": reasons,
        "explanation": explanation,
        "weights_used": active_weights,
    }


def rank_outfits(
    outfits: List[dict],
    weather: dict,
    top_k: int = 5,
    target_formality: float = 5.0,
    weights: Dict[str, float] | None = None,
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

    scored.sort(
        key=lambda x: (
            x["score"],
            x["score_breakdown"]["weather_fit"],
            x["score_breakdown"]["formality_match"],
        ),
        reverse=True,
    )

    return scored[:top_k]