from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import get_database
from app.services.constraint_engine import apply_constraints

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.post("/filter")
async def filter_wardrobe_items(user_id: str = Query(..., min_length=1)):
    """
    Load wardrobe items for a user, load latest weather snapshot,
    apply constraint filtering, and return valid/rejected items.
    """
    db = get_database()

    wardrobe_col = db["wardrobe_items"]
    weather_col = db["context_snapshots"]

    # Load wardrobe items for this user
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

    try:
        result = apply_constraints(items, latest_weather)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result