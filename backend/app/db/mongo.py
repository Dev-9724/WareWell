from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Load backend/.env reliably even when uvicorn reloads
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "warewell")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set. Add it to backend/.env")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def get_db():
    return db