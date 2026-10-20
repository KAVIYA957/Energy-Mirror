from datetime import datetime
from app.services.event_detector import RuleBasedEventDetector, event_detector


def test_detector_insufficient_data():
    detector = RuleBasedEventDetector()
    event = detector.detect_transition(prev_power_w=None, curr_power_w=284.0)
    assert event.status == "INSUFFICIENT_DATA"
    assert event.appliance_id is None
    assert event.data_classification == "RULE_BASED_ESTIMATE"
    assert "Insufficient" in event.rule_description


def test_detector_noise_floor_steady_state():
    detector = RuleBasedEventDetector(noise_floor_w=5.0)
    # Step under 5W noise floor
    event = detector.detect_transition(prev_power_w=284.0, curr_power_w=286.2)
    assert event.status == "NO_CHANGE"
    assert event.appliance_id is None
    assert event.delta_power_w == 2.2
    assert "noise floor" in event.rule_description


def test_detector_matched_heater_transitions():
    detector = RuleBasedEventDetector()
    # Heater ON: +140W
    event_on = detector.detect_transition(prev_power_w=144.0, curr_power_w=284.0)
    assert event_on.status == "MATCHED"
    assert event_on.appliance_id == "heater_01"
    assert event_on.appliance_name == "Water Heater"
    assert event_on.transition_type == "ON"
    assert event_on.delta_power_w == 140.0
    assert event_on.data_classification == "RULE_BASED_ESTIMATE"

    # Heater OFF: -140W
    event_off = detector.detect_transition(prev_power_w=284.0, curr_power_w=144.0)
    assert event_off.status == "MATCHED"
    assert event_off.appliance_id == "heater_01"
    assert event_off.transition_type == "OFF"
    assert event_off.delta_power_w == -140.0


def test_detector_matched_pump_transitions():
    detector = RuleBasedEventDetector()
    # Pump ON: +75W
    event_on = detector.detect_transition(prev_power_w=209.0, curr_power_w=284.0)
    assert event_on.status == "MATCHED"
    assert event_on.appliance_id == "pump_01"
    assert event_on.appliance_name == "Water Pump"
    assert event_on.transition_type == "ON"
    assert event_on.delta_power_w == 75.0

    # Pump OFF: -75W
    event_off = detector.detect_transition(prev_power_w=284.0, curr_power_w=209.0)
    assert event_off.status == "MATCHED"
    assert event_off.appliance_id == "pump_01"
    assert event_off.transition_type == "OFF"
    assert event_off.delta_power_w == -75.0


def test_detector_matched_fan_transitions():
    detector = RuleBasedEventDetector()
    # Fan ON: +45W
    event_on = detector.detect_transition(prev_power_w=239.0, curr_power_w=284.0)
    assert event_on.status == "MATCHED"
    assert event_on.appliance_id == "fan_01"
    assert event_on.appliance_name == "Ceiling Fan"
    assert event_on.transition_type == "ON"
    assert event_on.delta_power_w == 45.0

    # Fan OFF: -45W
    event_off = detector.detect_transition(prev_power_w=284.0, curr_power_w=239.0)
    assert event_off.status == "MATCHED"
    assert event_off.appliance_id == "fan_01"
    assert event_off.transition_type == "OFF"
    assert event_off.delta_power_w == -45.0


def test_detector_matched_bulb_transitions():
    detector = RuleBasedEventDetector()
    # Bulb ON: +12W
    event_on = detector.detect_transition(prev_power_w=272.0, curr_power_w=284.0)
    assert event_on.status == "MATCHED"
    assert event_on.appliance_id == "bulb_01"
    assert event_on.appliance_name == "LED Bulb"
    assert event_on.transition_type == "ON"
    assert event_on.delta_power_w == 12.0

    # Bulb OFF: -12W
    event_off = detector.detect_transition(prev_power_w=284.0, curr_power_w=272.0)
    assert event_off.status == "MATCHED"
    assert event_off.appliance_id == "bulb_01"
    assert event_off.transition_type == "OFF"
    assert event_off.delta_power_w == -12.0


def test_detector_ambiguous_composite_step():
    detector = RuleBasedEventDetector()
    # Simultaneous switching of Heater (140W) + Pump (75W) = 215W step
    event = detector.detect_transition(prev_power_w=69.0, curr_power_w=284.0)
    assert event.status == "AMBIGUOUS"
    assert event.appliance_id is None
    assert event.delta_power_w == 215.0
    assert "Unrecognized transition" in event.rule_description
    assert event.data_classification == "RULE_BASED_ESTIMATE"


def test_detector_detect_from_history():
    detector = RuleBasedEventDetector()
    # Empty history
    assert detector.detect_from_history([]) == []
    assert detector.detect_from_history([284.0]) == []

    # Sequence with 2 transitions: +140W then +75W
    powers = [69.0, 209.0, 284.0]
    events = detector.detect_from_history(powers)
    assert len(events) == 2
    assert events[0].appliance_id == "heater_01"
    assert events[0].transition_type == "ON"
    assert events[1].appliance_id == "pump_01"
    assert events[1].transition_type == "ON"


def test_detector_is_completely_blind_to_toggled_appliance():
    """
    Architectural Verification:
    The event detector only receives (prev_power_w, curr_power_w, prev_pf, curr_pf).
    It is never passed the appliance_id or target_state.
    Verify that it evaluates based purely on electrical derivative envelopes.
    """
    detector = RuleBasedEventDetector()

    # Step of 75.0 W is classified as Water Pump purely from [66, 84] W envelope
    event = detector.detect_transition(prev_power_w=100.0, curr_power_w=175.0)
    assert event.status == "MATCHED"
    assert event.appliance_id == "pump_01"
    assert event.appliance_name == "Water Pump"
    assert event.transition_type == "ON"
    assert event.data_classification == "RULE_BASED_ESTIMATE"

    # Step of 95.0 W does not match any single appliance envelope:
    # Heater is [128, 152] W, Pump is [66, 84] W, Fan is [38, 52] W, Bulb is [8, 16] W.
    # Therefore, 95 W must be classified as AMBIGUOUS, even if a user claims it is an appliance!
    event_unknown = detector.detect_transition(prev_power_w=100.0, curr_power_w=195.0)
    assert event_unknown.status == "AMBIGUOUS"
    assert event_unknown.appliance_id is None
    assert "Unrecognized transition" in event_unknown.rule_description


def test_detector_first_sample_and_steady_state_boundaries():
    """Verify first sample returns INSUFFICIENT_DATA and step < 5 W returns NO_CHANGE."""
    detector = RuleBasedEventDetector(noise_floor_w=5.0)

    # First sample
    assert detector.detect_transition(prev_power_w=None, curr_power_w=150.0).status == "INSUFFICIENT_DATA"

    # Delta within noise floor (e.g. 4.9 W)
    noise_event = detector.detect_transition(prev_power_w=100.0, curr_power_w=104.9)
    assert noise_event.status == "NO_CHANGE"
    assert noise_event.appliance_id is None
    assert noise_event.delta_power_w == 4.9

