from datetime import datetime, date
from pathlib import Path
from typing import Optional, List
from uuid import uuid4
import shutil

from bson import ObjectId
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Query
from app.db.mongo import get_database

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def serialize_item(doc):
    return {
        "id": str(doc["_id"]),
        "user_id": doc.get("user_id"),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "occasion": doc.get("occasion"),
        "colour_primary": doc.get("colour_primary"),
        "colour_secondary": doc.get("colour_secondary"),
        "formality_level": doc.get("formality_level"),
        "season": doc.get("season", []),
        "temperature_min": doc.get("temperature_min"),
        "temperature_max": doc.get("temperature_max"),
        "rain_suitable": doc.get("rain_suitable"),
        "wear_count": doc.get("wear_count", 0),
        "last_worn_date": doc.get("last_worn_date"),
        "cost": doc.get("cost"),
        "image_url": doc.get("image_url"),
        "created_at": (
            doc.get("created_at").isoformat()
            if isinstance(doc.get("created_at"), datetime)
            else doc.get("created_at")
        ),
    }


def parse_optional_date(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = str(value).strip()

    if cleaned == "" or cleaned.lower() == "string" or cleaned.lower() == "null":
        return None

    try:
        date.fromisoformat(cleaned)
        return cleaned
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="last_worn_date must be empty or in YYYY-MM-DD format."
        )


def parse_optional_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None

    cleaned = str(value).strip()
    if cleaned == "":
        return None

    try:
        return float(cleaned)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid number value.")


@router.get("/items")
async def get_items(user_id: str = Query(..., min_length=1)):
    db = get_database()
    items = await db["wardrobe_items"].find({"user_id": user_id}).sort("created_at", -1).to_list(length=1000)
    return [serialize_item(item) for item in items]


@router.get("/items/{item_id}")
async def get_item(item_id: str):
    db = get_database()

    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item id.")

    item = await db["wardrobe_items"].find_one({"_id": ObjectId(item_id)})

    if not item:
        raise HTTPException(status_code=404, detail="Wardrobe item not found.")

    return serialize_item(item)


@router.post("/items")
async def create_item(
    user_id: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    occasion: Optional[str] = Form(None),
    colour_primary: str = Form(...),
    colour_secondary: Optional[str] = Form(None),
    formality_level: int = Form(5),
    season: List[str] = Form([]),
    temperature_min: float = Form(0),
    temperature_max: float = Form(40),
    rain_suitable: bool = Form(False),
    wear_count: int = Form(0),
    last_worn_date: Optional[str] = Form(None),
    cost: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
):
    db = get_database()

    if temperature_min > temperature_max:
      raise HTTPException(
          status_code=400,
          detail="temperature_min cannot be greater than temperature_max."
      )

    image_url = None

    if image_file and image_file.filename:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        extension = Path(image_file.filename).suffix.lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, PNG, and WEBP files are allowed."
            )

        safe_filename = f"{uuid4().hex}{extension}"
        save_path = UPLOAD_DIR / safe_filename

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        image_url = f"/uploads/{safe_filename}"

    parsed_last_worn_date = parse_optional_date(last_worn_date)
    parsed_cost = parse_optional_float(cost)

    document = {
        "user_id": user_id,
        "name": name.strip(),
        "category": category.strip(),
        "occasion": occasion.strip() if occasion else None,
        "colour_primary": colour_primary.strip(),
        "colour_secondary": colour_secondary.strip() if colour_secondary else None,
        "formality_level": formality_level,
        "season": season,
        "temperature_min": temperature_min,
        "temperature_max": temperature_max,
        "rain_suitable": rain_suitable,
        "wear_count": wear_count,
        "last_worn_date": parsed_last_worn_date,
        "cost": parsed_cost if parsed_cost is not None else 0,
        "image_url": image_url,
        "created_at": datetime.utcnow(),
    }

    result = await db["wardrobe_items"].insert_one(document)
    saved = await db["wardrobe_items"].find_one({"_id": result.inserted_id})

    return serialize_item(saved)


@router.put("/items/{item_id}")
async def update_item(
    item_id: str,
    user_id: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    occasion: Optional[str] = Form(None),
    colour_primary: str = Form(...),
    colour_secondary: Optional[str] = Form(None),
    formality_level: int = Form(5),
    season: List[str] = Form([]),
    temperature_min: float = Form(0),
    temperature_max: float = Form(40),
    rain_suitable: bool = Form(False),
    wear_count: int = Form(0),
    last_worn_date: Optional[str] = Form(None),
    cost: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
):
    db = get_database()

    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item id.")

    existing = await db["wardrobe_items"].find_one({"_id": ObjectId(item_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Wardrobe item not found.")

    if temperature_min > temperature_max:
        raise HTTPException(
            status_code=400,
            detail="temperature_min cannot be greater than temperature_max."
        )

    image_url = existing.get("image_url")

    if image_file and image_file.filename:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        extension = Path(image_file.filename).suffix.lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, PNG, and WEBP files are allowed."
            )

        safe_filename = f"{uuid4().hex}{extension}"
        save_path = UPLOAD_DIR / safe_filename

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        image_url = f"/uploads/{safe_filename}"

    parsed_last_worn_date = parse_optional_date(last_worn_date)
    parsed_cost = parse_optional_float(cost)

    updated_doc = {
        "user_id": user_id,
        "name": name.strip(),
        "category": category.strip(),
        "occasion": occasion.strip() if occasion else None,
        "colour_primary": colour_primary.strip(),
        "colour_secondary": colour_secondary.strip() if colour_secondary else None,
        "formality_level": formality_level,
        "season": season,
        "temperature_min": temperature_min,
        "temperature_max": temperature_max,
        "rain_suitable": rain_suitable,
        "wear_count": wear_count,
        "last_worn_date": parsed_last_worn_date,
        "cost": parsed_cost if parsed_cost is not None else 0,
        "image_url": image_url,
    }

    await db["wardrobe_items"].update_one(
        {"_id": ObjectId(item_id)},
        {"$set": updated_doc}
    )

    saved = await db["wardrobe_items"].find_one({"_id": ObjectId(item_id)})
    return serialize_item(saved)


@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    db = get_database()

    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item id.")

    item = await db["wardrobe_items"].find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Wardrobe item not found.")

    image_url = item.get("image_url")
    if image_url and str(image_url).startswith("/uploads/"):
        file_path = UPLOAD_DIR / image_url.replace("/uploads/", "")
        if file_path.exists():
            file_path.unlink()

    await db["wardrobe_items"].delete_one({"_id": ObjectId(item_id)})

    return {"message": "Wardrobe item deleted successfully."}