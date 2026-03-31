from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.wardrobe import router as wardrobe_router
from app.api.weather import router as weather_router
from app.api.recommendation import router as recommendation_router
from app.routes.evaluation_routes import router as evaluation_router
from app.api.feedback import router as feedback_router
from app.db.mongo import get_database

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://dev-9724.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(weather_router)
app.include_router(recommendation_router)
app.include_router(evaluation_router)
app.include_router(feedback_router)

@app.get("/")
def root():
    return {
        "message": "WareWell API is running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db/ping")
def db_ping():
    db = get_database()
    db.command("ping")
    return {"db": "connected"}