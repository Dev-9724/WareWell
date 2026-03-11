from typing import List, Dict, Any
from itertools import product


def group_items_by_category(items: List[dict]) -> Dict[str, List[dict]]:
    grouped = {
        "top": [],
        "bottom": [],
        "shoes": [],
        "outerwear": [],
        "accessory": [],
    }

    for item in items:
        category = str(item.get("category", "")).strip().lower()
        if category in grouped:
            grouped[category].append(item)

    return grouped


def generate_outfits(valid_items: List[dict]) -> Dict[str, Any]:
    """
    Generate outfit combinations from valid wardrobe items.

    Required:
    - top
    - bottom
    - shoes

    Optional:
    - outerwear
    - accessory
    """
    grouped = group_items_by_category(valid_items)

    tops = grouped["top"]
    bottoms = grouped["bottom"]
    shoes = grouped["shoes"]
    outerwears = grouped["outerwear"]
    accessories = grouped["accessory"]

    # Must have required categories
    if not tops or not bottoms or not shoes:
        missing = []
        if not tops:
            missing.append("top")
        if not bottoms:
            missing.append("bottom")
        if not shoes:
            missing.append("shoes")

        return {
            "can_generate_outfits": False,
            "missing_required_categories": missing,
            "outfit_count": 0,
            "outfits": [],
        }

    # Optional categories can be absent
    outerwear_options = [None] + outerwears
    accessory_options = [None] + accessories

    outfits = []
    outfit_id = 1

    for top, bottom, shoe, outerwear, accessory in product(
        tops, bottoms, shoes, outerwear_options, accessory_options
    ):
        items = [top, bottom, shoe]
        if outerwear is not None:
            items.append(outerwear)
        if accessory is not None:
            items.append(accessory)

        outfits.append({
            "outfit_id": outfit_id,
            "items": items,
            "categories": [item["category"] for item in items],
        })
        outfit_id += 1

    return {
        "can_generate_outfits": True,
        "missing_required_categories": [],
        "outfit_count": len(outfits),
        "outfits": outfits,
    }