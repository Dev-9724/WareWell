from fastapi import FastAPI
from app.api.wardrobe import router as wardrobe_router
from app.api.weather import router as weather_router

app = FastAPI(
    title="WareWell API",
    version="0.1.0"
)

app.include_router(wardrobe_router)
app.include_router(weather_router)

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

# DB Works
from app.db.mongo import get_database

@app.get("/db/ping")
def db_ping():
    db = get_database()
    # command "ping" checks DB connectivity
    db.command("ping")
    return {"db": "connected"}