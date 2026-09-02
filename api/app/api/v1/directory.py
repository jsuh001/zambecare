from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db.session import get_db
from app.models.directory import Facility, Provider
from app.models.identity import UserAccount
from app.schemas.directory import (
    FacilityCreate,
    FacilityResponse,
    ProviderCreate,
    ProviderResponse,
)
from app.services.audit import record_audit

router = APIRouter(tags=["care directory"])


@router.get("/facilities", response_model=list[FacilityResponse])
def list_facilities(
    city: str | None = None,
    state: str | None = Query(default=None, min_length=2, max_length=50),
    facility_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[Facility]:
    query = select(Facility).where(Facility.is_active.is_(True))
    if city:
        query = query.where(Facility.city.ilike(f"%{city}%"))
    if state:
        query = query.where(Facility.state_code.ilike(f"%{state}%"))
    if facility_type:
        query = query.where(Facility.facility_type.ilike(f"%{facility_type}%"))
    return list(db.scalars(query.order_by(Facility.facility_name)).all())


@router.get("/providers", response_model=list[ProviderResponse])
def list_providers(
    specialty: str | None = None,
    facility_id: int | None = None,
    city: str | None = None,
    state: str | None = Query(default=None, min_length=2, max_length=50),
    accepting_patients: bool = True,
    db: Session = Depends(get_db),
) -> list[Provider]:
    query = select(Provider).where(Provider.is_accepting_patients == accepting_patients)
    if specialty:
        query = query.where(Provider.specialty_code.ilike(f"%{specialty}%"))
    if facility_id:
        query = query.where(Provider.facility_id == facility_id)
    if city or state:
        query = query.join(Facility, Provider.facility_id == Facility.facility_id)
        if city:
            query = query.where(Facility.city.ilike(f"%{city}%"))
        if state:
            query = query.where(Facility.state_code.ilike(f"%{state}%"))
    return list(db.scalars(query.order_by(Provider.last_name, Provider.first_name)).all())


@router.post("/facilities", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def create_facility(
    payload: FacilityCreate,
    user: UserAccount = Depends(require_roles("FACILITY_ADMIN", "SYSTEM_ADMIN")),
    db: Session = Depends(get_db),
) -> Facility:
    values = payload.model_dump()
    values["state_code"] = payload.state_code.upper()
    facility = Facility(**values)
    db.add(facility)
    db.flush()
    record_audit(
        db,
        actor_id=str(user.user_id),
        actor_role=",".join(user.roles),
        action_name="CREATE_FACILITY",
        resource_type="FACILITY",
        resource_id=str(facility.facility_id),
        outcome="SUCCESS",
    )
    db.commit()
    db.refresh(facility)
    return facility


@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(
    payload: ProviderCreate,
    user: UserAccount = Depends(require_roles("FACILITY_ADMIN", "SYSTEM_ADMIN")),
    db: Session = Depends(get_db),
) -> Provider:
    if payload.facility_id is not None and db.get(Facility, payload.facility_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found.")
    values = payload.model_dump()
    values["specialty_code"] = payload.specialty_code.upper()
    provider = Provider(**values)
    db.add(provider)
    db.flush()
    record_audit(
        db,
        actor_id=str(user.user_id),
        actor_role=",".join(user.roles),
        action_name="CREATE_PROVIDER",
        resource_type="PROVIDER",
        resource_id=str(provider.provider_id),
        outcome="SUCCESS",
    )
    db.commit()
    db.refresh(provider)
    return provider
