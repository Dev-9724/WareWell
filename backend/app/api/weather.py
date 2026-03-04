from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Query

from app.db.mongo import get_database
from app.models.weather_models import WeatherManualIn, WeatherSnapshotOut
from app.services.weather_service import fetch_current_weather, WeatherServiceError

router = APIRouter(prefix="/weather", tags=["Weather"])


def to_out(doc: dict) -> WeatherSnapshotOut:
    return WeatherSnapshotOut(
        id=str(doc["_id"]),
        temperature=doc["temperature"],
        humidity=doc["humidity"],
        wind=doc["wind"],
        rain=doc.get("rain", 0.0),
        condition=doc["condition"],
        city=doc["city"],
        timestamp=doc["timestamp"],
        source=doc.get("source", "unknown"),
    )


@router.get("/current", response_model=WeatherSnapshotOut)
async def get_current_weather(city: str = Query(..., min_length=2)):
    """
    Fetch live weather from WeatherAPI, store it in MongoDB (context_snapshots),
    and return the saved snapshot.
    """
    try:
        snapshot = fetch_current_weather(city)
    except WeatherServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    db = get_database()
    col = db["context_snapshots"]

    result = await col.insert_one(snapshot)
    saved = await col.find_one({"_id": result.inserted_id})
    return to_out(saved)


@router.post("/manual", response_model=WeatherSnapshotOut, status_code=status.HTTP_201_CREATED)
async def post_manual_weather(payload: WeatherManualIn):
    """
    Manual weather input (demo-safe).
    Stores snapshot in MongoDB with source='manual'.
    """
    snapshot = payload.model_dump()
    snapshot["timestamp"] = datetime.now(timezone.utc)
    snapshot["source"] = "manual"

    # Normalize condition lightly for consistency
    # (manual can enter Clear/Rain/Cloudy/Mist/Snow/Storm/Other)
    snapshot["condition"] = str(snapshot["condition"]).strip().title()

    db = get_database()
    col = db["context_snapshots"]

    result = await col.insert_one(snapshot)
    saved = await col.find_one({"_id": result.inserted_id})
    return to_out(saved)


@router.get("/latest", response_model=WeatherSnapshotOut)
async def get_latest_snapshot():
    """
    Return the most recent saved snapshot without calling external API.
    """
    db = get_database()
    col = db["context_snapshots"]

    doc = await col.find_one({}, sort=[("timestamp", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No weather snapshots found")

    return to_out(doc)