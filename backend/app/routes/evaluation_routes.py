from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import get_database
from app.services.constraint_engine import apply_constraints
from app.services.outfit_generator import generate_outfits
from app.services.scoring_engine import DEFAULT_WEIGHTS, get_target_formality
from app.services.evaluation_service import evaluate_models

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


async def get_active_weights(db):
    """
    Load learned weights from MongoDB.
    If no learned weights exist yet, use default weights.
    """
    weights_col = db["model_weights"]
    weights_doc = await weights_col.find_one({"model_name": "hybrid_recommender"})

    if weights_doc and "weights" in weights_doc:
        return weights_doc["weights"]

    return DEFAULT_WEIGHTS


@router.post("/compare")
async def compare_models(
    user_id: str = Query(..., min_length=1),
    occasion: str | None = Query(None),
    target_formality: float | None = Query(None, ge=0, le=10),
    max_outfits: int = Query(20, ge=1, le=100),
    top_k: int = Query(5, ge=1, le=20),
):
    """
    Phase 11:
    Compare random baseline, rule-only baseline, and hybrid model
    using evaluation metrics.
    """
    db = get_database()

    wardrobe_col = db["wardrobe_items"]
    weather_col = db["context_snapshots"]

    # Load wardrobe items for the user
    items = []
    cursor = wardrobe_col.find({"user_id": user_id})
    async for doc in cursor:
        items.append(doc)

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No wardrobe items found for this user"
        )

    # Load latest weather snapshot
    latest_weather = await weather_col.find_one({}, sort=[("timestamp", -1)])
    if not latest_weather:
        raise HTTPException(
            status_code=404,
            detail="No weather snapshot found. Please call /weather/current first."
        )

    # Apply hard constraints
    try:
        filtered_result = apply_constraints(items, latest_weather)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid_items = filtered_result["valid_items"]
    total_valid_items = len(valid_items)

    # Generate outfit combinations
    outfit_result = generate_outfits(valid_items)

    if not outfit_result["can_generate_outfits"]:
        return {
            "weather_used": filtered_result["weather_used"],
            "occasion_used": occasion,
            "message": "No complete outfits could be generated after constraint filtering.",
            "comparison": {
                "random_baseline": {"metrics": {}, "outfits": []},
                "rule_only_baseline": {"metrics": {}, "outfits": []},
                "hybrid_model": {"metrics": {}, "outfits": []},
            },
        }

    generated_outfits = outfit_result["outfits"][:max_outfits]

    # Resolve target formality
    if target_formality is None:
        resolved_target_formality = get_target_formality(
            occasion=occasion,
            fallback=5.0
        )
    else:
        resolved_target_formality = target_formality

    # Load current model weights
    active_weights = await get_active_weights(db)

    # Run all three models through evaluation service
    comparison = evaluate_models(
        outfits=generated_outfits,
        weather=filtered_result["weather_used"],
        total_valid_items=total_valid_items,
        top_k=top_k,
        target_formality=resolved_target_formality,
        weights=active_weights,
    )

    return {
        "weather_used": filtered_result["weather_used"],
        "occasion_used": occasion,
        "target_formality_used": resolved_target_formality,
        "weights_used": active_weights,
        "valid_item_count": filtered_result["valid_count"],
        "rejected_item_count": filtered_result["rejected_count"],
        "generated_outfit_count": len(generated_outfits),
        "top_k_used": top_k,
        "comparison": comparison,
    }