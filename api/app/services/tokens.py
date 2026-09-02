from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    token_fingerprint,
)
from app.models.identity import RefreshSession, UserAccount
from app.schemas.auth import TokenResponse


def issue_token_pair(db: Session, user: UserAccount) -> TokenResponse:
    access_token = create_access_token(str(user.user_id), user.roles)
    refresh_token = create_refresh_token(str(user.user_id), user.roles)
    db.add(
        RefreshSession(
            user_id=user.user_id,
            token_hash=token_fingerprint(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=get_settings().refresh_token_expire_days),
        )
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=get_settings().access_token_expire_minutes * 60,
    )


def active_refresh_session(db: Session, token: str) -> RefreshSession | None:
    return db.scalar(
        select(RefreshSession).where(
            RefreshSession.token_hash == token_fingerprint(token),
            RefreshSession.revoked_at.is_(None),
            RefreshSession.expires_at > datetime.now(UTC),
        )
    )
