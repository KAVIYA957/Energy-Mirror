from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class ApplianceSignature:
    appliance_id: str
    name: str
    nominal_power_w: float
    tolerance_w: float
    expected_pf: Optional[float] = None
    pf_tolerance: Optional[float] = None
    category: str = "general"


@dataclass
class DetectedEvent:
    status: str  # "MATCHED", "AMBIGUOUS", "NO_CHANGE", "INSUFFICIENT_DATA"
    appliance_id: Optional[str]
    appliance_name: Optional[str]
    transition_type: Optional[str]  # "ON", "OFF", None
    delta_power_w: float
    rule_description: str
    timestamp: datetime
    delta_pf: Optional[float] = None
    data_classification: str = "RULE_BASED_ESTIMATE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "appliance_id": self.appliance_id,
            "appliance_name": self.appliance_name,
            "transition_type": self.transition_type,
            "delta_power_w": round(self.delta_power_w, 1),
            "delta_pf": round(self.delta_pf, 2) if self.delta_pf is not None else None,
            "rule_description": self.rule_description,
            "timestamp": self.timestamp.isoformat(),
            "data_classification": self.data_classification,
        }


class RuleBasedEventDetector:
    """
    Transparent, rule-based edge detector for Non-Intrusive Load Monitoring (NILM).
    
    CRITICAL METHODOLOGICAL GUARANTEE:
    This detector operates strictly on observed aggregate telemetry transitions (Delta P, Delta PF).
    It has ZERO access to the simulator's internal truth state.
    It does not claim to be a trained machine learning model and assigns zero fabricated confidence scores.
    """

    def __init__(self, noise_floor_w: float = 5.0):
        self.noise_floor_w = noise_floor_w
        # Configured calibrated appliance signatures with tolerance envelopes
        self.signatures: List[ApplianceSignature] = [
            ApplianceSignature(
                appliance_id="heater_01",
                name="Water Heater",
                nominal_power_w=140.0,
                tolerance_w=12.0,
                expected_pf=0.99,
                pf_tolerance=0.06,
                category="Heating",
            ),
            ApplianceSignature(
                appliance_id="pump_01",
                name="Water Pump",
                nominal_power_w=75.0,
                tolerance_w=9.0,
                expected_pf=0.78,
                pf_tolerance=0.12,
                category="Motor",
            ),
            ApplianceSignature(
                appliance_id="fan_01",
                name="Ceiling Fan",
                nominal_power_w=45.0,
                tolerance_w=7.0,
                expected_pf=0.91,
                pf_tolerance=0.09,
                category="Motor",
            ),
            ApplianceSignature(
                appliance_id="bulb_01",
                name="LED Bulb",
                nominal_power_w=12.0,
                tolerance_w=4.0,
                expected_pf=0.85,
                pf_tolerance=0.18,
                category="Lighting",
            ),
        ]

    def detect_transition(
        self,
        prev_power_w: Optional[float],
        curr_power_w: float,
        prev_pf: Optional[float] = None,
        curr_pf: Optional[float] = None,
        timestamp: Optional[datetime] = None,
    ) -> DetectedEvent:
        """
        Evaluate an aggregate step transition between two consecutive telemetry readings.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        if prev_power_w is None:
            return DetectedEvent(
                status="INSUFFICIENT_DATA",
                appliance_id=None,
                appliance_name=None,
                transition_type=None,
                delta_power_w=0.0,
                delta_pf=None,
                rule_description="Insufficient telemetry history to compute power derivative (Delta P).",
                timestamp=timestamp,
            )

        delta_p = round(curr_power_w - prev_power_w, 2)
        abs_delta_p = abs(delta_p)
        delta_pf = round(curr_pf - prev_pf, 2) if (curr_pf is not None and prev_pf is not None) else None

        # 1. Noise Floor Gate: If change is below noise floor, classify as steady state
        if abs_delta_p < self.noise_floor_w:
            return DetectedEvent(
                status="NO_CHANGE",
                appliance_id=None,
                appliance_name=None,
                transition_type=None,
                delta_power_w=delta_p,
                delta_pf=delta_pf,
                rule_description=f"Steady state: Delta P ({delta_p:+.1f} W) is within noise floor (< {self.noise_floor_w} W).",
                timestamp=timestamp,
            )

        direction = "ON" if delta_p > 0 else "OFF"

        # 2. Match against candidate signatures
        matches: List[ApplianceSignature] = []
        for sig in self.signatures:
            min_w = sig.nominal_power_w - sig.tolerance_w
            max_w = sig.nominal_power_w + sig.tolerance_w
            if min_w <= abs_delta_p <= max_w:
                matches.append(sig)

        # 3. Single Match: Unique identified transition
        if len(matches) == 1:
            matched_sig = matches[0]
            pf_note = f", Delta PF: {delta_pf:+.2f}" if delta_pf is not None else ""

            return DetectedEvent(
                status="MATCHED",
                appliance_id=matched_sig.appliance_id,
                appliance_name=matched_sig.name,
                transition_type=direction,
                delta_power_w=delta_p,
                delta_pf=delta_pf,
                rule_description=(
                    f"Rule-based match: {matched_sig.name} {direction} "
                    f"(|Delta P| = {abs_delta_p:.1f} W matches nominal {matched_sig.nominal_power_w:.0f} W "
                    f"within [{matched_sig.nominal_power_w - matched_sig.tolerance_w:.0f}, "
                    f"{matched_sig.nominal_power_w + matched_sig.tolerance_w:.0f}] W envelope{pf_note})."
                ),
                timestamp=timestamp,
            )

        # 4. Multiple Matches: Ambiguous overlap
        if len(matches) > 1:
            names = ", ".join(m.name for m in matches)
            return DetectedEvent(
                status="AMBIGUOUS",
                appliance_id=None,
                appliance_name="Ambiguous Overlap",
                transition_type=direction,
                delta_power_w=delta_p,
                delta_pf=delta_pf,
                rule_description=(
                    f"Ambiguous step of {delta_p:+.1f} W overlaps multiple configured signatures: {names}. "
                    "Evidence is insufficient to isolate a single appliance without higher-frequency waveform analysis."
                ),
                timestamp=timestamp,
            )

        # 5. Zero Matches: Unrecognized step or simultaneous multi-load switching
        return DetectedEvent(
            status="AMBIGUOUS",
            appliance_id=None,
            appliance_name="Unrecognized / Multi-Load Step",
            transition_type=direction,
            delta_power_w=delta_p,
            delta_pf=delta_pf,
            rule_description=(
                f"Unrecognized transition: Step of {delta_p:+.1f} W does not match any single appliance signature. "
                "Likely represents composite simultaneous switching or an uncalibrated household load."
            ),
            timestamp=timestamp,
        )

    def detect_from_history(self, power_points: List[float], timestamps: Optional[List[datetime]] = None) -> List[DetectedEvent]:
        """Process a series of aggregate power points and return all detected transition events."""
        events = []
        if len(power_points) < 2:
            return events

        for i in range(1, len(power_points)):
            t = timestamps[i] if timestamps and i < len(timestamps) else datetime.utcnow()
            event = self.detect_transition(
                prev_power_w=power_points[i - 1],
                curr_power_w=power_points[i],
                timestamp=t,
            )
            if event.status != "NO_CHANGE":
                events.append(event)
        return events


event_detector = RuleBasedEventDetector()
