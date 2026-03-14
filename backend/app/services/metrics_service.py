def constraint_satisfaction_rate(outfits):
    """
    % of outfits satisfying constraints
    """
    if not outfits:
        return 0

    valid = [o for o in outfits if o.get("valid", True)]

    return len(valid) / len(outfits)


def diversity_index(outfits):
    """
    Simple diversity metric based on colour diversity
    """
    colours = set()

    for outfit in outfits:
        for item in outfit["items"]:
            colours.add(item.get("colour_primary"))

    return len(colours)


def wardrobe_utilisation(outfits):
    """
    Measures how many unique wardrobe items are used
    """
    items = set()

    for outfit in outfits:
        for item in outfit["items"]:
            items.add(item["id"])

    return len(items)