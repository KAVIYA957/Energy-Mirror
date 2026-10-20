from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

class SystemDiagnosticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Literal["healthy", "degraded", "offline"] = "healthy"
    app_name: str = "Energy Mirror"
    app_version: str = "1.0.0"
    server_timestamp: datetime
    active_telemetry_source: str = "SIMULATED"
    hardware_ingestion_enabled: bool = False
    hardware_mode: Literal["STAGED_INACTIVE", "HARDWARE_ACTIVE"] = "STAGED_INACTIVE"
    database_connected: bool = True
    database_type: str = "SQLite"
    database_record_count: int
    simulator_active: bool = True
    simulator_appliances_count: int = 4
    simulator_aggregate_w: float
    unattributed_baseline_w: float = 12.0
    recent_events_count: int
    nilm_detector_mode: str = "RULE_BASED_ESTIMATE"
    nilm_methodology: str = "Derivative Step Detection (Delta P, Delta PF)"
    data_classification: str = "SIMULATED_SYSTEM_DIAGNOSTICS"
