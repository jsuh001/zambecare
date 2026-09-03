from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

SUPPORTED_ENTITIES = {
    "Patient", "Practitioner", "Facility", "Encounter", "Condition", "Observation"
}


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def checksum(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()


@dataclass(slots=True)
class PreparedRecord:
    entity: str
    source_system: str
    source_record_id: str
    raw: dict[str, Any]
    values: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def record_hash(self) -> str:
        return checksum(self.raw)

    @property
    def raw_json(self) -> str:
        return canonical_json(self.raw)


def parse_iso_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def decimal_or_none(value: Any) -> Decimal | None:
    return Decimal(str(value)) if value not in (None, "") else None
