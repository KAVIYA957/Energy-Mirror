import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.telemetry import (
    TelemetryResponse,
    ApplianceEstimateSchema,
    DisaggregationResponse,
    HistoryPoint,
)
from app.schemas.simulator import (
    SimulatorApplianceState,
    SimulatorStateResponse,
    DetectedEventSchema,
)
from app.services.event_detector import event_detector, DetectedEvent


class TelemetrySimulator:
    """
    Deterministic telemetry and NILM disaggregation simulator.
    Provides controllable virtual appliance states, physical power reconciliation,
    and rule-based edge detection for the Living Current specification.
    """

    def __init__(self):
        self.base_device_id = "esp32-sim-01"
        self.voltage_nominal = 230.2
        self.frequency_nominal = 50.01

        # Simulated background load assumption (12.0 W baseline floor).
        # Note: This is an assumed simulator constant, not a physically detected or measured load.
        self.unattributed_w = 12.0
        self.standby_pf = 0.90

        # Controllable 4-appliance model matching Living Current design specification
        self._init_appliances()
        self.reset()

    def _init_appliances(self):
        self.appliances: Dict[str, Dict[str, Any]] = {
            "heater_01": {
                "appliance_id": "heater_01",
                "name": "Water Heater",
                "category": "Heating",
                "nominal_power_w": 140.0,
                "expected_pf": 0.99,
                "is_on": True,
                "last_toggled_at": None,
                "confidence_score": 0.94,
                "evidence_notes": "Sharp +140W step with near-unity power factor (PF ~ 0.99), typical of resistive heating element.",
            },
            "pump_01": {
                "appliance_id": "pump_01",
                "name": "Water Pump",
                "category": "Motor",
                "nominal_power_w": 75.0,
                "expected_pf": 0.78,
                "is_on": True,
                "last_toggled_at": None,
                "confidence_score": 0.88,
                "evidence_notes": "Inductive motor signature (+75W, PF ~ 0.78 lagging) detected following inrush transient.",
            },
            "fan_01": {
                "appliance_id": "fan_01",
                "name": "Ceiling Fan",
                "category": "Motor",
                "nominal_power_w": 45.0,
                "expected_pf": 0.91,
                "is_on": True,
                "last_toggled_at": None,
                "confidence_score": 0.91,
                "evidence_notes": "Continuous steady rotation load of 45W with slight reactive component.",
            },
            "bulb_01": {
                "appliance_id": "bulb_01",
                "name": "LED Bulb",
                "category": "Lighting",
                "nominal_power_w": 12.0,
                "expected_pf": 0.85,
                "is_on": True,
                "last_toggled_at": None,
                "confidence_score": 0.85,
                "evidence_notes": "Constant low-wattage step characteristic of high-efficiency switch-mode LED driver.",
            },
        }

    def reset(self):
        """Restore all appliances to baseline all-ON state (284 W aggregate) and reset event history."""
        self._init_appliances()
        for app in self.appliances.values():
            app["is_on"] = True
            app["last_toggled_at"] = None

        self.story_headline = "Baseline steady state: All 4 appliances running (284 W)"
        self.story_detail = "Simulated aggregate power is 284 W (272 W attributed + 12 W fixed residual floor). Detector is monitoring for load step transitions."

        initial_event = DetectedEvent(
            status="MATCHED",
            appliance_id="pump_01",
            appliance_name="Water Pump",
            transition_type="ON",
            delta_power_w=75.0,
            rule_description="Rule-based match: Water Pump ON (|Delta P| = 75.0 W matches nominal 75 W within [66, 84] W envelope).",
            timestamp=datetime.utcnow() - timedelta(minutes=42),
            data_classification="RULE_BASED_ESTIMATE",
        )
        self.recent_events: List[DetectedEvent] = [initial_event]

    def get_attributed_power(self) -> float:
        """Sum nominal power of all currently active virtual appliances."""
        total = sum(app["nominal_power_w"] for app in self.appliances.values() if app["is_on"])
        return round(total, 1)

    def get_aggregate_power(self) -> float:
        """Total aggregate power = active appliances + unattributed baseline (12.0 W)."""
        return round(self.get_attributed_power() + self.unattributed_w, 1)

    def get_composite_power_factor(self) -> float:
        """
        Calculate physically realistic composite AC power factor:
        Active power P = sum(P_i) + P_unatt
        Reactive power Q = sum(P_i * tan(acos(PF_i))) + Q_unatt
        Composite PF = P / sqrt(P^2 + Q^2)
        """
        total_p = 0.0
        total_q = 0.0

        for app in self.appliances.values():
            if app["is_on"]:
                p = app["nominal_power_w"]
                pf = app["expected_pf"]
                total_p += p
                # Q = P * tan(acos(pf))
                if 0.0 < pf < 1.0:
                    q = p * math.tan(math.acos(pf))
                    total_q += q

        # Add standby/unattributed contribution
        total_p += self.unattributed_w
        total_q += self.unattributed_w * math.tan(math.acos(self.standby_pf))

        if total_p <= 0.0:
            return 1.0

        apparent_s = math.sqrt(total_p**2 + total_q**2)
        composite_pf = total_p / apparent_s if apparent_s > 0 else 1.0
        return round(min(1.0, max(0.0, composite_pf)), 2)

    def toggle_appliance(
        self,
        appliance_id: str,
        target_state: Optional[str] = "TOGGLE",
        now: Optional[datetime] = None,
        db: Optional[Any] = None,
    ) -> Tuple[bool, str, str, float, Optional[DetectedEvent]]:
        """
        Controllably toggle or set state of a specific virtual appliance.
        Returns:
            (changed: bool, prev_state: str, new_state: str, delta_power_w: float, event: Optional[DetectedEvent])
        """
        if appliance_id not in self.appliances:
            valid_ids = list(self.appliances.keys())
            raise KeyError(f"Invalid appliance ID '{appliance_id}'. Valid IDs are: {valid_ids}")

        if now is None:
            now = datetime.utcnow()

        app = self.appliances[appliance_id]
        current_on: bool = app["is_on"]

        # Parse target state
        if target_state is None or target_state == "TOGGLE":
            new_on = not current_on
        elif target_state in ("ON", "RUNNING"):
            new_on = True
        elif target_state in ("OFF", "IDLE"):
            new_on = False
        else:
            raise ValueError(f"Invalid target state '{target_state}'. Permitted values: 'ON', 'OFF', 'TOGGLE'.")

        prev_state_str = "ON" if current_on else "OFF"
        new_state_str = "ON" if new_on else "OFF"

        if new_on == current_on:
            return False, prev_state_str, new_state_str, 0.0, None

        prev_power_w = self.get_aggregate_power()
        prev_pf = self.get_composite_power_factor()

        # Apply state transition
        app["is_on"] = new_on
        app["last_toggled_at"] = now

        curr_power_w = self.get_aggregate_power()
        curr_pf = self.get_composite_power_factor()
        delta_p = round(curr_power_w - prev_power_w, 1)

        # Trigger rule-based NILM event detector on aggregate derivative
        event = event_detector.detect_transition(
            prev_power_w=prev_power_w,
            curr_power_w=curr_power_w,
            prev_pf=prev_pf,
            curr_pf=curr_pf,
            timestamp=now,
        )

        self.recent_events.insert(0, event)
        self.recent_events = self.recent_events[:30]

        # Update dynamic telemetry narrative
        if event.status == "MATCHED":
            self.story_headline = f"{event.appliance_name} {event.transition_type} ({event.delta_power_w:+.0f} W)"
            self.story_detail = event.rule_description
        elif event.status == "AMBIGUOUS":
            self.story_headline = f"Ambiguous step detected ({event.delta_power_w:+.0f} W)"
            self.story_detail = event.rule_description

        # Persist event in durable database if session is provided
        if db is not None and event.status in ("MATCHED", "AMBIGUOUS"):
            try:
                from app.services.telemetry_service import telemetry_service
                telemetry_service.persist_detected_event(db, event)
            except Exception:
                pass

        return True, prev_state_str, new_state_str, delta_p, event


    def get_current_snapshot(self, now: Optional[datetime] = None) -> Tuple[TelemetryResponse, DisaggregationResponse]:
        if now is None:
            now = datetime.utcnow()

        appliance_schemas: List[ApplianceEstimateSchema] = []
        appliance_sum = 0.0

        for item in self.appliances.values():
            is_on = item["is_on"]
            power = float(item["nominal_power_w"]) if is_on else 0.0
            appliance_sum += power

            appliance_schemas.append(
                ApplianceEstimateSchema(
                    appliance_id=item["appliance_id"],
                    name=item["name"],
                    category=item["category"],
                    status="RUNNING" if is_on else "OFF",
                    estimated_power_w=power,
                    data_source="NILM_ESTIMATED",
                    confidence_score=item["confidence_score"] if is_on else None,
                    evidence_notes=item["evidence_notes"] if is_on else "Appliance is currently OFF (0 W detected).",
                    timestamp=now,
                )
            )

        aggregate_power_w = round(appliance_sum + self.unattributed_w, 1)
        calc_unattributed = max(0.0, round(aggregate_power_w - appliance_sum, 2))
        unattributed_pct = round((calc_unattributed / aggregate_power_w) * 100.0, 1) if aggregate_power_w > 0 else 0.0

        current_a = round(aggregate_power_w / self.voltage_nominal, 2)
        power_factor = self.get_composite_power_factor()
        apparent_va = round(aggregate_power_w / max(0.1, power_factor), 1)

        telemetry = TelemetryResponse(
            device_id=self.base_device_id,
            timestamp=now,
            data_source="SIMULATED",
            voltage_v=self.voltage_nominal,
            current_a=current_a,
            active_power_w=aggregate_power_w,
            apparent_power_va=apparent_va,
            power_factor=power_factor,
            frequency_hz=self.frequency_nominal,
            energy_kwh=18.42,
            is_simulated=True,
            unattributed_power_w=calc_unattributed,
            story_headline=self.story_headline,
        )

        disaggregation = DisaggregationResponse(
            timestamp=now,
            aggregate_power_w=aggregate_power_w,
            data_source="SIMULATED",
            is_simulated=True,
            unattributed_power_w=calc_unattributed,
            unattributed_percentage=unattributed_pct,
            appliances=appliance_schemas,
            story_headline=self.story_headline,
            story_detail=self.story_detail,
        )

        return telemetry, disaggregation

    def get_state(self, now: Optional[datetime] = None) -> SimulatorStateResponse:
        """Return the current dynamic simulator state, accounting, and rule-based event history."""
        if now is None:
            now = datetime.utcnow()

        appliances_state: List[SimulatorApplianceState] = []
        for app in self.appliances.values():
            is_on = app["is_on"]
            appliances_state.append(
                SimulatorApplianceState(
                    appliance_id=app["appliance_id"],
                    name=app["name"],
                    category=app["category"],
                    is_on=is_on,
                    nominal_power_w=app["nominal_power_w"],
                    current_power_w=app["nominal_power_w"] if is_on else 0.0,
                    status="RUNNING" if is_on else "OFF",
                    last_toggled_at=app["last_toggled_at"],
                )
            )

        attributed_w = self.get_attributed_power()
        aggregate_w = self.get_aggregate_power()
        unattributed_pct = round((self.unattributed_w / aggregate_w) * 100.0, 1) if aggregate_w > 0 else 0.0

        events_schema = [
            DetectedEventSchema(
                status=ev.status,
                appliance_id=ev.appliance_id,
                appliance_name=ev.appliance_name,
                transition_type=ev.transition_type,
                delta_power_w=ev.delta_power_w,
                rule_description=ev.rule_description,
                timestamp=ev.timestamp,
                data_classification=ev.data_classification,
            )
            for ev in self.recent_events
        ]

        return SimulatorStateResponse(
            timestamp=now,
            aggregate_power_w=aggregate_w,
            attributed_power_w=attributed_w,
            unattributed_power_w=self.unattributed_w,
            unattributed_percentage=unattributed_pct,
            appliances=appliances_state,
            recent_events=events_schema,
            data_source="SIMULATED",
            detector_mode="RULE_BASED_ESTIMATE",
            message=f"Current aggregate load: {aggregate_w} W ({attributed_w} W attributed, {self.unattributed_w} W background standby)",
        )

    def generate_history(self, minutes: int = 60, now: Optional[datetime] = None) -> List[HistoryPoint]:
        """
        Generate minute-by-minute historical aggregate power points showing traceable baseline transitions,
        matching current active loads.
        """
        if now is None:
            now = datetime.utcnow()

        points: List[HistoryPoint] = []
        minutes = max(5, min(minutes, 1440))
        current_agg = self.get_aggregate_power()

        for offset in range(minutes, -1, -1):
            t = now - timedelta(minutes=offset)
            event_name = None

            # Traceable historical profile leading to current state
            if offset > 45:
                # Base load: Fan (45W) + Bulb (12W) + standby (12W) = 69W
                power = 69.0 + (offset % 3) * 0.5
            elif offset > 18:
                # Heater engaged: 69 + 140 = 209W
                power = 209.0 + (offset % 4) * 0.4
                if offset == 45:
                    event_name = "Water Heater ON (+140 W)"
            elif offset > 2:
                # Pump engaged: 209 + 75 = 284W
                power = 284.0 + (offset % 3) * 0.3
                if offset == 18:
                    event_name = "Water Pump ON (+75 W)"
            else:
                # Recent minutes align with current dynamic simulator aggregate load
                power = current_agg + (offset % 2) * 0.2
                if offset == 0 and self.recent_events:
                    latest = self.recent_events[0]
                    if latest.status == "MATCHED":
                        event_name = f"{latest.appliance_name} {latest.transition_type} ({latest.delta_power_w:+.0f} W)"

            points.append(
                HistoryPoint(
                    timestamp=t,
                    active_power_w=round(power, 1),
                    data_source="SIMULATED",
                    appliance_event=event_name,
                )
            )

        return points


simulator = TelemetrySimulator()
