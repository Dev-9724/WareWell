from copy import deepcopy


DEFAULT_WEIGHTS = {
    "weather_fit": 0.35,
    "formality_match": 0.25,
    "colour_harmony": 0.20,
    "usage_balance": 0.10,
    "comfort": 0.10,
}


VALID_KEYS = list(DEFAULT_WEIGHTS.keys())


def merge_with_defaults(weights: dict | None) -> dict:
    """
    Ensure all expected weight keys exist.
    """
    merged = deepcopy(DEFAULT_WEIGHTS)

    if weights:
        for key, value in weights.items():
            if key in merged:
                try:
                    merged[key] = float(value)
                except (TypeError, ValueError):
                    pass

    return merged


def normalize_weights(weights: dict) -> dict:
    """
    Make sure all weights sum to 1.0
    """
    total = sum(weights.values())
    if total <= 0:
        return deepcopy(DEFAULT_WEIGHTS)

    return {k: round(v / total, 4) for k, v in weights.items()}


def normalize_rating(rating: str | None) -> str:
    """
    Make feedback safer and more flexible.
    """
    if not rating:
        return ""

    value = str(rating).strip().lower()

    aliases = {
        "perfect": "perfect",
        "excellent": "perfect",
        "good": "okay",
        "okay": "okay",
        "ok": "okay",
        "average": "okay",
        "not_suitable": "not_suitable",
        "bad": "not_suitable",
        "poor": "not_suitable",
    }

    return aliases.get(value, value)


def adapt_weights(current_weights: dict, rating: str) -> dict:
    """
    Beginner-friendly learning logic.

    perfect:
        increase weather + formality + colour slightly

    okay:
        tiny increase to comfort and usage balance

    not_suitable:
        reduce weather + formality slightly, increase comfort + usage
    """
    weights = merge_with_defaults(current_weights)
    rating_key = normalize_rating(rating)

    if rating_key == "perfect":
        weights["weather_fit"] += 0.02
        weights["formality_match"] += 0.02
        weights["colour_harmony"] += 0.01

    elif rating_key == "okay":
        weights["usage_balance"] += 0.01
        weights["comfort"] += 0.01

    elif rating_key == "not_suitable":
        weights["weather_fit"] -= 0.02
        weights["formality_match"] -= 0.02
        weights["comfort"] += 0.03
        weights["usage_balance"] += 0.01

    for key in VALID_KEYS:
        if weights[key] < 0.01:
            weights[key] = 0.01

    return normalize_weights(weights)


def adapt_weights_with_summary(current_weights: dict, rating: str) -> dict:
    """
    Optional helper if you want to store what changed for debugging or explanation.
    """
    before = merge_with_defaults(current_weights)
    after = adapt_weights(before, rating)

    changes = {}
    for key in VALID_KEYS:
        changes[key] = round(after[key] - before[key], 4)

    return {
        "previous_weights": before,
        "updated_weights": after,
        "rating_used": normalize_rating(rating),
        "changes": changes,
    }