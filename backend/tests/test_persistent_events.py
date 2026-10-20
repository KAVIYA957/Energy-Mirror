from datetime import datetime, timedelta
import pytest
from app.db.models import DetectedEventModel, TelemetryModel
from app.services.event_detector import DetectedEvent, event_detector
from app.services.telemetry_service import telemetry_service
from app.services.simulator import simulator


def test_successful_event_persistence(client, db_session):
    """
    Verify that toggling an appliance via API triggers rule-based detection
    and durably persists the event in SQLite detected_events table.
    """
    initial_count = db_session.query(DetectedEventModel).count()

    # Toggle Water Heater OFF (-140 W step)
    res = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "OFF"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["delta_power_w"] == -140.0

    # Verify event stored in SQLite
    new_count = db_session.query(DetectedEventModel).count()
    assert new_count == initial_count + 1

    latest_event = (
        db_session.query(DetectedEventModel)
        .order_by(DetectedEventModel.id.desc())
        .first()
    )
    assert latest_event is not None
    assert latest_event.status == "MATCHED"
    assert latest_event.appliance_id == "heater_01"
    assert latest_event.appliance_name == "Water Heater"
    assert latest_event.transition_type == "OFF"
    assert latest_event.delta_power_w == -140.0
    assert latest_event.data_classification == "RULE_BASED_ESTIMATE"
    assert "Water Heater OFF" in latest_event.rule_description


def test_event_retrieval_after_restart(client, db_session):
    """
    Verify that persisted events survive in-memory resets (simulating server restarts)
    and remain retrievable via GET /api/v1/telemetry/events and history.
    """
    # 1. Generate a pump toggle event
    res = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "pump_01", "target_state": "OFF"},
    )
    assert res.status_code == 200

    # 2. Simulate server restart: in-memory simulator reset clears recent_events ring buffer
    simulator.reset()
    assert len(simulator.recent_events) == 1  # reset to single baseline event in-memory

    # 3. Query durable API endpoint: persisted events must still be returned from SQLite
    res_events = client.get("/api/v1/telemetry/events?minutes=60")
    assert res_events.status_code == 200
    events = res_events.json()
    assert len(events) >= 2  # includes seeded initial event + pump toggle

    pump_events = [e for e in events if e.get("appliance_id") == "pump_01" and e.get("transition_type") == "OFF"]
    assert len(pump_events) == 1
    assert pump_events[0]["delta_power_w"] == -75.0
    assert pump_events[0]["status"] == "MATCHED"


def test_duplicate_prevention_during_repeated_polling_or_retries(db_session):
    """
    Verify that duplicate persistence attempts for the same event or fingerprint
    are safely ignored and do not create duplicate records.
    """
    now = datetime.utcnow()
    event = DetectedEvent(
        status="MATCHED",
        appliance_id="fan_01",
        appliance_name="Ceiling Fan",
        transition_type="ON",
        delta_power_w=45.0,
        delta_pf=0.08,
        rule_description="Rule-based match: Ceiling Fan ON",
        timestamp=now,
        data_classification="RULE_BASED_ESTIMATE",
    )

    # First persistence
    rec1 = telemetry_service.persist_detected_event(db_session, event)
    assert rec1 is not None
    count_after_1 = db_session.query(DetectedEventModel).filter_by(appliance_id="fan_01").count()
    assert count_after_1 == 1

    # Second persistence with identical event
    rec2 = telemetry_service.persist_detected_event(db_session, event)
    assert rec2 is not None
    assert rec2.id == rec1.id
    count_after_2 = db_session.query(DetectedEventModel).filter_by(appliance_id="fan_01").count()
    assert count_after_2 == 1

    # Retry within 1 second window with same delta and status
    event_retry = DetectedEvent(
        status="MATCHED",
        appliance_id="fan_01",
        appliance_name="Ceiling Fan",
        transition_type="ON",
        delta_power_w=45.0,
        delta_pf=0.08,
        rule_description="Rule-based match: Ceiling Fan ON (retry)",
        timestamp=now + timedelta(milliseconds=400),
        data_classification="RULE_BASED_ESTIMATE",
    )
    rec3 = telemetry_service.persist_detected_event(db_session, event_retry)
    assert rec3 is not None
    assert rec3.id == rec1.id
    count_after_retry = db_session.query(DetectedEventModel).filter_by(appliance_id="fan_01").count()
    assert count_after_retry == 1


