from datetime import datetime
from app.services.simulator import simulator

def test_simulator_snapshot_invariants():
    telemetry, disaggregation = simulator.get_current_snapshot()
    assert telemetry.active_power_w == 284.0
    assert disaggregation.aggregate_power_w == 284.0
    assert disaggregation.unattributed_power_w >= 0.0

    app_total = sum(a.estimated_power_w for a in disaggregation.appliances)
    assert round(disaggregation.aggregate_power_w, 1) == round(app_total + disaggregation.unattributed_power_w, 1)

def test_simulator_history_generation():
    points = simulator.generate_history(minutes=30)
    assert len(points) == 31  # 0 to 30 inclusive
    for pt in points:
        assert pt.active_power_w > 0
        assert pt.data_source == "SIMULATED"
