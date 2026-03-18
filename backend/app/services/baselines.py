import random
from typing import List, Dict, Any

from app.services.scoring_engine import rank_outfits


def random_baseline(outfits: List[dict], top_k: int = 5) -> List[dict]:
    """
    Randomly select outfits from generated outfit candidates.
    """
    if not outfits:
        return []

    shuffled = outfits.copy()
    random.shuffle(shuffled)
    selected = shuffled[:top_k]

    # add a label so we know these are random outputs
    return [
        {
            "model": "random_baseline",
            "outfit_id": outfit.get("outfit_id"),
            "items": outfit.get("items", []),
            "categories": outfit.get("categories", []),
        }
        for outfit in selected
    ]


def rule_only_baseline(outfits: List[dict], top_k: int = 5) -> List[dict]:
    """
    Rule-only baseline:
    just take the first valid outfits after constraints/generation.
    No ranking.
    """
    if not outfits:
        return []

    selected = outfits[:top_k]

    return [
        {
            "model": "rule_only_baseline",
            "outfit_id": outfit.get("outfit_id"),
            "items": outfit.get("items", []),
            "categories": outfit.get("categories", []),
        }
        for outfit in selected
    ]


def hybrid_baseline(
    outfits: List[dict],
    weather: Dict[str, Any],
    top_k: int = 5,
    target_formality: float = 5.0,
    weights: Dict[str, float] | None = None,
) -> List[dict]:
    """
    Hybrid baseline:
    rank outfits using the scoring engine and return top_k.
    """
    if not outfits:
        return []

    ranked = rank_outfits(
        outfits=outfits,
        weather=weather,
        top_k=top_k,
        target_formality=target_formality,
        weights=weights,
    )

    for outfit in ranked:
        outfit["model"] = "hybrid_model"

    return ranked