from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.simulator import (
    ApplianceToggleRequest,
    SimulatorStateResponse,
    SimulatorToggleResponse,
    DetectedEventSchema,
)
from app.services.simulator import simulator

router = APIRouter(prefix="/simulator", tags=["Simulator Lab"])


@router.get("/state", response_model=SimulatorStateResponse)
def get_simulator_state():
    """
    Returns the current dynamic state of the virtual simulator:
    - On/off status and power of all 4 virtual appliances
    - Aggregate simulated power and unattributed background standby
    - Recent rule-based detected events
    """
    return simulator.get_state()


@router.post("/toggle-appliance", response_model=SimulatorToggleResponse)
def toggle_appliance(request: ApplianceToggleRequest, db: Session = Depends(get_db)):
    """
    Controllably toggle or set an individual virtual appliance's state.
    Supported IDs: 'heater_01', 'pump_01', 'fan_01', 'bulb_01'.
    Target state: 'ON', 'OFF', or 'TOGGLE'.
    Triggers rule-based event detection on the resulting aggregate power derivative and persists detected events.
    """
    try:
        changed, prev_state, new_state, delta_w, event = simulator.toggle_appliance(
            appliance_id=request.appliance_id,
            target_state=request.target_state,
            db=db,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    current_state = simulator.get_state()
    event_schema = (
        DetectedEventSchema(
            status=event.status,
            appliance_id=event.appliance_id,
            appliance_name=event.appliance_name,
            transition_type=event.transition_type,
            delta_power_w=event.delta_power_w,
            rule_description=event.rule_description,
            timestamp=event.timestamp,
            data_classification=event.data_classification,
        )
        if event
        else None
    )

    if not changed:
        return SimulatorToggleResponse(
            status="no_change",
            appliance_id=request.appliance_id,
            previous_state=prev_state,
            new_state=new_state,
            delta_power_w=0.0,
            event_detected=None,
            simulator_state=current_state,
            message=f"Appliance '{request.appliance_id}' was already {new_state}. No state change performed.",
        )

    return SimulatorToggleResponse(
        status="success",
        appliance_id=request.appliance_id,
        previous_state=prev_state,
        new_state=new_state,
        delta_power_w=delta_w,
        event_detected=event_schema,
        simulator_state=current_state,
        message=f"Appliance '{request.appliance_id}' transitioned from {prev_state} to {new_state} ({delta_w:+.1f} W).",
    )


@router.post("/reset", response_model=SimulatorStateResponse)
def reset_simulator():
    """
    Reset simulator to baseline demonstration state:
    - All 4 appliances ON (272 W total attributed)
    - Unattributed background standby: 12 W
    - Aggregate load: 284 W
    - Event history reset
    """
    simulator.reset()
    return simulator.get_state()
