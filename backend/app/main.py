from fastapi import FastAPI

app = FastAPI(
    title="WareWell API",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}

# DB Works
from app.db.mongo import get_db

@app.get("/db/ping")
def db_ping():
    db = get_db()
    # command "ping" checks DB connectivity
    db.command("ping")
    return {"db": "connected"}