from copy import deepcopy


DEFAULT_WEIGHTS = {
    "weather_fit": 0.35,
    "formality_match": 0.25,
    "colour_harmony": 0.20,
    "usage_balance": 0.10,
    "comfort": 0.10,
}


def normalize_weights(weights: dict) -> dict:
    """
    Make sure all weights sum to 1.0
    """
    total = sum(weights.values())
    if total == 0:
        return deepcopy(DEFAULT_WEIGHTS)

    return {k: round(v / total, 4) for k, v in weights.items()}


def adapt_weights(current_weights: dict, rating: str) -> dict:
    """
    Very simple beginner-friendly learning logic.

    perfect:
        increase weather + formality + colour slightly
    okay:
        tiny increase to comfort and usage balance
    not_suitable:
        reduce weather + formality slightly, increase comfort
    """
    weights = deepcopy(current_weights)

    if rating == "perfect":
        weights["weather_fit"] += 0.02
        weights["formality_match"] += 0.02
        weights["colour_harmony"] += 0.01

    elif rating == "okay":
        weights["usage_balance"] += 0.01
        weights["comfort"] += 0.01

    elif rating == "not_suitable":
        weights["weather_fit"] -= 0.02
        weights["formality_match"] -= 0.02
        weights["comfort"] += 0.03
        weights["usage_balance"] += 0.01

    # prevent negative values
    for key in weights:
        if weights[key] < 0.01:
            weights[key] = 0.01

    return normalize_weights(weights)