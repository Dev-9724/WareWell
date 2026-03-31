from datetime import datetime, timezone
from fastapi import APIRouter, status

from app.db.mongo import get_database
from app.models.feedback_models import FeedbackCreate, FeedbackOut
from app.services.weight_adapter import DEFAULT_WEIGHTS, adapt_weights

router = APIRouter(prefix="/feedback", tags=["Feedback"])


def to_out(doc: dict) -> FeedbackOut:
    return FeedbackOut(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        outfit_id=doc["outfit_id"],
        rating=doc["rating"],
        occasion=doc.get("occasion"),
        comment=doc.get("comment"),
        timestamp=doc["timestamp"],
        weights_before=doc["weights_before"],
        weights_after=doc["weights_after"],
    )


@router.post("/submit", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def submit_feedback(payload: FeedbackCreate):
    db = get_database()

    feedback_col = db["feedback_logs"]
    weights_col = db["model_weights"]

    weights_doc = await weights_col.find_one({"model_name": "hybrid_recommender"})
    if not weights_doc:
        weights_before = DEFAULT_WEIGHTS.copy()
        await weights_col.insert_one({
            "model_name": "hybrid_recommender",
            "weights": weights_before,
            "updated_at": datetime.now(timezone.utc),
        })
    else:
        weights_before = weights_doc.get("weights", DEFAULT_WEIGHTS.copy())

    weights_after = adapt_weights(weights_before, payload.rating)

    await weights_col.update_one(
        {"model_name": "hybrid_recommender"},
        {
            "$set": {
                "weights": weights_after,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

    doc = {
        "user_id": payload.user_id,
        "outfit_id": payload.outfit_id,
        "rating": payload.rating,
        "occasion": payload.occasion,
        "comment": payload.comment,
        "timestamp": datetime.now(timezone.utc),
        "weights_before": weights_before,
        "weights_after": weights_after,
    }

    result = await feedback_col.insert_one(doc)
    created = await feedback_col.find_one({"_id": result.inserted_id})

    return to_out(created)


@router.get("/weights")
async def get_current_weights():
    db = get_database()
    weights_col = db["model_weights"]

    weights_doc = await weights_col.find_one({"model_name": "hybrid_recommender"})
    if not weights_doc:
        return {
            "model_name": "hybrid_recommender",
            "weights": DEFAULT_WEIGHTS,
            "message": "Using default weights (no feedback submitted yet)."
        }

    return {
        "model_name": weights_doc["model_name"],
        "weights": weights_doc["weights"],
        "updated_at": weights_doc.get("updated_at"),
    }


@router.get("/logs")
async def list_feedback_logs():
    db = get_database()
    feedback_col = db["feedback_logs"]

    logs = []
    cursor = feedback_col.find({}).sort("timestamp", -1)

    async for doc in cursor:
        logs.append({
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "outfit_id": doc["outfit_id"],
            "rating": doc["rating"],
            "occasion": doc.get("occasion"),
            "comment": doc.get("comment"),
            "timestamp": doc["timestamp"],
            "weights_before": doc["weights_before"],
            "weights_after": doc["weights_after"],
        })

    return logs