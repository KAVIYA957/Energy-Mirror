from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.telemetry import (
    TelemetryResponse,
    DisaggregationResponse,
    HistoryResponse,
    PersistedEventSchema,
)
from app.services.telemetry_service import telemetry_service

router = APIRouter(tags=["Telemetry & NILM"])

@router.get("/telemetry/live", response_model=TelemetryResponse)
def get_live_telemetry(db: Session = Depends(get_db)):
    """
    Returns the latest aggregate telemetry record.
    Clearly marks whether data is LIVE or SIMULATED.
    """
    return telemetry_service.get_live_telemetry(db)

@router.get("/telemetry/history", response_model=HistoryResponse)
def get_telemetry_history(
    minutes: int = Query(default=60, ge=5, le=1440, description="History window in minutes"),
    db: Session = Depends(get_db),
):
    """
    Returns timestamped power telemetry points for the requested minute interval.
    Includes appliance transition events and persisted event records.
    """
    return telemetry_service.get_history(db, minutes=minutes)

@router.get("/telemetry/events", response_model=List[PersistedEventSchema])
def get_telemetry_events(
    minutes: int = Query(default=60, ge=5, le=1440, description="History window in minutes"),
    db: Session = Depends(get_db),
):
    """
    Returns durable rule-based detected events from SQLite for the requested window.
    Filtered by timestamp, ordered descending (newest first).
    """
    return telemetry_service.get_persisted_events(db, minutes=minutes)

@router.get("/nilm/live-disaggregation", response_model=DisaggregationResponse)
def get_live_disaggregation(db: Session = Depends(get_db)):
    """
    Returns current appliance-level NILM estimates, aggregate power,
    and residual unattributed load.
    All appliance items are explicitly tagged NILM_ESTIMATED.
    """
    return telemetry_service.get_live_disaggregation(db)

