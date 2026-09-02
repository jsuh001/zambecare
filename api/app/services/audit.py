from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


def record_audit(
    db: Session,
    *,
    actor_id: str,
    actor_role: str,
    action_name: str,
    resource_type: str,
    resource_id: str,
    outcome: str,
    request_id: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_id=actor_id,
            actor_role=actor_role,
            action_name=action_name,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            request_id=request_id or str(uuid4()),
        )
    )
