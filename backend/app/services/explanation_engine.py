from typing import Dict, List, Any


def describe_score(label: str, value: float) -> str:
    """
    Convert a numeric score into a readable explanation sentence.
    """
    if value >= 0.9:
        level = "very strong"
    elif value >= 0.75:
        level = "strong"
    elif value >= 0.6:
        level = "moderate"
    else:
        level = "limited"

    label_map = {
        "weather_fit": "weather suitability",
        "formality_match": "formality alignment",
        "colour_harmony": "colour harmony",
        "usage_balance": "wardrobe usage balance",
        "comfort": "comfort suitability",
    }

    readable_label = label_map.get(label, label.replace("_", " "))
    return f"{readable_label.capitalize()} is {level} ({value:.2f})."


def build_main_reason(score_breakdown: Dict[str, float]) -> str:
    """
    Use the strongest criterion as the main explanation.
    """
    if not score_breakdown:
        return "This outfit is recommended based on the available scoring criteria."

    best_key = max(score_breakdown, key=score_breakdown.get)

    reason_map = {
        "weather_fit": "it is highly suitable for the current weather",
        "formality_match": "it closely matches the requested occasion formality",
        "colour_harmony": "its colours work together well",
        "usage_balance": "it helps improve wardrobe utilisation by using less-worn items",
        "comfort": "it offers strong comfort for the current conditions",
    }

    return f"This outfit is recommended because {reason_map.get(best_key, 'it achieved a strong overall score')}."


def generate_outfit_explanation(
    outfit: Dict[str, Any],
    weather: Dict[str, Any],
    occasion: str | None = None,
    target_formality: float | None = None,
) -> Dict[str, Any]:
    """
    Generate human-readable explanation for one ranked outfit.
    """
    score_breakdown = outfit.get("score_breakdown", {}) or {}
    categories = outfit.get("categories", []) or []
    score = float(outfit.get("score", 0.0) or 0.0)

    summary = build_main_reason(score_breakdown)

    detail_lines: List[str] = []
    for key, value in score_breakdown.items():
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            numeric_value = 0.0
        detail_lines.append(describe_score(key, numeric_value))

    category_text = ", ".join(categories) if categories else "items"

    city = weather.get("city", "the selected city")
    temperature = weather.get("temperature", "unknown")
    condition = weather.get("condition", "unknown")

    weather_text = (
        f"The recommendation was generated for {city} "
        f"with temperature {temperature}°C and condition {condition}."
    )

    occasion_text = None
    if occasion and target_formality is not None:
        occasion_text = (
            f"The selected occasion was '{occasion}', using a target formality of "
            f"{float(target_formality):.1f}."
        )
    elif occasion:
        occasion_text = f"The selected occasion was '{occasion}'."
    elif target_formality is not None:
        occasion_text = f"A target formality score of {float(target_formality):.1f} was used."

    return {
        "outfit_id": outfit.get("outfit_id"),
        "score": score,
        "summary": summary,
        "details": detail_lines,
        "categories_used": category_text,
        "weather_context": weather_text,
        "occasion_context": occasion_text,
        "items": outfit.get("items", []),
        "score_breakdown": score_breakdown,
    }


def generate_explanations_for_ranked_outfits(
    ranked_outfits: List[Dict[str, Any]],
    weather: Dict[str, Any],
    occasion: str | None = None,
    target_formality: float | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate explanations for multiple ranked outfits.
    """
    explained: List[Dict[str, Any]] = []

    for outfit in ranked_outfits:
        explained.append(
            generate_outfit_explanation(
                outfit=outfit,
                weather=weather,
                occasion=occasion,
                target_formality=target_formality,
            )
        )

    return explained