def test_ambiguous_event_persistence(client, db_session):
    """
    Verify that ambiguous/unrecognized multi-load steps are honestly classified
    and persisted with status AMBIGUOUS and no fabricated appliance identity.
    """
    initial_count = db_session.query(DetectedEventModel).count()

    now = datetime.utcnow()
    # 215 W step matches no single appliance envelope (composite heater + pump)
    ambiguous_event = event_detector.detect_transition(
        prev_power_w=50.0,
        curr_power_w=265.0,
        prev_pf=0.90,
        curr_pf=0.82,
        timestamp=now,
    )
    assert ambiguous_event.status == "AMBIGUOUS"
    assert ambiguous_event.appliance_id is None

    # Persist ambiguous event
    rec = telemetry_service.persist_detected_event(db_session, ambiguous_event)
    assert rec is not None
    assert rec.status == "AMBIGUOUS"
    assert rec.appliance_id is None
    assert rec.delta_power_w == 215.0

    new_count = db_session.query(DetectedEventModel).count()
    assert new_count == initial_count + 1


def test_no_event_creation_when_no_observed_transition(client, db_session):
    """
    Verify that steady-state noise or no-change steps do not create records in detected_events.
    """
    initial_count = db_session.query(DetectedEventModel).count()

    # 1. Steady state below noise floor (+2 W)
    noise_event = event_detector.detect_transition(
        prev_power_w=200.0,
        curr_power_w=202.0,
        timestamp=datetime.utcnow(),
    )
    assert noise_event.status == "NO_CHANGE"
    res = telemetry_service.persist_detected_event(db_session, noise_event)
    assert res is None
    assert db_session.query(DetectedEventModel).count() == initial_count

    # 2. Toggle appliance to its already existing state (no transition)
    res_api = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "ON"},
    )
    assert res_api.status_code == 200
    assert res_api.json()["status"] == "no_change"
    assert db_session.query(DetectedEventModel).count() == initial_count


def test_compatibility_with_existing_telemetry_history(client, db_session):
    """
    Verify that GET /api/v1/telemetry/history continues returning all existing fields
    (points, interval_minutes, count, data_source) along with the new persisted events list.
    """
    # Create an event
    client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "bulb_01", "target_state": "OFF"},
    )

    res = client.get("/api/v1/telemetry/history?minutes=60")
    assert res.status_code == 200
    data = res.json()

    # Standard existing fields must be present and valid
    assert "interval_minutes" in data
    assert "count" in data
    assert "points" in data
    assert "data_source" in data
    assert "is_simulated" in data
    assert isinstance(data["points"], list)

    # Extended events field must be present
    assert "events" in data
    assert isinstance(data["events"], list)
    assert len(data["events"]) >= 1

    bulb_events = [e for e in data["events"] if e.get("appliance_id") == "bulb_01"]
    assert len(bulb_events) == 1
    assert bulb_events[0]["status"] == "MATCHED"
    assert bulb_events[0]["delta_power_w"] == -12.0
    assert bulb_events[0]["data_classification"] == "RULE_BASED_ESTIMATE"


