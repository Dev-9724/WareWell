from typing import List, Dict


REQUIRED_CORE_CATEGORIES = {"top", "bottom", "shoes"}


def normalise_category(category: str | None) -> str:
    if not category:
        return ""
    return str(category).strip().lower()


def constraint_satisfaction_rate(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    valid = 0

    for outfit in outfits:
        categories = {
            normalise_category(item.get("category"))
            for item in outfit.get("items", [])
        }

        if REQUIRED_CORE_CATEGORIES.issubset(categories):
            valid += 1

    return round(valid / len(outfits), 4)


def diversity_index(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    unique_item_ids = set()
    total_item_slots = 0

    for outfit in outfits:
        items = outfit.get("items", [])
        total_item_slots += len(items)

        for item in items:
            item_id = item.get("id") or item.get("_id")
            if item_id:
                unique_item_ids.add(str(item_id))

    if total_item_slots == 0:
        return 0.0

    return round(len(unique_item_ids) / total_item_slots, 4)


def repetition_rate(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    all_ids = []

    for outfit in outfits:
        for item in outfit.get("items", []):
            item_id = item.get("id") or item.get("_id")
            if item_id:
                all_ids.append(str(item_id))

    if not all_ids:
        return 0.0

    unique_ids = set(all_ids)
    repetition = 1 - (len(unique_ids) / len(all_ids))

    return round(repetition, 4)


def wardrobe_utilisation(outfits: List[dict], total_valid_items: int) -> float:
    if not outfits or total_valid_items == 0:
        return 0.0

    used_ids = set()

    for outfit in outfits:
        for item in outfit.get("items", []):
            item_id = item.get("id") or item.get("_id")
            if item_id:
                used_ids.add(str(item_id))

    return round(len(used_ids) / total_valid_items, 4)


def average_outfit_size(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    sizes = [len(outfit.get("items", [])) for outfit in outfits]
    return round(sum(sizes) / len(sizes), 4)


def explanation_completeness(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    explained = 0

    for outfit in outfits:
        if outfit.get("explanation") or outfit.get("score_breakdown") or outfit.get("reasons"):
            explained += 1

    return round(explained / len(outfits), 4)


def calculate_metrics(outfits: List[dict], total_valid_items: int) -> Dict:
    return {
        "outfit_count": len(outfits),
        "constraint_satisfaction_rate": constraint_satisfaction_rate(outfits),
        "diversity_index": diversity_index(outfits),
        "repetition_rate": repetition_rate(outfits),
        "wardrobe_utilisation": wardrobe_utilisation(outfits, total_valid_items),
        "average_outfit_size": average_outfit_size(outfits),
        "explanation_completeness": explanation_completeness(outfits),
    }