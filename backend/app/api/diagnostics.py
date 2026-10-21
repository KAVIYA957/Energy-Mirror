from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.models import TelemetryModel
from app.config import settings
from app.services.simulator import simulator
from app.schemas.diagnostics import SystemDiagnosticsResponse

router = APIRouter(prefix="/diagnostics", tags=["System Diagnostics"])


@router.get("/system", response_model=SystemDiagnosticsResponse)
def get_system_diagnostics(db: Session = Depends(get_db)):
    """
    Returns non-sensitive system diagnostics:
    - Backend health & database connectivity
    - Hardware ingestion configuration (staged/inactive)
    - Active telemetry source & simulator subsystem status
    - Rule-based NILM detector mode
    Never exposes secrets, tokens, or local filesystem paths.
    """
    db_connected = False
    record_count = 0
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
        record_count = db.query(TelemetryModel).count()
    except Exception:
        db_connected = False
        record_count = 0

    sim_state = simulator.get_state()

    return SystemDiagnosticsResponse(
        status="healthy" if db_connected else "degraded",
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        server_timestamp=datetime.utcnow(),
        active_telemetry_source="HARDWARE_CONNECTED" if settings.ENABLE_HARDWARE_INGEST else "SIMULATED",
        hardware_ingestion_enabled=settings.ENABLE_HARDWARE_INGEST,
        hardware_mode="HARDWARE_ACTIVE" if settings.ENABLE_HARDWARE_INGEST else "STAGED_INACTIVE",
        database_connected=db_connected,
        database_type="PostgreSQL" if "postgres" in settings.DATABASE_URL.lower() else "SQLite",
        database_record_count=record_count,
        simulator_active=True,
        simulator_appliances_count=len(sim_state.appliances),
        simulator_aggregate_w=sim_state.aggregate_power_w,
        unattributed_baseline_w=sim_state.unattributed_power_w,
        recent_events_count=len(sim_state.recent_events),
        nilm_detector_mode="RULE_BASED_ESTIMATE",
        nilm_methodology="Derivative Step Detection (Delta P, Delta PF)",
        data_classification="SIMULATED_SYSTEM_DIAGNOSTICS",
    )
