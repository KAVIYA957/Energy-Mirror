"""
appliances.py - Dynamic Appliance Registry Endpoints for Energy Mirror.

Provides REST API endpoints for querying, registering, updating, and managing
appliance definitions. Integrates directly with the database-backed ApplianceRegistry,
ensuring strict validation, detection honesty, and subsystem synchronization.

NOTE: In accordance with project security guidelines, while user authentication
is not yet implemented, administrative mutation endpoints (POST/PATCH/DELETE)
are intended for local administrative and developer configuration.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.appliance import (
    ApplianceDefinitionSchema,
    ApplianceCreateRequest,
    ApplianceUpdateRequest,
    ApplianceListResponse,
)
from app.services.appliance_registry import appliance_registry, PROTECTED_DEFAULT_IDS

router = APIRouter(prefix="/appliances", tags=["Appliance Registry"])


@router.get("", response_model=ApplianceListResponse)
def list_appliances(
    enabled_only: bool = Query(default=False, description="Filter for enabled appliances only"),
    db: Session = Depends(get_db),
):
    """
    List all appliance definitions currently stored in the registry.
    Can be filtered by enabled status.
    """
    appliances = appliance_registry.get_all(db, enabled_only=enabled_only)
    schemas = [ApplianceDefinitionSchema.model_validate(app) for app in appliances]
    return ApplianceListResponse(
        count=len(schemas),
        appliances=schemas,
        message=f"Retrieved {len(schemas)} appliance definitions.",
    )


@router.get("/{appliance_id}", response_model=ApplianceDefinitionSchema)
def get_appliance(appliance_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific appliance by its stable identifier."""
    record = appliance_registry.get_by_id(db, appliance_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appliance with ID '{appliance_id}' not found in registry.",
        )
    return ApplianceDefinitionSchema.model_validate(record)


@router.post("", response_model=ApplianceDefinitionSchema, status_code=status.HTTP_201_CREATED)
def register_appliance(request: ApplianceCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new appliance definition in the registry.

    Validation rules:
    - Stable appliance_id must be unique.
    - nominal_power_w must be positive and realistic (>0 W, <=25,000 W).
    - Claiming PRODUCTION_RULE_MATCHED requires providing a calibrated tolerance_w envelope.
    - Uncalibrated appliances default to UNSUPPORTED detection capability.
    """
    try:
        created = appliance_registry.register(db, request)
        return ApplianceDefinitionSchema.model_validate(created)
    except ValueError as exc:
        err_msg = str(exc)
        if "already exists" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=err_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_msg,
        )


@router.patch("/{appliance_id}", response_model=ApplianceDefinitionSchema)
def update_appliance(
    appliance_id: str,
    request: ApplianceUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update fields of an existing appliance definition and resync subsystems."""
    try:
        updated = appliance_registry.update(db, appliance_id, request)
        return ApplianceDefinitionSchema.model_validate(updated)
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


@router.delete("/{appliance_id}", status_code=status.HTTP_200_OK)
def delete_appliance(appliance_id: str, db: Session = Depends(get_db)):
    """
    Remove an appliance definition from the registry.
    Default baseline simulator appliances are protected and cannot be deleted.
    """
    try:
        appliance_registry.delete(db, appliance_id)
        return {
            "deleted": True,
            "appliance_id": appliance_id,
            "message": f"Appliance '{appliance_id}' successfully removed from registry.",
        }
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
