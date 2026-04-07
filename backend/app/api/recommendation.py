from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import get_database
from app.services.constraint_engine import apply_constraints
from app.services.outfit_generator import generate_outfits
from app.services.scoring_engine import (
    rank_outfits,
    get_target_formality,
    DEFAULT_WEIGHTS,
)
from app.services.explanation_engine import generate_explanations_for_ranked_outfits

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


async def get_active_weights(db):
    """
    Load current learned weights from MongoDB.
    If none exist yet, use default weights.
    """
    weights_col = db["model_weights"]
    weights_doc = await weights_col.find_one({"model_name": "hybrid_recommender"})

    if weights_doc and "weights" in weights_doc:
        return weights_doc["weights"]

    return DEFAULT_WEIGHTS


async def get_user_wardrobe_items(db, user_id: str):
    """
    Load wardrobe items for the selected user.
    """
    wardrobe_col = db["wardrobe_items"]

    items = []
    cursor = wardrobe_col.find({"user_id": user_id})
    async for doc in cursor:
        items.append(doc)

    return items


async def get_latest_weather_snapshot(db):
    """
    Load the latest weather snapshot from MongoDB.
    """
    weather_col = db["context_snapshots"]
    latest_weather = await weather_col.find_one({}, sort=[("timestamp", -1)])
    return latest_weather


