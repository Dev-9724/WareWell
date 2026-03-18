from typing import List, Dict


def constraint_satisfaction_rate(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    valid = 0

    for outfit in outfits:
        categories = {item.get("category") for item in outfit.get("items", [])}

        if "top" in categories and "bottom" in categories and "shoes" in categories:
            valid += 1

    return round(valid / len(outfits), 4)


def diversity_index(outfits: List[dict]) -> float:
    if not outfits:
        return 0.0

    colours = set()

    for outfit in outfits:
        for item in outfit.get("items", []):
            colour = item.get("colour_primary")
            if colour:
                colours.add(colour.lower())

    return round(len(colours) / 10.0, 4)


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


def calculate_metrics(outfits: List[dict], total_valid_items: int) -> Dict:

    return {
        "outfit_count": len(outfits),
        "constraint_satisfaction_rate": constraint_satisfaction_rate(outfits),
        "diversity_index": diversity_index(outfits),
        "repetition_rate": repetition_rate(outfits),
        "wardrobe_utilisation": wardrobe_utilisation(outfits, total_valid_items),
        "average_outfit_size": average_outfit_size(outfits),
    }