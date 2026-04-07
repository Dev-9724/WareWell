import os
from datetime import datetime, timezone, timedelta
from hashlib import pbkdf2_hmac, sha256
from hmac import compare_digest
from secrets import token_hex, token_urlsafe
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from dotenv import load_dotenv

from app.db.mongo import get_database
from app.services.email_service import send_password_reset_email

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

RESET_TOKEN_EXPIRY_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRY_MINUTES", "15"))
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=6)


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


def hash_reset_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


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

    existing_email = await users_col.find_one({"email": payload.email.lower().strip()})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered.")

    existing_username = await users_col.find_one({"username": payload.username.strip()})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken.")

    document = {
        "username": payload.username.strip(),
        "email": payload.email.lower().strip(),
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
        "reset_token_hash": None,
        "reset_token_expires_at": None,
        "reset_token_used": False,
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


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    db = get_database()
    users_col = db["users"]

    email = payload.email.lower().strip()
    user = await users_col.find_one({"email": email})

    success_message = "If an account with that email exists, a reset email has been sent."

    if not user:
        return {"message": success_message}

    raw_token = token_urlsafe(32)
    token_hash = hash_reset_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)

    await users_col.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "reset_token_hash": token_hash,
                "reset_token_expires_at": expires_at,
                "reset_token_used": False,
            }
        },
    )

    reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={raw_token}"

    try:
        send_password_reset_email(user["email"], reset_link)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send reset email: {str(exc)}"
        )

    return {"message": success_message}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    db = get_database()
    users_col = db["users"]

    token_hash = hash_reset_token(payload.token)
    user = await users_col.find_one({"reset_token_hash": token_hash})

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    if user.get("reset_token_used") is True:
        raise HTTPException(status_code=400, detail="This reset token has already been used.")

    expires_at = user.get("reset_token_expires_at")
    if not expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(status_code=400, detail="Reset token has expired.")

    if verify_password(payload.new_password, user["password_hash"]):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from the current password."
        )

    await users_col.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password_hash": hash_password(payload.new_password),
                "reset_token_hash": None,
                "reset_token_expires_at": None,
                "reset_token_used": True,
            }
        },
    )

    return {"message": "Password has been reset successfully."}


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