def test_repeated_polling_does_not_create_duplicate_history_events(client, db_session):
    """
    Priority 1 Regression Test: Repeated polling of /telemetry/live in steady state
    must not stamp duplicate event descriptions onto steady-state telemetry records
    or create duplicate detected event entries.
    """
    # 1. Check baseline event count
    init_events = client.get("/api/v1/telemetry/events?minutes=60").json()
    init_event_count = len(init_events)

    # 2. Poll live telemetry 15 times repeatedly (simulating frontend polling loop)
    for _ in range(15):
        poll_res = client.get("/api/v1/telemetry/live")
        assert poll_res.status_code == 200

    # 3. Verify that persistent detected events did NOT multiply
    after_events = client.get("/api/v1/telemetry/events?minutes=60").json()
    assert len(after_events) == init_event_count

    # 4. Verify history points do not have repeated duplicate appliance_event stamps
    hist_res = client.get("/api/v1/telemetry/history?minutes=60")
    assert hist_res.status_code == 200
    points = hist_res.json()["points"]
    # Telemetry samples created during steady-state polling must have appliance_event == None
    recent_points_with_event = [p for p in points[-15:] if p.get("appliance_event") is not None]
    assert len(recent_points_with_event) == 0


def test_empty_events_in_narrow_window_returns_truthful_empty_list(client, db_session):
    """
    Priority 1 Regression Test: When no events occurred within the requested window,
    /telemetry/events must return an empty list [], not fabricated events or errors.
    """
    # Query an interval where no events exist (e.g. 5 minutes when initial seed is 42m ago)
    res = client.get("/api/v1/telemetry/events?minutes=5")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    assert len(events) == 0


def test_distinct_transitions_with_matching_descriptions_have_unique_identities(client, db_session):
    """
    Priority 1 Regression Test: Multiple distinct toggles of the same appliance
    (e.g. Pump OFF, then Pump ON, then Pump OFF again) must each have unique stable IDs
    and distinct timestamps, never merged destructively.
    """
    # Toggle pump OFF
    res1 = client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "pump_01", "target_state": "OFF"})
    assert res1.status_code == 200

    # Toggle pump ON
    res2 = client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "pump_01", "target_state": "ON"})
    assert res2.status_code == 200

    # Toggle pump OFF again
    res3 = client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "pump_01", "target_state": "OFF"})
    assert res3.status_code == 200

    events = client.get("/api/v1/telemetry/events?minutes=60").json()
    pump_events = [e for e in events if e.get("appliance_id") == "pump_01"]

    # Must have seeded initial ON + OFF + ON + OFF = 4 events
    assert len(pump_events) >= 3
    ids = [e["id"] for e in pump_events]
    assert len(ids) == len(set(ids)), "Each event must possess a unique stable ID"


