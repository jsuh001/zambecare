from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import decode_token, hash_password, verify_password
from app.db.session import get_db
from app.models.identity import Role, UserAccount, UserRole
from app.models.patient import Patient
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegistrationResponse,
    TokenResponse,
)
from app.services.audit import record_audit
from app.services.tokens import active_refresh_session, issue_token_pair

router = APIRouter(prefix="/auth", tags=["authentication"])
DUMMY_PASSWORD_HASH = hash_password("NotARealAccountPassword123!")


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegistrationResponse:
    email = payload.email.lower()
    if db.scalar(select(UserAccount).where(UserAccount.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account cannot be created.")

    role = db.scalar(select(Role).where(Role.role_name == "PATIENT"))
    if role is None:
        role = Role(role_name="PATIENT", description="Patient portal user")
        db.add(role)
        db.flush()

    user = UserAccount(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.user_id, role_id=role.role_id))
    patient = Patient(
        user_id=user.user_id,
        email=email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        sex_at_birth=payload.sex_at_birth,
        phone=payload.phone,
        state=payload.state,
        city=payload.city,
        postal_code=payload.postal_code,
        **({"country": payload.country} if payload.country else {}),
    )
    db.add(patient)
    try:
        db.flush()
        record_audit(
            db,
            actor_id=str(user.user_id),
            actor_role="PATIENT",
            action_name="REGISTER",
            resource_type="PATIENT",
            resource_id=str(patient.patient_id),
            outcome="SUCCESS",
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account cannot be created.") from exc
    db.refresh(user)
    db.refresh(patient)
    return RegistrationResponse(
        user_id=user.user_id,
        patient_id=patient.patient_id,
        email=user.email,
        roles=["PATIENT"],
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(UserAccount).where(UserAccount.email == payload.email.lower()))
    now = datetime.now(UTC)
    password_is_valid = verify_password(
        payload.password, user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    )
    if user is None or not password_is_valid:
        if user is not None:
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                user.locked_until = now + timedelta(minutes=15)
                user.failed_login_count = 0
        record_audit(
            db,
            actor_id=str(user.user_id) if user else "anonymous",
            actor_role="UNKNOWN",
            action_name="LOGIN",
            resource_type="USER_ACCOUNT",
            resource_id=str(user.user_id) if user else "unknown",
            outcome="DENIED",
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if user.account_status != "ACTIVE" or (user.locked_until and user.locked_until > now):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now
    tokens = issue_token_pair(db, user)
    record_audit(
        db,
        actor_id=str(user.user_id),
        actor_role=",".join(user.roles),
        action_name="LOGIN",
        resource_type="USER_ACCOUNT",
        resource_id=str(user.user_id),
        outcome="SUCCESS",
    )
    db.commit()
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_payload = decode_token(payload.refresh_token, "refresh")
    session = active_refresh_session(db, payload.refresh_token)
    if session is None or session.user_id != int(token_payload["sub"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session is invalid.")
    user = db.get(UserAccount, session.user_id)
    if user is None or user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is unavailable.")
    session.revoked_at = datetime.now(UTC)
    tokens = issue_token_pair(db, user)
    db.commit()
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> None:
    session = active_refresh_session(db, payload.refresh_token)
    if session is not None:
        session.revoked_at = datetime.now(UTC)
        db.commit()
