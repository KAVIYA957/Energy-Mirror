from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.telemetry import HealthResponse
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        database_connected=db_connected,
        timestamp=datetime.utcnow(),
    )
