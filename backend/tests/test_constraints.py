from datetime import datetime, timezone

from app.services.constraint_engine import apply_constraints


def test_apply_constraints_filters_invalid_items():
    items = [
        {
            "_id": "1",
            "user_id": "dev_mdx_user",
            "category": "top",
            "colour_primary": "blue",
            "colour_secondary": "white",
            "formality_level": 5,
            "season": ["spring"],
            "temperature_min": 5,
            "temperature_max": 15,
            "rain_suitable": True,
            "wear_count": 0,
            "last_worn_date": None,
            "cost": 20,
            "image_url": "",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "_id": "2",
            "user_id": "dev_mdx_user",
            "category": "shoes",
            "colour_primary": "white",
            "colour_secondary": None,
            "formality_level": 4,
            "season": ["summer"],
            "temperature_min": 15,
            "temperature_max": 30,
            "rain_suitable": False,
            "wear_count": 0,
            "last_worn_date": None,
            "cost": 30,
            "image_url": "",
            "created_at": datetime.now(timezone.utc),
        },
    ]

    weather_snapshot = {
        "temperature": 9.0,
        "rain": 0.0,
        "city": "London",
        "condition": "Mist",
        "timestamp": datetime(2026, 3, 10, tzinfo=timezone.utc),
    }

    result = apply_constraints(items, weather_snapshot)

    assert result["valid_count"] == 1
    assert result["rejected_count"] == 1
    assert result["valid_items"][0]["category"] == "top"
    assert result["rejected_items"][0]["category"] == "shoes"


def test_apply_constraints_rejects_rain_unsuitable_item():
    items = [
        {
            "_id": "10",
            "user_id": "dev_mdx_user",
            "category": "outerwear",
            "colour_primary": "black",
            "colour_secondary": None,
            "formality_level": 6,
            "season": ["spring"],
            "temperature_min": 5,
            "temperature_max": 15,
            "rain_suitable": False,
            "wear_count": 1,
            "last_worn_date": None,
            "cost": 40,
            "image_url": "",
            "created_at": datetime.now(timezone.utc),
        }
    ]

    weather_snapshot = {
        "temperature": 10.0,
        "rain": 2.0,
        "city": "London",
        "condition": "Rain",
        "timestamp": datetime(2026, 3, 10, tzinfo=timezone.utc),
    }

    result = apply_constraints(items, weather_snapshot)

    assert result["valid_count"] == 0
    assert result["rejected_count"] == 1
    assert "not_rain_suitable" in result["rejected_items"][0]["reasons"]