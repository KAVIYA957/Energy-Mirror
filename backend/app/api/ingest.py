import secrets
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.schemas.telemetry import TelemetryIngestRequest, TelemetryIngestResponse

router = APIRouter(tags=["Telemetry Ingestion"])

@router.post(
    "/telemetry/ingest",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_200_OK,
)
def ingest_telemetry(
    payload: TelemetryIngestRequest,
    x_device_token: Optional[str] = Header(default=None, alias="X-Device-Token"),
    db: Session = Depends(get_db),
):
    """
    Ingest raw physical telemetry from ESP32 + PZEM-004T.
    
    Security:
    If DEVICE_INGEST_TOKEN is configured in environment, X-Device-Token is verified
    using constant-time comparison to prevent timing attacks.
    
    Staging Behavior:
    If ENABLE_HARDWARE_INGEST is false (default), telemetry is validated and acknowledged
    in STAGED_INACTIVE mode, preserving the simulator as the active telemetry provider.
    """
    # 1. Token authentication
    if settings.DEVICE_INGEST_TOKEN:
        if not x_device_token or not secrets.compare_digest(x_device_token, settings.DEVICE_INGEST_TOKEN):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing X-Device-Token authentication header.",
            )

    effective_power = round(payload.active_power_w / payload.ct_turns_ratio, 2)

    # 2. Check if hardware mode is active
    if not settings.ENABLE_HARDWARE_INGEST:
        return TelemetryIngestResponse(
            status="staged_inactive",
            device_id=payload.device_id,
            received_at=datetime.utcnow(),
            active_power_w=payload.active_power_w,
            effective_power_w=effective_power,
            ct_turns_ratio=payload.ct_turns_ratio,
            mode="STAGED_INACTIVE",
            message="Telemetry validated successfully. Hardware ingestion is currently STAGED (inactive). Simulator remains the active provider.",
        )

    # 3. If hardware ingestion is enabled, record to DB
    from app.db.models import TelemetryModel
    record = TelemetryModel(
        device_id=payload.device_id,
        timestamp=payload.timestamp,
        data_source=payload.data_source,
        voltage_v=payload.voltage_v,
        current_a=round(payload.current_a / payload.ct_turns_ratio, 3),
        active_power_w=effective_power,
        apparent_power_va=round(payload.apparent_power_va / payload.ct_turns_ratio, 2) if payload.apparent_power_va else None,
        power_factor=payload.power_factor,
        frequency_hz=payload.frequency_hz,
        energy_kwh=payload.energy_kwh,
        is_simulated=False,
        unattributed_power_w=effective_power,
        story_headline="Physical telemetry active",
    )
    db.add(record)
    db.commit()

    return TelemetryIngestResponse(
        status="accepted",
        device_id=payload.device_id,
        received_at=datetime.utcnow(),
        active_power_w=payload.active_power_w,
        effective_power_w=effective_power,
        ct_turns_ratio=payload.ct_turns_ratio,
        mode="HARDWARE_ACTIVE",
        message="Telemetry ingested and stored into hardware database stream.",
    )
