from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict

ApplianceIdLiteral = Literal["heater_01", "pump_01", "fan_01", "bulb_01"]


class ApplianceToggleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    appliance_id: str = Field(
        ...,
        description="Target appliance identifier ('heater_01', 'pump_01', 'fan_01', 'bulb_01')",
        examples=["heater_01"],
    )
    target_state: Optional[Literal["ON", "OFF", "TOGGLE"]] = Field(
        default="TOGGLE",
        description="Explicit state to set ('ON', 'OFF') or 'TOGGLE' to invert current state",
    )


class DetectedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    appliance_id: Optional[str] = None
    appliance_name: Optional[str] = None
    transition_type: Optional[str] = None
    delta_power_w: float
    delta_pf: Optional[float] = None
    rule_description: str
    timestamp: datetime
    data_classification: str = "RULE_BASED_ESTIMATE"



class SimulatorApplianceState(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    appliance_id: str
    name: str
    category: str
    is_on: bool
    nominal_power_w: float
    current_power_w: float
    status: Literal["ON", "OFF", "RUNNING", "IDLE"]
    last_toggled_at: Optional[datetime] = None


class SimulatorStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    aggregate_power_w: float
    attributed_power_w: float
    unattributed_power_w: float
    unattributed_percentage: float
    appliances: List[SimulatorApplianceState]
    recent_events: List[DetectedEventSchema]
    data_source: Literal["SIMULATED"] = "SIMULATED"
    detector_mode: Literal["RULE_BASED_ESTIMATE"] = "RULE_BASED_ESTIMATE"
    message: Optional[str] = None


class SimulatorToggleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Literal["success", "no_change"]
    appliance_id: str
    previous_state: str
    new_state: str
    delta_power_w: float
    event_detected: Optional[DetectedEventSchema] = None
    simulator_state: SimulatorStateResponse
    message: str
