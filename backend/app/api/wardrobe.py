from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from app.db.mongo import get_database
from app.models.wardrobe_item import WardrobeItemCreate, WardrobeItemOut

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])


def to_out(doc: dict) -> WardrobeItemOut:
    """Convert Mongo document -> API response."""
    return WardrobeItemOut(
        id=str(doc["_id"]),
        created_at=doc["created_at"],
        user_id=doc["user_id"],
        category=doc["category"],
        colour_primary=doc["colour_primary"],
        colour_secondary=doc.get("colour_secondary"),
        formality_level=doc["formality_level"],
        season=doc.get("season", []),
        temperature_min=doc["temperature_min"],
        temperature_max=doc["temperature_max"],
        rain_suitable=doc["rain_suitable"],
        wear_count=doc.get("wear_count", 0),
        last_worn_date=doc.get("last_worn_date"),
        cost=doc.get("cost"),
        image_url=doc.get("image_url"),
    )


@router.post("/items", response_model=WardrobeItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(payload: WardrobeItemCreate):
    db = get_database()
    col = db["wardrobe_items"]

    doc = payload.model_dump()
    doc["created_at"] = datetime.utcnow()

    result = await col.insert_one(doc)
    created = await col.find_one({"_id": result.inserted_id})
    return to_out(created)


@router.get("/items", response_model=list[WardrobeItemOut])
async def list_items():
    db = get_database()
    col = db["wardrobe_items"]

    items: list[WardrobeItemOut] = []
    cursor = col.find({})
    async for doc in cursor:
        items.append(to_out(doc))
    return items


@router.get("/items/{item_id}", response_model=WardrobeItemOut)
async def get_item(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item id format")

    db = get_database()
    col = db["wardrobe_items"]

    doc = await col.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")

    return to_out(doc)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item id format")

    db = get_database()
    col = db["wardrobe_items"]

    result = await col.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return