from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class TelemetryModel(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), index=True, default="esp32-sim-01")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    data_source = Column(String(32), default="SIMULATED", nullable=False)
    voltage_v = Column(Float, nullable=True)
    current_a = Column(Float, nullable=True)
    active_power_w = Column(Float, nullable=False)
    apparent_power_va = Column(Float, nullable=True)
    power_factor = Column(Float, nullable=True)
    frequency_hz = Column(Float, nullable=True)
    energy_kwh = Column(Float, nullable=True)
    is_simulated = Column(Boolean, default=True, nullable=False)
    unattributed_power_w = Column(Float, default=0.0, nullable=False)
    story_headline = Column(String(255), nullable=True)

    appliances = relationship("ApplianceEstimateModel", back_populates="telemetry", cascade="all, delete-orphan")


class ApplianceEstimateModel(Base):
    __tablename__ = "appliance_estimates"

    id = Column(Integer, primary_key=True, index=True)
    telemetry_id = Column(Integer, ForeignKey("telemetry_records.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    appliance_id = Column(String(64), index=True, nullable=False)
    name = Column(String(128), nullable=False)
    category = Column(String(64), default="general")
    status = Column(String(32), default="RUNNING")
    estimated_power_w = Column(Float, default=0.0, nullable=False)
    data_source = Column(String(32), default="NILM_ESTIMATED", nullable=False)
    confidence_score = Column(Float, nullable=True)
    evidence_notes = Column(Text, nullable=True)

    telemetry = relationship("TelemetryModel", back_populates="appliances")


class DetectedEventModel(Base):
    __tablename__ = "detected_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    status = Column(String(32), index=True, nullable=False)  # "MATCHED", "AMBIGUOUS"
    appliance_id = Column(String(64), nullable=True, index=True)
    appliance_name = Column(String(128), nullable=True)
    transition_type = Column(String(16), nullable=True)  # "ON", "OFF"
    delta_power_w = Column(Float, nullable=False)
    delta_pf = Column(Float, nullable=True)
    rule_description = Column(Text, nullable=False)
    data_classification = Column(String(64), default="RULE_BASED_ESTIMATE", nullable=False)
    event_fingerprint = Column(String(128), unique=True, index=True, nullable=True)


class ApplianceDefinitionModel(Base):
    __tablename__ = "appliance_definitions"

    id = Column(Integer, primary_key=True, index=True)
    appliance_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    category = Column(String(64), default="General", nullable=False)
    nominal_power_w = Column(Float, nullable=False)
    expected_pf = Column(Float, nullable=True)
    tolerance_w = Column(Float, nullable=True)
    pf_tolerance = Column(Float, nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_simulator_supported = Column(Boolean, default=True, nullable=False)
    detection_capability = Column(String(64), default="UNSUPPORTED", nullable=False)  # "PRODUCTION_RULE_MATCHED", "UNSUPPORTED", "EXPERIMENTAL_ONLY"
    confidence_score = Column(Float, nullable=True)
    evidence_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


