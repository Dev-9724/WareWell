from datetime import datetime, timezone
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

from app.db.mongo import get_database

router = APIRouter(prefix="/auth", tags=["Auth"])


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class PublicUser(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime


def hash_password(password: str, salt: Optional[str] = None) -> str:
    salt = salt or token_hex(16)
    hashed = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        salt, stored_hash = stored_value.split("$", 1)
    except ValueError:
        return False

    candidate = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    return compare_digest(candidate, stored_hash)


def serialize_user(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "username": doc["username"],
        "email": doc["email"],
        "created_at": doc["created_at"],
    }


@router.post("/signup", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest):
    db = get_database()
    users_col = db["users"]

    existing_email = await users_col.find_one({"email": payload.email.lower()})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered.")

    existing_username = await users_col.find_one({"username": payload.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken.")

    document = {
        "username": payload.username.strip(),
        "email": payload.email.lower().strip(),
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }

    result = await users_col.insert_one(document)
    created = await users_col.find_one({"_id": result.inserted_id})

    return serialize_user(created)


@router.post("/login")
async def login(payload: LoginRequest):
    db = get_database()
    users_col = db["users"]

    user = await users_col.find_one({"email": payload.email.lower().strip()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {
        "message": "Login successful.",
        "user": serialize_user(user),
    }


@router.get("/me/{user_id}", response_model=PublicUser)
async def get_me(user_id: str):
    db = get_database()
    users_col = db["users"]

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user id.")

    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return serialize_user(user)