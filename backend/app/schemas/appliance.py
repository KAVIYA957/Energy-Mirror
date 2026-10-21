from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict

DetectionCapabilityType = Literal["PRODUCTION_RULE_MATCHED", "UNSUPPORTED", "EXPERIMENTAL_ONLY"]


class ApplianceDefinitionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appliance_id: str
    name: str
    category: str
    nominal_power_w: float
    expected_pf: Optional[float] = None
    tolerance_w: Optional[float] = None
    pf_tolerance: Optional[float] = None
    is_enabled: bool = True
    is_simulator_supported: bool = True
    detection_capability: DetectionCapabilityType = "UNSUPPORTED"
    confidence_score: Optional[float] = None
    evidence_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplianceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    appliance_id: str = Field(
        ...,
        min_length=2,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Unique stable machine-readable identifier (alphanumeric, underscores, hyphens)",
        examples=["toaster_01", "ev_charger_01"],
    )
    name: str = Field(..., min_length=2, max_length=128, description="Human-readable display name")
    category: str = Field(default="General", max_length=64, description="Appliance category (Heating, Motor, Lighting, Cooking, etc.)")
    nominal_power_w: float = Field(..., gt=0.0, le=25000.0, description="Rated or nominal active power in Watts")
    expected_pf: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Expected power factor magnitude (0.0 to 1.0)")
    tolerance_w: Optional[float] = Field(default=None, gt=0.0, le=5000.0, description="Edge detection tolerance envelope in Watts")
    pf_tolerance: Optional[float] = Field(default=None, ge=0.0, le=0.5, description="Power factor tolerance envelope")
    is_enabled: bool = Field(default=True, description="Whether this appliance is active and enabled")
    is_simulator_supported: bool = Field(default=True, description="Whether this appliance can be simulated in the virtual lab")
    detection_capability: DetectionCapabilityType = Field(
        default="UNSUPPORTED",
        description="Detection status: PRODUCTION_RULE_MATCHED (only if rule envelope calibrated), UNSUPPORTED, or EXPERIMENTAL_ONLY",
    )
    evidence_notes: Optional[str] = Field(default=None, description="Technical rationale or metrological signature notes")


class ApplianceUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=2, max_length=128)
    category: Optional[str] = Field(default=None, max_length=64)
    nominal_power_w: Optional[float] = Field(default=None, gt=0.0, le=25000.0)
    expected_pf: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tolerance_w: Optional[float] = Field(default=None, gt=0.0, le=5000.0)
    pf_tolerance: Optional[float] = Field(default=None, ge=0.0, le=0.5)
    is_enabled: Optional[bool] = None
    is_simulator_supported: Optional[bool] = None
    detection_capability: Optional[DetectionCapabilityType] = None
    evidence_notes: Optional[str] = None


class ApplianceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    count: int
    appliances: List[ApplianceDefinitionSchema]
    message: Optional[str] = None
