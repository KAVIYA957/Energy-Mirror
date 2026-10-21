"""
appliance_registry.py - Dynamic Appliance Registry Service for Energy Mirror.

Provides database-backed storage and management of appliance definitions,
replacing static 4-device hardcoding with a validated, extensible architecture:
- Stores stable IDs, display names, categories, and nominal ratings in Watts
- Tracks capability: PRODUCTION_RULE_MATCHED vs UNSUPPORTED vs EXPERIMENTAL_ONLY
- Safely seeds and preserves the default 4 simulator appliances
- Synchronizes dynamic changes to TelemetrySimulator and RuleBasedEventDetector
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import ApplianceDefinitionModel
from app.schemas.appliance import ApplianceCreateRequest, ApplianceUpdateRequest

DEFAULT_APPLIANCE_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "appliance_id": "heater_01",
        "name": "Water Heater",
        "category": "Heating",
        "nominal_power_w": 140.0,
        "expected_pf": 0.99,
        "tolerance_w": 12.0,
        "pf_tolerance": 0.06,
        "is_enabled": True,
        "is_simulator_supported": True,
        "detection_capability": "PRODUCTION_RULE_MATCHED",
        "confidence_score": 0.94,
        "evidence_notes": "Sharp +140W step with near-unity power factor (PF ~ 0.99), typical of resistive heating element.",
    },
    {
        "appliance_id": "pump_01",
        "name": "Water Pump",
        "category": "Motor",
        "nominal_power_w": 75.0,
        "expected_pf": 0.78,
        "tolerance_w": 9.0,
        "pf_tolerance": 0.12,
        "is_enabled": True,
        "is_simulator_supported": True,
        "detection_capability": "PRODUCTION_RULE_MATCHED",
        "confidence_score": 0.88,
        "evidence_notes": "Inductive motor signature (+75W, PF ~ 0.78 lagging) detected following inrush transient.",
    },
    {
        "appliance_id": "fan_01",
        "name": "Ceiling Fan",
        "category": "Motor",
        "nominal_power_w": 45.0,
        "expected_pf": 0.91,
        "tolerance_w": 7.0,
        "pf_tolerance": 0.09,
        "is_enabled": True,
        "is_simulator_supported": True,
        "detection_capability": "PRODUCTION_RULE_MATCHED",
        "confidence_score": 0.91,
        "evidence_notes": "Continuous steady rotation load of 45W with slight reactive component.",
    },
    {
        "appliance_id": "bulb_01",
        "name": "LED Bulb",
        "category": "Lighting",
        "nominal_power_w": 12.0,
        "expected_pf": 0.85,
        "tolerance_w": 4.0,
        "pf_tolerance": 0.18,
        "is_enabled": True,
        "is_simulator_supported": True,
        "detection_capability": "PRODUCTION_RULE_MATCHED",
        "confidence_score": 0.85,
        "evidence_notes": "Constant low-wattage step characteristic of high-efficiency switch-mode LED driver.",
    },
]

PROTECTED_DEFAULT_IDS = {"heater_01", "pump_01", "fan_01", "bulb_01"}


class ApplianceRegistry:
    """Manages CRUD and lifecycle of dynamic appliance definitions."""

    def seed_defaults(self, db: Session) -> List[ApplianceDefinitionModel]:
        """
        Safely seeds the default 4 simulator appliances if missing.
        Idempotent: preserves existing user-configured values and history.
        """
        seeded = []
        for defn in DEFAULT_APPLIANCE_DEFINITIONS:
            existing = db.query(ApplianceDefinitionModel).filter_by(appliance_id=defn["appliance_id"]).first()
            if not existing:
                model = ApplianceDefinitionModel(**defn)
                db.add(model)
                seeded.append(model)
        if seeded:
            db.commit()
            for m in seeded:
                db.refresh(m)
        return seeded

    def get_all(self, db: Session, enabled_only: bool = False) -> List[ApplianceDefinitionModel]:
        """Returns all appliance definitions from the SQLite registry."""
        query = db.query(ApplianceDefinitionModel)
        if enabled_only:
            query = query.filter(ApplianceDefinitionModel.is_enabled == True)
        return query.order_by(ApplianceDefinitionModel.id.asc()).all()

    def get_by_id(self, db: Session, appliance_id: str) -> Optional[ApplianceDefinitionModel]:
        """Retrieve single appliance definition by its stable appliance_id."""
        return db.query(ApplianceDefinitionModel).filter_by(appliance_id=appliance_id).first()

    def register(self, db: Session, data: ApplianceCreateRequest) -> ApplianceDefinitionModel:
        """
        Validates and registers a new appliance definition.
        Rejects duplicates and syncs simulator and detector subsystems.
        """
        existing = self.get_by_id(db, data.appliance_id)
        if existing:
            raise ValueError(f"Appliance with ID '{data.appliance_id}' already exists in the registry.")

        # If marked as PRODUCTION_RULE_MATCHED, tolerance envelope must be provided
        if data.detection_capability == "PRODUCTION_RULE_MATCHED":
            if data.tolerance_w is None or data.tolerance_w <= 0:
                raise ValueError("Appliance claimed as PRODUCTION_RULE_MATCHED must define a positive tolerance_w envelope.")

        record = ApplianceDefinitionModel(
            appliance_id=data.appliance_id,
            name=data.name,
            category=data.category,
            nominal_power_w=round(data.nominal_power_w, 2),
            expected_pf=round(data.expected_pf, 2) if data.expected_pf is not None else None,
            tolerance_w=round(data.tolerance_w, 2) if data.tolerance_w is not None else None,
            pf_tolerance=round(data.pf_tolerance, 2) if data.pf_tolerance is not None else None,
            is_enabled=data.is_enabled,
            is_simulator_supported=data.is_simulator_supported,
            detection_capability=data.detection_capability,
            evidence_notes=data.evidence_notes,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        self._sync_subsystems(db)
        return record

    def update(self, db: Session, appliance_id: str, data: ApplianceUpdateRequest) -> ApplianceDefinitionModel:
        """Updates fields of an existing appliance definition and resyncs subsystems."""
        record = self.get_by_id(db, appliance_id)
        if not record:
            raise KeyError(f"Appliance with ID '{appliance_id}' not found.")

        if data.name is not None:
            record.name = data.name
        if data.category is not None:
            record.category = data.category
        if data.nominal_power_w is not None:
            record.nominal_power_w = round(data.nominal_power_w, 2)
        if data.expected_pf is not None:
            record.expected_pf = round(data.expected_pf, 2)
        if data.tolerance_w is not None:
            record.tolerance_w = round(data.tolerance_w, 2)
        if data.pf_tolerance is not None:
            record.pf_tolerance = round(data.pf_tolerance, 2)
        if data.is_enabled is not None:
            record.is_enabled = data.is_enabled
        if data.is_simulator_supported is not None:
            record.is_simulator_supported = data.is_simulator_supported
        if data.detection_capability is not None:
            record.detection_capability = data.detection_capability
        if data.evidence_notes is not None:
            record.evidence_notes = data.evidence_notes

        db.commit()
        db.refresh(record)

        self._sync_subsystems(db)
        return record

    def delete(self, db: Session, appliance_id: str) -> bool:
        """
        Deletes a custom appliance definition.
        Disallows deletion of the 4 protected baseline appliances.
        """
        if appliance_id in PROTECTED_DEFAULT_IDS:
            raise ValueError(f"Cannot delete protected default simulator appliance '{appliance_id}'. You may disable it instead via is_enabled=False.")

        record = self.get_by_id(db, appliance_id)
        if not record:
            raise KeyError(f"Appliance with ID '{appliance_id}' not found.")

        db.delete(record)
        db.commit()

        self._sync_subsystems(db)
        return True

    def _sync_subsystems(self, db: Session):
        """Propagates updated appliance registry state to Simulator and Detector."""
        try:
            from app.services.simulator import simulator
            simulator.sync_from_registry(db)
        except Exception:
            pass

        try:
            from app.services.event_detector import event_detector
            event_detector.sync_from_registry(db)
        except Exception:
            pass


appliance_registry = ApplianceRegistry()
