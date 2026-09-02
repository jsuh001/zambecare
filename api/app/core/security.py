import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    return password_hash.verify(password, encoded_hash)


def _create_token(subject: str, token_type: str, lifetime: timedelta, roles: list[str]) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type,
        "roles": roles,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, get_settings().secret_key, algorithm="HS256")


def create_access_token(subject: str, roles: list[str]) -> str:
    return _create_token(
        subject,
        "access",
        timedelta(minutes=get_settings().access_token_expire_minutes),
        roles,
    )


def create_refresh_token(subject: str, roles: list[str]) -> str:
    return _create_token(
        subject,
        "refresh",
        timedelta(days=get_settings().refresh_token_expire_days),
        roles,
    )


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        ) from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type.")
    return payload


def token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
