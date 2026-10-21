from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

DataSourceType = Literal["LIVE", "SIMULATED", "STALE", "UNAVAILABLE", "NILM_ESTIMATED", "HARDWARE_CONNECTED"]

class ApplianceEstimateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    appliance_id: str
    name: str
    category: str = "general"
    status: Literal["OFF", "ON", "RUNNING", "IDLE"] = "RUNNING"
    estimated_power_w: float = Field(ge=0.0)
    nominal_power_w: Optional[float] = Field(default=None, ge=0.0)
    detection_capability: Optional[str] = "PRODUCTION_RULE_MATCHED"
    data_source: Literal["NILM_ESTIMATED"] = "NILM_ESTIMATED"
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence_notes: Optional[str] = None
    timestamp: datetime



class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    timestamp: datetime
    data_source: DataSourceType = "SIMULATED"
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None
    active_power_w: float
    apparent_power_va: Optional[float] = None
    power_factor: Optional[float] = None
    frequency_hz: Optional[float] = None
    energy_kwh: Optional[float] = None
    is_simulated: bool = True
    unattributed_power_w: float = Field(ge=0.0)
    story_headline: Optional[str] = None


class DisaggregationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    aggregate_power_w: float = Field(ge=0.0)
    data_source: DataSourceType = "SIMULATED"
    is_simulated: bool = True
    unattributed_power_w: float = Field(ge=0.0)
    unattributed_percentage: float = Field(ge=0.0, le=100.0)
    appliances: List[ApplianceEstimateSchema]
    story_headline: Optional[str] = None
    story_detail: Optional[str] = None


class HistoryPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    active_power_w: float
    data_source: DataSourceType = "SIMULATED"
    appliance_event: Optional[str] = None


class PersistedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    timestamp: datetime
    status: str
    appliance_id: Optional[str] = None
    appliance_name: Optional[str] = None
    transition_type: Optional[str] = None
    delta_power_w: float
    delta_pf: Optional[float] = None
    rule_description: str
    data_classification: str = "RULE_BASED_ESTIMATE"


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interval_minutes: int
    count: int
    points: List[HistoryPoint]
    available_range_minutes: Optional[int] = None
    data_source: DataSourceType = "SIMULATED"
    is_simulated: bool = True
    events: List[PersistedEventSchema] = Field(default_factory=list)



class HealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    app: str = "Energy Mirror Backend"
    version: str = "1.0.0"
    database_connected: bool = True
    timestamp: datetime


class TelemetryIngestRequest(BaseModel):
    """
    Contract for raw physical aggregate telemetry ingested from ESP32.
    Explicitly distinguishes native metrology measurements from derived values.
    """
    model_config = ConfigDict(extra="forbid")

    device_id: str = Field(..., min_length=3, max_length=64, description="Unique hardware identifier e.g. MAC address")
    timestamp: datetime = Field(..., description="UTC ISO8601 timestamp synchronized via SNTP on ESP32")
    firmware_version: Optional[str] = Field(default=None, max_length=32)
    data_source: Literal["HARDWARE_CONNECTED"] = "HARDWARE_CONNECTED"

    # --- Native Metrology (PZEM-004T v3.0 Modbus Registers) ---
    voltage_v: float = Field(..., ge=80.0, le=280.0, description="Native RMS voltage (PZEM reg 0x0000, 0.1V resolution)")
    current_a: float = Field(..., ge=0.0, le=100.0, description="Native RMS current through CT (PZEM regs 0x0001-02, 0.001A resolution)")
    active_power_w: float = Field(..., ge=0.0, le=23000.0, description="Native active power (PZEM regs 0x0003-04, 0.1W resolution)")
    energy_kwh: Optional[float] = Field(default=None, ge=0.0, description="Native active energy (PZEM regs 0x0005-06, 1Wh resolution)")
    frequency_hz: Optional[float] = Field(default=None, ge=45.0, le=65.0, description="Native line frequency (PZEM reg 0x0007, 0.1Hz resolution)")
    power_factor: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Native power factor magnitude (PZEM reg 0x0008, 0.01 resolution; unsigned magnitude only, no sign/quadrant)"
    )

    # --- Derived Quantities (Calculated, NOT natively measured by PZEM-004T) ---
    apparent_power_va: Optional[float] = Field(default=None, ge=0.0, description="Derived apparent power S = V * I (VA)")
    derived_reactive_power_var: Optional[float] = Field(
        default=None,
        ge=0.0,
        description=(
            "Derived approximate reactive power |Q| = sqrt(max(0, S^2 - P^2)). "
            "High mathematical uncertainty when PF > 0.95 due to 0.01 PF quantization resolution."
        )
    )

    # --- Low-Power Metrology & Multi-Turn CT Support ---
    ct_turns_ratio: int = Field(
        default=1,
        ge=1,
        le=50,
        description="Multi-turn primary winding multiplier through CT aperture (1 for standard single wire pass, N for multi-turn winding to magnify low currents like 12W LED bulbs)."
    )
    rssi_dbm: Optional[int] = Field(default=None, ge=-120, le=0, description="Wi-Fi signal strength at transmitter")

    @model_validator(mode="after")
    def validate_physical_consistency(self) -> "TelemetryIngestRequest":
        # Check active power vs apparent power consistency if apparent power is supplied
        if self.apparent_power_va is not None and self.apparent_power_va > 0:
            # 8% tolerance allowance for non-simultaneous register reads and measurement jitter
            if self.active_power_w > self.apparent_power_va * 1.08:
                raise ValueError(
                    f"Active power ({self.active_power_w} W) cannot exceed apparent power "
                    f"({self.apparent_power_va} VA) by more than measurement tolerance."
                )
        return self


class TelemetryIngestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Literal["accepted", "staged_inactive", "rejected"] = "accepted"
    device_id: str
    received_at: datetime
    active_power_w: float
    effective_power_w: float
    ct_turns_ratio: int = 1
    mode: Literal["STAGED_INACTIVE", "HARDWARE_ACTIVE"]
    message: str