def test_exact_10_step_water_heater_persistence_verification(client, db_session):
    """
    P0 Verification: Verify durable event persistence end-to-end across the exact 10-step sequence:
    1. Record current simulator state and event count.
    2. Toggle Water Heater OFF.
    3. Confirm aggregate power falls from 284 W to 144 W under baseline assumptions.
    4. Confirm exactly one matching durable transition is stored.
    5. Refresh History (/api/v1/telemetry/history) and verify transition appears once with correct timestamp.
    6. Refresh browser/query API again (/api/v1/telemetry/events).
    7. Restart backend in controlled test environment (reset in-memory caches) and verify persisted event remains in SQLite.
    8. Toggle Water Heater ON and verify the next distinct event is recorded once.
    9. Confirm routine polling does not create extra events.
    10. Confirm transient simulator feed and durable archive are clearly distinguished.
    """
    # Step 1: Record current simulator state and event count
    state_res = client.get("/api/v1/simulator/state")
    assert state_res.status_code == 200
    initial_state = state_res.json()
    assert initial_state["aggregate_power_w"] == 284.0

    init_events = client.get("/api/v1/telemetry/events?minutes=60").json()
    initial_event_count = len(init_events)

    # Step 2: Toggle Water Heater OFF
    toggle_off_res = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "OFF"},
    )
    assert toggle_off_res.status_code == 200
    toggle_data = toggle_off_res.json()
    assert toggle_data["status"] == "success"
    assert toggle_data["delta_power_w"] == -140.0

    # Step 3: Confirm aggregate power falls from 284 W to 144 W under existing baseline assumptions
    post_off_state = client.get("/api/v1/simulator/state").json()
    assert post_off_state["aggregate_power_w"] == 144.0
    live_res = client.get("/api/v1/telemetry/live").json()
    assert live_res["active_power_w"] == 144.0

    # Step 4: Confirm exactly one matching durable transition is stored
    events_after_off = client.get("/api/v1/telemetry/events?minutes=60").json()
    assert len(events_after_off) == initial_event_count + 1
    heater_off_events = [e for e in events_after_off if e["appliance_id"] == "heater_01" and e["transition_type"] == "OFF"]
    assert len(heater_off_events) == 1
    h_off = heater_off_events[0]
    assert h_off["delta_power_w"] == -140.0
    assert h_off["status"] == "MATCHED"
    assert h_off["data_classification"] == "RULE_BASED_ESTIMATE"

    # Step 5: Refresh History and verify that the transition appears once with correct timestamp
    history_res = client.get("/api/v1/telemetry/history?minutes=60").json()
    history_events = history_res.get("events", [])
    history_heater_off = [e for e in history_events if e["appliance_id"] == "heater_01" and e["transition_type"] == "OFF"]
    assert len(history_heater_off) == 1
    assert history_heater_off[0]["id"] == h_off["id"]
    assert history_heater_off[0]["timestamp"] == h_off["timestamp"]

    # Step 6: Refresh browser and query the API again
    recheck_events = client.get("/api/v1/telemetry/events?minutes=60").json()
    assert len(recheck_events) == initial_event_count + 1
    assert [e["id"] for e in recheck_events] == [e["id"] for e in events_after_off]

    # Step 7: Restart the backend in a controlled test environment and verify persisted event remains available
    # Simulate restart: clear volatile in-memory event buffer while SQLite db_session remains persistent
    simulator.recent_events.clear()
    assert len(simulator.recent_events) == 0
    surviving_events = client.get("/api/v1/telemetry/events?minutes=60").json()
    surviving_heater_off = [e for e in surviving_events if e["appliance_id"] == "heater_01" and e["transition_type"] == "OFF"]
    assert len(surviving_heater_off) == 1
    assert surviving_heater_off[0]["id"] == h_off["id"]

    # Step 8: Toggle the Water Heater ON and verify next distinct event is recorded once
    toggle_on_res = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "ON"},
    )
    assert toggle_on_res.status_code == 200
    assert toggle_on_res.json()["delta_power_w"] == 140.0

    post_on_state = client.get("/api/v1/simulator/state").json()
    assert post_on_state["aggregate_power_w"] == 284.0

    events_after_on = client.get("/api/v1/telemetry/events?minutes=60").json()
    heater_on_events = [e for e in events_after_on if e["appliance_id"] == "heater_01" and e["transition_type"] == "ON"]
    assert len(heater_on_events) >= 1
    newest_event = events_after_on[0]
    assert newest_event["appliance_id"] == "heater_01"
    assert newest_event["transition_type"] == "ON"
    assert newest_event["delta_power_w"] == 140.0
    assert newest_event["id"] != h_off["id"]

    # Step 9: Confirm routine polling does not create extra events
    pre_poll_count = len(client.get("/api/v1/telemetry/events?minutes=60").json())
    for _ in range(10):
        p_res = client.get("/api/v1/telemetry/live")
        assert p_res.status_code == 200
    post_poll_count = len(client.get("/api/v1/telemetry/events?minutes=60").json())
    assert post_poll_count == pre_poll_count

    # Step 10: Confirm transient simulator feed and durable archive are clearly distinguished
    sim_feed = client.get("/api/v1/simulator/state").json()
    assert "recent_events" in sim_feed
    assert isinstance(sim_feed["recent_events"], list)

    durable_archive = client.get("/api/v1/telemetry/events?minutes=60").json()
    assert all("id" in e and "status" in e and "data_classification" in e for e in durable_archive)
    assert any(e["id"] == h_off["id"] for e in durable_archive)

