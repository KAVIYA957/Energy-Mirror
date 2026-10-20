from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.db.models import TelemetryModel, ApplianceEstimateModel, DetectedEventModel
from app.schemas.telemetry import (
    TelemetryResponse,
    DisaggregationResponse,
    ApplianceEstimateSchema,
    HistoryPoint,
    HistoryResponse,
    PersistedEventSchema,
)
from app.services.event_detector import DetectedEvent
from app.services.simulator import simulator

class TelemetryService:
    def get_live_telemetry(self, db: Session) -> TelemetryResponse:
        now = datetime.utcnow()
        telemetry, disaggregation = simulator.get_current_snapshot(now)

        # Persist the current telemetry record in SQLite
        db_record = TelemetryModel(
            device_id=telemetry.device_id,
            timestamp=telemetry.timestamp,
            data_source=telemetry.data_source,
            voltage_v=telemetry.voltage_v,
            current_a=telemetry.current_a,
            active_power_w=telemetry.active_power_w,
            apparent_power_va=telemetry.apparent_power_va,
            power_factor=telemetry.power_factor,
            frequency_hz=telemetry.frequency_hz,
            energy_kwh=telemetry.energy_kwh,
            is_simulated=telemetry.is_simulated,
            unattributed_power_w=telemetry.unattributed_power_w,
            story_headline=None,
        )
        db.add(db_record)
        db.flush()

        # Add appliance estimate records
        for app in disaggregation.appliances:
            app_record = ApplianceEstimateModel(
                telemetry_id=db_record.id,
                timestamp=app.timestamp,
                appliance_id=app.appliance_id,
                name=app.name,
                category=app.category,
                status=app.status,
                estimated_power_w=app.estimated_power_w,
                data_source=app.data_source,
                confidence_score=app.confidence_score,
                evidence_notes=app.evidence_notes,
            )
            db.add(app_record)

        db.commit()
        return telemetry

    def get_live_disaggregation(self, db: Session) -> DisaggregationResponse:
        now = datetime.utcnow()
        _, disaggregation = simulator.get_current_snapshot(now)
        return disaggregation

    def persist_detected_event(self, db: Session, event: DetectedEvent) -> Optional[DetectedEventModel]:
        """
        Durable persistence for rule-based detected events.
        Idempotent: prevents duplicate persistence upon repeated polling, toggle requests, or retries.
        """
        if event.status not in ("MATCHED", "AMBIGUOUS"):
            return None

        # Build idempotent fingerprint (to second precision)
        ts_sec = event.timestamp.replace(microsecond=0).isoformat()
        fingerprint = f"{ts_sec}_{round(event.delta_power_w, 1)}_{event.status}_{event.appliance_id or 'none'}"

        existing = db.query(DetectedEventModel).filter(DetectedEventModel.event_fingerprint == fingerprint).first()
        if existing:
            return existing

        # Check for near-simultaneous duplicate within 2-second window
        window_start = event.timestamp - timedelta(seconds=2)
        window_end = event.timestamp + timedelta(seconds=2)
        recent_dup = (
            db.query(DetectedEventModel)
            .filter(
                DetectedEventModel.timestamp >= window_start,
                DetectedEventModel.timestamp <= window_end,
                DetectedEventModel.status == event.status,
                DetectedEventModel.delta_power_w == round(event.delta_power_w, 1),
                DetectedEventModel.appliance_id == event.appliance_id,
            )
            .first()
        )
        if recent_dup:
            return recent_dup

        db_event = DetectedEventModel(
            timestamp=event.timestamp,
            status=event.status,
            appliance_id=event.appliance_id,
            appliance_name=event.appliance_name,
            transition_type=event.transition_type,
            delta_power_w=round(event.delta_power_w, 1),
            delta_pf=round(event.delta_pf, 2) if event.delta_pf is not None else None,
            rule_description=event.rule_description,
            data_classification=event.data_classification,
            event_fingerprint=fingerprint,
        )

        try:
            db.add(db_event)
            db.commit()
            db.refresh(db_event)
            return db_event
        except Exception:
            db.rollback()
            return db.query(DetectedEventModel).filter(DetectedEventModel.event_fingerprint == fingerprint).first()

    def get_persisted_events(self, db: Session, minutes: int = 60) -> List[DetectedEventModel]:
        """Query persisted detected events for the requested interval window."""
        minutes = max(5, min(minutes, 1440))
        since = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            db.query(DetectedEventModel)
            .filter(DetectedEventModel.timestamp >= since)
            .order_by(DetectedEventModel.timestamp.desc())
            .all()
        )

    def get_history(self, db: Session, minutes: int = 60) -> HistoryResponse:
        minutes = max(5, min(minutes, 1440))
        since = datetime.utcnow() - timedelta(minutes=minutes)

        # Retrieve records from SQLite
        records = (
            db.query(TelemetryModel)
            .filter(TelemetryModel.timestamp >= since)
            .order_by(TelemetryModel.timestamp.asc())
            .all()
        )

        persisted_events = self.get_persisted_events(db, minutes=minutes)
        event_schemas = [
            PersistedEventSchema(
                id=e.id,
                timestamp=e.timestamp,
                status=e.status,
                appliance_id=e.appliance_id,
                appliance_name=e.appliance_name,
                transition_type=e.transition_type,
                delta_power_w=e.delta_power_w,
                delta_pf=e.delta_pf,
                rule_description=e.rule_description,
                data_classification=e.data_classification,
            )
            for e in persisted_events
        ]

        # If database has insufficient history, generate deterministic history
        if len(records) < 5:
            simulated_points = simulator.generate_history(minutes=minutes)
            return HistoryResponse(
                interval_minutes=minutes,
                count=len(simulated_points),
                points=simulated_points,
                available_range_minutes=minutes,
                data_source="SIMULATED",
                is_simulated=True,
                events=event_schemas,
            )

        # Correlate actual detected events with telemetry points within a 2-second timestamp window
        # so chart markers only show on points where a discrete transition occurred!
        points: List[HistoryPoint] = []
        for r in records:
            matched_event_name = None
            for ev in persisted_events:
                if abs((ev.timestamp - r.timestamp).total_seconds()) <= 2.0:
                    matched_event_name = (
                        f"{ev.appliance_name} {ev.transition_type} ({ev.delta_power_w:+.0f} W)"
                        if ev.appliance_name
                        else f"{ev.status} Step ({ev.delta_power_w:+.0f} W)"
                    )
                    break

            points.append(
                HistoryPoint(
                    timestamp=r.timestamp,
                    active_power_w=r.active_power_w,
                    data_source=r.data_source,
                    appliance_event=matched_event_name,
                )
            )

        # Calculate actual available span from earliest to latest point
        if len(points) >= 2:
            span_seconds = max(0.0, (points[-1].timestamp - points[0].timestamp).total_seconds())
            actual_span_m = max(1, round(span_seconds / 60.0))
        else:
            actual_span_m = 1

        is_sim = any(p.data_source == "SIMULATED" for p in points)

        return HistoryResponse(
            interval_minutes=minutes,
            count=len(points),
            points=points,
            available_range_minutes=actual_span_m,
            data_source="SIMULATED" if is_sim else "LIVE",
            is_simulated=is_sim,
            events=event_schemas,
        )

    def seed_initial_history(self, db: Session):
        """Seed initial 60 minutes of historical readings and baseline event into SQLite if empty."""
        count = db.query(TelemetryModel).count()
        if count == 0:
            now = datetime.utcnow()
            history_points = simulator.generate_history(minutes=60, now=now)
            for pt in history_points:
                rec = TelemetryModel(
                    device_id="esp32-sim-01",
                    timestamp=pt.timestamp,
                    data_source="SIMULATED",
                    voltage_v=230.2,
                    current_a=round(pt.active_power_w / 230.2, 2),
                    active_power_w=pt.active_power_w,
                    apparent_power_va=round(pt.active_power_w / 0.94, 1),
                    power_factor=0.94,
                    frequency_hz=50.01,
                    energy_kwh=18.42,
                    is_simulated=True,
                    unattributed_power_w=12.0,
                    story_headline=pt.appliance_event,
                )
                db.add(rec)
            db.commit()

        # Seed initial detected event if detected_events is empty
        event_count = db.query(DetectedEventModel).count()
        if event_count == 0:
            initial_event = DetectedEvent(
                status="MATCHED",
                appliance_id="pump_01",
                appliance_name="Water Pump",
                transition_type="ON",
                delta_power_w=75.0,
                delta_pf=0.12,
                rule_description="Rule-based match: Water Pump ON (|Delta P| = 75.0 W matches nominal 75 W within [66, 84] W envelope).",
                timestamp=datetime.utcnow() - timedelta(minutes=42),
                data_classification="RULE_BASED_ESTIMATE",
            )
            self.persist_detected_event(db, initial_event)

telemetry_service = TelemetryService()

