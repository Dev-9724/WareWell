from app.services.outfit_generator import generate_outfits


def test_generate_outfits_creates_valid_combinations():
    valid_items = [
        {"id": "1", "category": "top", "colour_primary": "blue"},
        {"id": "2", "category": "bottom", "colour_primary": "black"},
        {"id": "3", "category": "shoes", "colour_primary": "white"},
        {"id": "4", "category": "outerwear", "colour_primary": "navy"},
    ]

    result = generate_outfits(valid_items)

    assert result["can_generate_outfits"] is True
    assert result["outfit_count"] >= 1
    assert len(result["outfits"]) >= 1


def test_generate_outfits_fails_when_required_category_missing():
    valid_items = [
        {"id": "1", "category": "top", "colour_primary": "blue"},
        {"id": "2", "category": "bottom", "colour_primary": "black"},
    ]

    result = generate_outfits(valid_items)

    assert result["can_generate_outfits"] is False
    assert "shoes" in result["missing_required_categories"]
    assert result["outfit_count"] == 0