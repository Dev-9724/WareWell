from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import get_database
from app.services.constraint_engine import apply_constraints
from app.services.outfit_generator import generate_outfits
from app.services.scoring_engine import rank_outfits
from app.services.evaluation_service import (
    random_baseline,
    rule_only_baseline,
    hybrid_model,
    evaluate_outfit_set,
)

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post("/compare")
async def compare_models(
    user_id: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    max_outfits: int = Query(20, ge=1, le=100),
):
    """
    Compare:
    1. Random baseline
    2. Rule-only baseline
    3. Hybrid scored model

    This endpoint runs the full backend pipeline automatically.
    """
    db = get_database()

    wardrobe_col = db["wardrobe_items"]
    weather_col = db["context_snapshots"]

    # Load wardrobe items
    items = []
    cursor = wardrobe_col.find({"user_id": user_id})
    async for doc in cursor:
        items.append(doc)

    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    # Load latest weather snapshot
    latest_weather = await weather_col.find_one({}, sort=[("timestamp", -1)])
    if not latest_weather:
        raise HTTPException(status_code=404, detail="No weather snapshot found. Please call /weather/current first.")

    # Apply constraints
    try:
        filtered_result = apply_constraints(items, latest_weather)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid_items = filtered_result["valid_items"]

    # Generate outfits
    outfit_result = generate_outfits(valid_items)

    if not outfit_result["can_generate_outfits"]:
        return {
            "weather_used": filtered_result["weather_used"],
            "message": "No complete outfits could be generated after constraint filtering.",
            "comparison": {
                "random_baseline": [],
                "rule_only_baseline": [],
                "hybrid_model": [],
            }
        }

    generated_outfits = outfit_result["outfits"][:max_outfits]

    # Build baselines
    random_results = random_baseline(generated_outfits, top_k=top_k)
    rule_results = rule_only_baseline(generated_outfits, top_k=top_k)

    # Build hybrid ranked model
    ranked = rank_outfits(
        outfits=generated_outfits,
        weather=filtered_result["weather_used"],
        top_k=top_k,
        target_formality=5.0,
    )
    hybrid_results = hybrid_model(ranked, top_k=top_k)

    return {
        "weather_used": filtered_result["weather_used"],
        "valid_item_count": filtered_result["valid_count"],
        "generated_outfit_count": len(generated_outfits),
        "top_k_used": top_k,
        "comparison": {
            "random_baseline": {
                "metrics": evaluate_outfit_set(random_results),
                "outfits": random_results,
            },
            "rule_only_baseline": {
                "metrics": evaluate_outfit_set(rule_results),
                "outfits": rule_results,
            },
            "hybrid_model": {
                "metrics": evaluate_outfit_set(hybrid_results),
                "outfits": hybrid_results,
            },
        },
    }