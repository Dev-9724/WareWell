from fastapi import FastAPI
from app.api.wardrobe import router as wardrobe_router
from app.api.weather import router as weather_router
from app.api.recommendation import router as recommendation_router
from app.routes.evaluation_routes import router as evaluation_router
from app.api.feedback import router as feedback_router


app = FastAPI()

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

# DB Works
from app.db.mongo import get_database

@app.get("/db/ping")
def db_ping():
    db = get_database()
    # command "ping" checks DB connectivity
    db.command("ping")
    return {"db": "connected"}