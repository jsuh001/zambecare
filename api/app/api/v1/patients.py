from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db.session import get_db
from app.models.identity import UserAccount
from app.schemas.patient import PatientResponse, PatientUpdate
from app.services.audit import record_audit

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientResponse)
def get_my_profile(
    user: UserAccount = Depends(require_roles("PATIENT")), db: Session = Depends(get_db)
) -> PatientResponse:
    if user.patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    record_audit(
        db,
        actor_id=str(user.user_id),
        actor_role="PATIENT",
        action_name="READ_PROFILE",
        resource_type="PATIENT",
        resource_id=str(user.patient.patient_id),
        outcome="SUCCESS",
    )
    db.commit()
    return user.patient


@router.patch("/me", response_model=PatientResponse)
def update_my_profile(
    payload: PatientUpdate,
    user: UserAccount = Depends(require_roles("PATIENT")),
    db: Session = Depends(get_db),
) -> PatientResponse:
    patient = user.patient
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    record_audit(
        db,
        actor_id=str(user.user_id),
        actor_role="PATIENT",
        action_name="UPDATE_PROFILE",
        resource_type="PATIENT",
        resource_id=str(patient.patient_id),
        outcome="SUCCESS",
    )
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_my_profile(
    user: UserAccount = Depends(require_roles("PATIENT")), db: Session = Depends(get_db)
) -> None:
    if user.patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    user.patient.is_active = False
    user.account_status = "DEACTIVATED"
    record_audit(
        db,
        actor_id=str(user.user_id),
        actor_role="PATIENT",
        action_name="DEACTIVATE_PROFILE",
        resource_type="PATIENT",
        resource_id=str(user.patient.patient_id),
        outcome="SUCCESS",
    )
    db.commit()
