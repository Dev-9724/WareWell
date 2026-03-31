from app.services.scoring_engine import score_outfit, rank_outfits


def test_score_outfit_returns_score_and_breakdown():
    outfit = {
        "outfit_id": 1,
        "items": [
            {
                "id": "1",
                "category": "top",
                "colour_primary": "blue",
                "formality_level": 5,
                "temperature_min": 5,
                "temperature_max": 15,
                "wear_count": 1,
            },
            {
                "id": "2",
                "category": "bottom",
                "colour_primary": "black",
                "formality_level": 6,
                "temperature_min": 5,
                "temperature_max": 15,
                "wear_count": 2,
            },
            {
                "id": "3",
                "category": "shoes",
                "colour_primary": "white",
                "formality_level": 5,
                "temperature_min": 0,
                "temperature_max": 20,
                "wear_count": 0,
            },
        ],
        "categories": ["top", "bottom", "shoes"],
    }

    weather = {
        "temperature": 9.0,
        "city": "London",
        "condition": "Mist",
    }

    result = score_outfit(outfit, weather)

    assert "score" in result
    assert "score_breakdown" in result
    assert result["score"] > 0
    assert "weather_fit" in result["score_breakdown"]


def test_rank_outfits_returns_sorted_top_k():
    outfits = [
        {
            "outfit_id": 1,
            "items": [
                {
                    "id": "1",
                    "category": "top",
                    "colour_primary": "blue",
                    "formality_level": 5,
                    "temperature_min": 5,
                    "temperature_max": 15,
                    "wear_count": 1,
                },
                {
                    "id": "2",
                    "category": "bottom",
                    "colour_primary": "black",
                    "formality_level": 5,
                    "temperature_min": 5,
                    "temperature_max": 15,
                    "wear_count": 1,
                },
                {
                    "id": "3",
                    "category": "shoes",
                    "colour_primary": "white",
                    "formality_level": 5,
                    "temperature_min": 0,
                    "temperature_max": 20,
                    "wear_count": 1,
                },
            ],
            "categories": ["top", "bottom", "shoes"],
        },
        {
            "outfit_id": 2,
            "items": [
                {
                    "id": "4",
                    "category": "top",
                    "colour_primary": "red",
                    "formality_level": 2,
                    "temperature_min": 20,
                    "temperature_max": 30,
                    "wear_count": 10,
                },
                {
                    "id": "5",
                    "category": "bottom",
                    "colour_primary": "green",
                    "formality_level": 2,
                    "temperature_min": 20,
                    "temperature_max": 30,
                    "wear_count": 10,
                },
                {
                    "id": "6",
                    "category": "shoes",
                    "colour_primary": "yellow",
                    "formality_level": 2,
                    "temperature_min": 20,
                    "temperature_max": 30,
                    "wear_count": 10,
                },
            ],
            "categories": ["top", "bottom", "shoes"],
        },
    ]

    weather = {
        "temperature": 9.0,
        "city": "London",
        "condition": "Mist",
    }

    ranked = rank_outfits(outfits, weather, top_k=1)

    assert len(ranked) == 1
    assert ranked[0]["outfit_id"] == 1