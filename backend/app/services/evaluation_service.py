import random
from typing import List, Dict, Any


def random_baseline(outfits: List[dict], top_k: int = 5) -> List[dict]:
    """
    Randomly select outfits as baseline.
    """
    if not outfits:
        return []

    shuffled = outfits.copy()
    random.shuffle(shuffled)
    return shuffled[:top_k]


def rule_only_baseline(outfits: List[dict], top_k: int = 5) -> List[dict]:
    """
    Rule-only baseline:
    just take the first valid outfits without scoring.
    """
    if not outfits:
        return []

    return outfits[:top_k]


def hybrid_model(ranked_outfits: List[dict], top_k: int = 5) -> List[dict]:
    """
    Hybrid model:
    already ranked by scoring engine, so just return top_k.
    """
    if not ranked_outfits:
        return []

    return ranked_outfits[:top_k]


def evaluate_outfit_set(outfits: List[dict]) -> Dict[str, Any]:
    """
    Simple evaluation metrics for a returned outfit set.
    """
    if not outfits:
        return {
            "outfit_count": 0,
            "unique_item_count": 0,
            "category_coverage": 0,
        }

    unique_items = set()
    categories = set()

    for outfit in outfits:
        for item in outfit.get("items", []):
            item_id = item.get("id") or item.get("_id")
            if item_id:
                unique_items.add(str(item_id))

            category = item.get("category")
            if category:
                categories.add(category)

    return {
        "outfit_count": len(outfits),
        "unique_item_count": len(unique_items),
        "category_coverage": len(categories),
    }