@router.post("/filter")
async def filter_wardrobe_items(
    user_id: str = Query(..., min_length=1),
    occasion: str | None = Query(None),
):
    """
    Phase 5:
    Apply hard constraints to wardrobe items using latest weather snapshot.
    """
    db = get_database()

    items = await get_user_wardrobe_items(db, user_id)
    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    latest_weather = await get_latest_weather_snapshot(db)
    if not latest_weather:
        raise HTTPException(
            status_code=404,
            detail="No weather snapshot found. Please call /weather/current first."
        )

    try:
        filtered_result = apply_constraints(items, latest_weather, occasion=occasion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return filtered_result


@router.post("/outfits")
async def generate_recommended_outfits(
    user_id: str = Query(..., min_length=1),
    occasion: str | None = Query(None),
    max_outfits: int = Query(20, ge=1, le=100),
):
    """
    Phase 6:
    Generate outfit combinations after constraint filtering.
    """
    db = get_database()

    items = await get_user_wardrobe_items(db, user_id)
    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    latest_weather = await get_latest_weather_snapshot(db)
    if not latest_weather:
        raise HTTPException(
            status_code=404,
            detail="No weather snapshot found. Please call /weather/current first."
        )

    try:
        filtered_result = apply_constraints(items, latest_weather, occasion=occasion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid_items = filtered_result["valid_items"]
    outfit_result = generate_outfits(valid_items)

    limited_outfits = outfit_result["outfits"][:max_outfits]
    outfit_result["outfits"] = limited_outfits
    outfit_result["outfit_count"] = len(limited_outfits)

    return {
        "weather_used": filtered_result["weather_used"],
        "occasion_used": occasion,
        "valid_item_count": filtered_result["valid_count"],
        "rejected_item_count": filtered_result["rejected_count"],
        "rejected_items": filtered_result["rejected_items"],
        "max_outfits_used": max_outfits,
        "outfit_generation": outfit_result,
    }


@router.post("/ranked-outfits")
async def generate_ranked_outfits(
    user_id: str = Query(..., min_length=1),
    occasion: str | None = Query(None),
    target_formality: float | None = Query(None, ge=0, le=10),
    max_outfits: int = Query(20, ge=1, le=100),
    top_k: int = Query(5, ge=1, le=20),
):
    """
    Phase 7 + Phase 9:
    Full recommendation pipeline with learned weights.
    """
    db = get_database()

    items = await get_user_wardrobe_items(db, user_id)
    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    latest_weather = await get_latest_weather_snapshot(db)
    if not latest_weather:
        raise HTTPException(
            status_code=404,
            detail="No weather snapshot found. Please call /weather/current first."
        )

    try:
        filtered_result = apply_constraints(items, latest_weather, occasion=occasion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid_items = filtered_result["valid_items"]
    outfit_result = generate_outfits(valid_items)

    if not outfit_result["can_generate_outfits"]:
        return {
            "weather_used": filtered_result["weather_used"],
            "occasion_used": occasion,
            "valid_item_count": filtered_result["valid_count"],
            "rejected_item_count": filtered_result["rejected_count"],
            "rejected_items": filtered_result["rejected_items"],
            "outfit_generation": outfit_result,
            "ranked_outfits": [],
            "message": "No complete outfits could be generated after constraint filtering.",
        }

    generated_outfits = outfit_result["outfits"][:max_outfits]

    if target_formality is None:
        resolved_target_formality = get_target_formality(occasion=occasion, fallback=5.0)
    else:
        resolved_target_formality = target_formality

    active_weights = await get_active_weights(db)

    ranked = rank_outfits(
        outfits=generated_outfits,
        weather=filtered_result["weather_used"],
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
        "rejected_items": filtered_result["rejected_items"],
        "generated_outfit_count": outfit_result["outfit_count"],
        "scored_outfit_count": len(generated_outfits),
        "returned_ranked_outfit_count": len(ranked),
        "max_outfits_used": max_outfits,
        "top_k_used": top_k,
        "ranked_outfits": ranked,
    }


@router.post("/explanations")
async def generate_outfit_explanations(
    user_id: str = Query(..., min_length=1),
    occasion: str | None = Query(None),
    target_formality: float | None = Query(None, ge=0, le=10),
    max_outfits: int = Query(20, ge=1, le=100),
    top_k: int = Query(5, ge=1, le=20),
):
    """
    Phase 8 + Phase 9:
    Full recommendation pipeline with explanations and learned weights.
    """
    db = get_database()

    items = await get_user_wardrobe_items(db, user_id)
    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items found for this user")

    latest_weather = await get_latest_weather_snapshot(db)
    if not latest_weather:
        raise HTTPException(
            status_code=404,
            detail="No weather snapshot found. Please call /weather/current first."
        )

    try:
        filtered_result = apply_constraints(items, latest_weather, occasion=occasion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid_items = filtered_result["valid_items"]
    outfit_result = generate_outfits(valid_items)

    if not outfit_result["can_generate_outfits"]:
        return {
            "weather_used": filtered_result["weather_used"],
            "occasion_used": occasion,
            "valid_item_count": filtered_result["valid_count"],
            "rejected_item_count": filtered_result["rejected_count"],
            "rejected_items": filtered_result["rejected_items"],
            "outfit_generation": outfit_result,
            "explained_outfits": [],
            "message": "No complete outfits could be generated after constraint filtering.",
        }

    generated_outfits = outfit_result["outfits"][:max_outfits]

    if target_formality is None:
        resolved_target_formality = get_target_formality(occasion=occasion, fallback=5.0)
    else:
        resolved_target_formality = target_formality

    active_weights = await get_active_weights(db)

    ranked = rank_outfits(
        outfits=generated_outfits,
        weather=filtered_result["weather_used"],
        top_k=top_k,
        target_formality=resolved_target_formality,
        weights=active_weights,
    )

    explained = generate_explanations_for_ranked_outfits(
        ranked_outfits=ranked,
        weather=filtered_result["weather_used"],
        occasion=occasion,
        target_formality=resolved_target_formality,
    )

    return {
        "weather_used": filtered_result["weather_used"],
        "occasion_used": occasion,
        "target_formality_used": resolved_target_formality,
        "weights_used": active_weights,
        "valid_item_count": filtered_result["valid_count"],
        "rejected_item_count": filtered_result["rejected_count"],
        "rejected_items": filtered_result["rejected_items"],
        "generated_outfit_count": outfit_result["outfit_count"],
        "scored_outfit_count": len(generated_outfits),
        "explained_outfit_count": len(explained),
        "max_outfits_used": max_outfits,
        "top_k_used": top_k,
        "explained_outfits": explained,
    }